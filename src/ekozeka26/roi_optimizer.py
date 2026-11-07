"""
WBS-4: Bütçe Kısıtlı Su Verimliliği Portföy (ROI / NPV) Optimizasyon Motoru (`roi_optimizer.py`)

Metodoloji & V&V Kuralları:
1. Ticari Platformlardan Tam Bağımsızlık: CarbonEmit veya başka bir ticari platforma bağımlılık yoktur;
   kendi açık şemamız (`data/schema/facility.schema.json`) ve SYGM NACE rehber profilleri kullanılır.
2. Çarpımsal Azalan Verim (Multiplicative Diminishing Returns):
   Aynı alt-prosese (`p ∈ {cooling, process, boiler, domestic}`) uygulanan önlemlerin tasarruf oranı
   asla doğrusal toplanmaz:
     S_p = 1 - prod_{i in M_p} (1 - r_i)
   Toplam tesis tasarruf oranı sektörel teknik üst sınırla (<= %78) kırpılır.
3. Kuyu Suyu vs Şebeke Suyu Ekonomisi:
   - İZSU Sanayi (1c) Şebeke: 403,79 TL/m³ (KDV hariç, Haziran 2026 tarifesi)
   - OSB Şebeke: 118,50 TL/m³
   - Kendi Yeraltı Kuyusu: Pompaj elektriği + bakım maliyeti düşüktür (24,80 TL/m³), ancak Gediz
     Havzası Sektörel Su Tahsis Planı'na göre kuraklıkta %62,9 tahsis kesintisi yaşandığı için
     beklenen üretim duruşu günleri ve günlük üretim kaybı zararı (`daily_downtime_cost_tl`) artar.
4. Kesin Kombinatoryal (0-1 Knapsack) Çözüm:
   Uygulanabilir önlemler (N <= 12, 2^12 = 4.096 kombinasyon) üzerinde çarpımsal azalan verim
   altında CAPEX bütçesini aşmadan 5 yıllık Net Bugünkü Değeri (NPV) maksimize eden kesin çözüm
   <5 ms içinde bulunur.
5. 27 Aralık 2029 Yeşil Su Verimliliği Belgesi (RG 27.12.2024, Sayı: 32765) kademe değerlendirmesi.
"""

from __future__ import annotations

import csv
import io
import json
from typing import Any

import numpy as np

from ekozeka26.data_pipeline import PROCESSED_DIR
from ekozeka26.risk_index import (
    _load_basins_df,
    _load_osb_profiles,
    compute_transparent_risk,
)

_MEASURES_CACHE: dict[str, Any] | None = None
_IZSU_CACHE: dict[str, Any] | None = None

PROCESS_KEYS = ("cooling", "process", "boiler", "domestic")
PROCESS_LABELS_TR = {
    "cooling": "Soğutma Kulesi & Isı Değiştirici",
    "process": "Yıkama, Boyama & Ürün Prosesi",
    "boiler": "Kazan Besleme & Buhar",
    "domestic": "Evsel, Saha & Kaçak Kontrolü",
}


def _load_measures_catalog() -> dict[str, Any]:
    global _MEASURES_CACHE
    if _MEASURES_CACHE is None:
        _MEASURES_CACHE = json.loads((PROCESSED_DIR / "measures_catalog.json").read_text(encoding="utf-8"))
    return _MEASURES_CACHE


def _load_izsu_snapshot() -> dict[str, Any]:
    global _IZSU_CACHE
    if _IZSU_CACHE is None:
        _IZSU_CACHE = json.loads((PROCESSED_DIR / "izsu_snapshot.json").read_text(encoding="utf-8"))
    return _IZSU_CACHE


def normalize_process_shares(shares: dict[str, float] | None, sector: str = "textile") -> dict[str, float]:
    """
    Edge-Case #6: Proses yüzdeleri toplamı 100 değilse veya eksikse sektörel varsayılanla
    tamamlar ve toplamı 100.0 olacak şekilde normalize eder.
    """
    osb_meta = _load_osb_profiles()
    defaults = osb_meta.get("sector_defaults", {}).get(
        sector, {"cooling": 35.0, "process": 40.0, "boiler": 15.0, "domestic": 10.0}
    )
    if not shares:
        return {k: float(defaults[k]) for k in PROCESS_KEYS}

    raw = {k: max(0.0, float(shares.get(k, defaults.get(k, 25.0)))) for k in PROCESS_KEYS}
    total = sum(raw.values())
    if total <= 1e-6:
        return {k: float(defaults[k]) for k in PROCESS_KEYS}

    normed = {k: round(100.0 * raw[k] / total, 2) for k in PROCESS_KEYS}
    # Yuvarlama farkını en büyük prosese ekle ki toplam tam 100.00 olsun
    diff = round(100.0 - sum(normed.values()), 2)
    max_k = max(PROCESS_KEYS, key=lambda k: normed[k])
    normed[max_k] = round(normed[max_k] + diff, 2)
    return normed


def compute_multiplicative_savings(
    selected_measures: list[dict[str, Any]],
    process_shares_pct: dict[str, float],
    max_sectoral_cap: float = 0.78,
) -> dict[str, Any]:
    """
    Aynı alt-prosese (`p ∈ {cooling, process, boiler, domestic}`) uygulanan önlemlerin
    çarpımsal azalan verim formülüyle (`S_p = 1 - prod(1 - r_i)`) net tasarruf oranını
    hesaplar ve sektörel teknik üst sınırla (`<= 0.78`) kırpar.
    """
    process_rates: dict[str, float] = {}
    for p in PROCESS_KEYS:
        rates_p = [
            float(m["process_saving_rate"])
            for m in selected_measures
            if m.get("target_process") == p
        ]
        if not rates_p:
            process_rates[p] = 0.0
        else:
            rem = 1.0
            for r in rates_p:
                rem *= 1.0 - np.clip(r, 0.0, 0.95)
            process_rates[p] = float(np.clip(1.0 - rem, 0.0, 0.88))

    weighted_sum = sum((process_shares_pct[p] / 100.0) * process_rates[p] for p in PROCESS_KEYS)
    capped_total_rate = float(min(max_sectoral_cap, weighted_sum))

    return {
        "process_saving_rates": {k: round(v, 4) for k, v in process_rates.items()},
        "uncapped_total_saving_rate": round(float(weighted_sum), 4),
        "total_saving_rate": round(capped_total_rate, 4),
        "total_saving_pct": round(100.0 * capped_total_rate, 2),
        "was_capped_at_sectoral_limit": bool(weighted_sum > max_sectoral_cap),
    }


def resolve_water_tariff_and_cutback_factor(
    water_source: str,
    grid_share_pct: float = 100.0,
    osb_info: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Su kaynağına (`izsu_grid`, `osb_grid`, `groundwater_well`, `hybrid`) ve seçilen
    bölgeye göre m³ birim maliyeti (TL/m³), veri gerçeklik etiketini (`provenance`)
    ve kuraklıkta tahsis kesintisi çarpanını döner.
    """
    tariffs = _load_izsu_snapshot()["tariffs_2026"]
    izsu_tl = float(tariffs["tier_21_plus_tl_m3"])  # 403.79 TL/m³ (Resmi İZSU 1c)
    default_osb_tl = float(tariffs["osb_typical_grid_tl_m3"])  # 118.50 TL/m³
    well_tl = float(tariffs["groundwater_well_pumping_tl_m3"])  # 24.80 TL/m³

    osb_tl = float(osb_info.get("osb_grid_tariff_tl_m3", default_osb_tl)) if osb_info else default_osb_tl
    osb_prov = (
        str(osb_info.get("tariff_provenance", "Kalibre Varsayım (BOSB Referanslı)"))
        if osb_info
        else "Kalibre Varsayım (OSB Referans Tarifesi)"
    )
    osb_note = (
        str(
            osb_info.get(
                "tariff_source_note",
                "OSB merkezi su/atıksu altyapısı; kuraklıkta kademeli kota kesintisine tabidir.",
            )
        )
        if osb_info
        else "OSB merkezi su/atıksu altyapısı; kuraklıkta kademeli kota kesintisine tabidir."
    )

    src = str(water_source).lower()
    if src == "izsu_grid":
        return {
            "water_source": "izsu_grid",
            "source_label": f"İZSU Sanayi (1c) Belediye Şebekesi ({izsu_tl:.2f} TL/m³)",
            "unit_cost_tl_m3": izsu_tl,
            "cutback_vulnerability_multiplier": 0.72,
            "provenance": "Ölçülmüş (İZSU Haziran 2026 Resmi Sanayi 1c Tarifesi)",
            "allocation_note": "Resmi İZSU 1c (21 m³+ su 269,20 + atıksu 134,59 = 403,79 TL/m³); şebeke çeşitliliği sayesinde kesinti çarpanı düşüktür (0,72×).",
        }
    if src == "osb_grid":
        return {
            "water_source": "osb_grid",
            "source_label": f"OSB Merkezi Şebeke Suyu ({osb_tl:.2f} TL/m³)",
            "unit_cost_tl_m3": osb_tl,
            "cutback_vulnerability_multiplier": 1.00,
            "provenance": osb_prov,
            "allocation_note": osb_note,
        }
    if src == "groundwater_well":
        return {
            "water_source": "groundwater_well",
            "source_label": f"Kendi Yeraltı Kuyusu ({well_tl:.2f} TL/m³ pompaj + yüksek tahsis kısıtı riski)",
            "unit_cost_tl_m3": well_tl,
            "cutback_vulnerability_multiplier": 1.38,
            "provenance": "Kalibre Varsayım (Kuyu Pompaj Enerjisi) + Resmi Plan (SYGM %62,9 Kısıt)",
            "allocation_note": (
                "Kuyu pompaj/enerji maliyeti düşüktür (24,80 TL/m³) ancak SYGM Gediz Tahsis Planı'na göre "
                "kuraklıkta sanayi tahsisi %85,9'dan %37,1'e düşer (%62,9 kesinti -> 1,38× üretim duruşu çarpanı)."
            ),
        }

    # hybrid (Karma: OSB/Şehir Şebekesi + Yeraltı Kuyusu)
    g_ratio = float(np.clip(grid_share_pct, 0.0, 100.0)) / 100.0
    grid_ref_tl = osb_tl if osb_info else izsu_tl
    unit_tl = round(g_ratio * grid_ref_tl + (1.0 - g_ratio) * well_tl, 2)
    mult = round(g_ratio * 0.90 + (1.0 - g_ratio) * 1.38, 2)
    return {
        "water_source": "hybrid",
        "source_label": f"Karma Kaynak (%{g_ratio*100:.0f} Şebeke + %{(1-g_ratio)*100:.0f} Kuyu — Ort. {unit_tl:.2f} TL/m³)",
        "unit_cost_tl_m3": unit_tl,
        "cutback_vulnerability_multiplier": mult,
        "provenance": f"Karma ({osb_prov} + Kuyu Pompaj Varsayımı)",
        "allocation_note": f"%{g_ratio*100:.0f} şebeke ({grid_ref_tl:.2f} TL/m³) ve %{(1-g_ratio)*100:.0f} yeraltı kuyusu (24,80 TL/m³) ağırlıklı ortalamasıdır.",
    }


def evaluate_2029_certificate_tier(
    saving_pct: float,
    selected_measure_ids: list[str],
    employee_count: int = 250,
) -> dict[str, Any]:
    """
    27.12.2024 tarihli ve 32765 sayılı Resmi Gazete'de yayımlanan Su Verimliliği Yönetmeliği
    (Madde 7, Ek-1/Ek-2) çerçevesinde **kriter tabanlı** ön değerlendirme yapar:
      - Mavi Belge: Su verimliliği sisteminin kurulması, ölçüm/kayıt altyapısı (M02 veya temel önlem).
      - Yeşil Belge (5 yıl içinde zorunlu): Mavi Belge + sektörel verimlilik teknikleri (MET) +
        geri kazanım / alternatif su kaynağı (gri su, yağmur suyu, kondens, kaskad, RO).
      - Turkuaz Belge (Gönüllü üst seviye): İleri döngüsel su geri kazanımı ve çoklu proses entegrasyonu.
    Not: Yönetmelikte sabit yüzde eşik bulunmaz; yüzde değerler teknik yeterlilik göstergesidir.
    """
    has_metering = "M02" in selected_measure_ids or len(selected_measure_ids) >= 2
    has_process_efficiency = any(mid in selected_measure_ids for mid in ("M01", "M03", "M05", "M06", "M07", "M11", "M12"))
    has_reuse = any(mid in selected_measure_ids for mid in ("M03", "M04", "M05", "M06", "M08", "M09", "M10"))
    has_advanced_circular = any(mid in selected_measure_ids for mid in ("M05", "M08", "M09", "M11")) and len(selected_measure_ids) >= 4

    criteria_checklist = [
        {
            "criterion_id": "C1_METERING",
            "title": "1. Su Ölçüm, Alt-Sayaç ve Kayıt Sistemi (Mavi Belge Temeli)",
            "met": bool(has_metering or len(selected_measure_ids) >= 1),
            "detail": "ISO 46001 dijital alt-sayaç ağı (M02) veya kayıtlı hat izleme sistemi",
        },
        {
            "criterion_id": "C2_BAT_TECHNIQUES",
            "title": "2. Sektörel Su Verimliliği Teknikleri — SYGM NACE MET (Yeşil Belge)",
            "met": bool(has_process_efficiency and saving_pct >= 12.0),
            "detail": "Proses, soğutma veya kazan hatlarında en iyi mevcut tekniklerin (MET) uygulanması",
        },
        {
            "criterion_id": "C3_REUSE_ALT_SOURCE",
            "title": "3. Geri Kazanım & Alternatif Su Kaynağı Kullanımı (Yeşil Belge)",
            "met": bool(has_reuse and saving_pct >= 15.0),
            "detail": "Kaskad durulama, buhar kondensi, kapalı devre soğutma, yağmur/gri su veya RO geri kazanımı",
        },
        {
            "criterion_id": "C4_VOLUNTARY_LEADERSHIP",
            "title": "4. İleri Su Döngüselliği & Çoklu Proses Entegrasyonu (Turkuaz Gönüllü)",
            "met": bool(has_advanced_circular and has_reuse and saving_pct >= 30.0),
            "detail": "En az 4 entegre önlem + ileri arıtma/kapalı devre dönüşümü ile üst düzey su döngüselliği",
        },
    ]

    if has_advanced_circular and has_metering and has_reuse and saving_pct >= 30.0:
        tier = "Turkuaz Su Verimliliği Belgesi"
        status = "ÜSTÜN UYUM — Gönüllü En Üst Kademe (Yeşil Zorunluluğu + İleri Döngüsellik Sağlandı)"
        compliant_2029 = True
        color_badge = "cyan"
    elif has_metering and (has_reuse or has_process_efficiency) and saving_pct >= 15.0:
        tier = "Yeşil Su Verimliliği Belgesi"
        status = "TAM UYUM (Mavi Belge + MET & Geri Kazanım Kriterleri Sağlandı — 2029 Zorunluluğu Karşılandı)"
        compliant_2029 = True
        color_badge = "emerald"
    elif len(selected_measure_ids) >= 1 and saving_pct >= 5.0:
        tier = "Mavi Su Verimliliği Belgesi"
        status = "BAŞLANGIÇ UYUMU (Sistem Kurulumu / Mavi Seviye — 5 Yıl İçinde Yeşil Belge İçin Ek Geri Kazanım Gerekir)"
        compliant_2029 = False
        color_badge = "blue"
    else:
        tier = "Belge Alınamaz (Uyumsuz)"
        status = "KRİTİK UYUMSUZLUK (Ölçüm ve Verimlilik Kriterleri Sağlanmadı)"
        compliant_2029 = False
        color_badge = "red"

    gap_to_green_pct = round(max(0.0, 15.0 - saving_pct), 2)
    return {
        "regulation": "Su Verimliliği Yönetmeliği (RG 27.12.2024, No. 32765 — Madde 7 & Ek-2)",
        "evaluation_type": "Kriter Tabanlı Ön Değerlendirme (Resmi Bakanlık Denetimi Değildir)",
        "provenance": "Regülasyon Kriter Eşlemesi + SYGM NACE MET Referansları",
        "mandatory_deadline": "2029-12-27",
        "is_mandatory_for_facility": employee_count >= 50,
        "achieved_tier": tier,
        "compliance_status": status,
        "compliant_with_2029_green_mandate": compliant_2029,
        "achieved_saving_pct": round(saving_pct, 2),
        "green_threshold_pct": 15.0,
        "turquoise_threshold_pct": 30.0,
        "remaining_gap_to_green_pct": gap_to_green_pct,
        "badge_color": color_badge,
        "criteria_checklist": criteria_checklist,
    }


def optimize_facility_roi(
    osb_id: str = "izmir_kemalpasa",
    sector: str = "textile",
    annual_water_m3: float = 150000.0,
    water_source: str = "izsu_grid",
    grid_share_pct: float = 100.0,
    process_shares: dict[str, float] | None = None,
    daily_downtime_cost_tl: float = 750000.0,
    capex_budget_tl: float = 3500000.0,
    target_year: int | str = 2030,
    scenario: str = "BAU",
    employee_count: int = 250,
    facility_name: str = "Örnek Sanayi Tesisi",
    discount_rate: float = 0.18,
    string_id: str | None = None,
) -> dict[str, Any]:
    """
    Girilen fabrika parametreleri ve CAPEX bütçe kısıtı altında:
    1. "Hiçbir Şey Yapmama" (Do-Nothing) 2030/2050 su faturası ve üretim duruşu zararını (P10/P50/P90),
    2. Çarpımsal azalan verim kuralıyla 5 yıllık NPV'yi maksimize eden 0-1 Knapsack optimum önlem portföyünü,
    3. 5 yıllık kümülatif nakit akışı ve geri ödeme (payback) süresini,
    4. 27.12.2029 Yeşil Su Verimliliği Belgesi kriter tabanlı uyum kademesini hesaplar.
    """
    if annual_water_m3 <= 0:
        raise ValueError("Yıllık su tüketimi (annual_water_m3) 0'dan büyük olmalıdır.")
    if capex_budget_tl < 0:
        raise ValueError("Yatırım bütçesi (capex_budget_tl) negatif olamaz.")
    if daily_downtime_cost_tl < 0:
        raise ValueError("Günlük üretim durma maliyeti negatif olamaz.")

    osb_meta = _load_osb_profiles()
    catalog_meta = _load_measures_catalog()
    df_basins = _load_basins_df().set_index("string_id")

    all_osbs = {o["osb_id"]: o for o in osb_meta["osbs"]}
    osb_info = all_osbs.get(osb_id, osb_meta["osbs"][0])
    is_custom_basin = bool(string_id and string_id in df_basins.index and string_id != osb_info["string_id"])
    if is_custom_basin and string_id is not None:
        sid = string_id
        basin_row = df_basins.loc[sid].to_dict()
        basin_row["string_id"] = sid
        gw_dep_input: float | None = None
    else:
        sid = osb_info["string_id"]
        if sid in df_basins.index:
            basin_row = df_basins.loc[sid].to_dict()
            # set_index("string_id") sonrası to_dict() indeksi düşürür; kimliği geri ekle.
            basin_row["string_id"] = sid
        else:
            basin_row = osb_info
        gw_dep_input = float(osb_info["groundwater_dependency_pct"])

    sec_key = sector if sector in osb_meta["sector_defaults"] else "general"
    norm_shares = normalize_process_shares(process_shares, sector=sec_key)
    max_cap = min(
        float(catalog_meta.get("max_sectoral_saving_cap", 0.78)),
        float(osb_meta["sector_defaults"][sec_key].get("max_tech_saving_pct", 78.0)) / 100.0,
    )

    # Konumun şeffaf risk ve kesinti günü hesabı
    risk_eval = compute_transparent_risk(
        basin_row=basin_row,
        sector=sec_key,
        year=target_year,
        scenario=scenario,
        groundwater_dependency_pct=gw_dep_input,
    )

    source_info = resolve_water_tariff_and_cutback_factor(water_source, grid_share_pct, osb_info=osb_info)
    unit_tl = float(source_info["unit_cost_tl_m3"])
    vuln_mult = float(source_info["cutback_vulnerability_multiplier"])

    # Do-Nothing (Hiçbir Şey Yapmama) yıllık maliyetleri
    annual_water_bill_tl = round(annual_water_m3 * unit_tl, 0)
    raw_days = risk_eval["expected_cutback_days"]
    eff_days_p10 = round(raw_days["p10"] * vuln_mult, 1)
    eff_days_p50 = round(raw_days["p50"] * vuln_mult, 1)
    eff_days_p90 = round(raw_days["p90"] * vuln_mult, 1)

    downtime_loss_p10_tl = round(eff_days_p10 * daily_downtime_cost_tl, 0)
    downtime_loss_p50_tl = round(eff_days_p50 * daily_downtime_cost_tl, 0)
    downtime_loss_p90_tl = round(eff_days_p90 * daily_downtime_cost_tl, 0)

    do_nothing_total_p10_tl = annual_water_bill_tl + downtime_loss_p10_tl
    do_nothing_total_p50_tl = annual_water_bill_tl + downtime_loss_p50_tl
    do_nothing_total_p90_tl = annual_water_bill_tl + downtime_loss_p90_tl

    # Sektöre uygun aday önlemleri filtrele
    candidate_measures = [
        m
        for m in catalog_meta["measures"]
        if "all" in m["applicable_sectors"] or sec_key in m["applicable_sectors"]
    ]
    n_cand = len(candidate_measures)

    # 5 yıllık NPV çarpanı: sum_{t=1..5} 1 / (1 + discount_rate)^t
    pv_annuity_factor = sum(1.0 / ((1.0 + discount_rate) ** t) for t in range(1, 6))

    # 0-1 Knapsack (2^N kombinasyon üzerinde çarpımsal azalan verimli tam arama)
    best_npv = -1e18
    best_mask = 0
    best_eval: dict[str, Any] | None = None

    for mask in range(1 << n_cand):
        chosen = [candidate_measures[i] for i in range(n_cand) if (mask & (1 << i))]
        total_capex = sum(float(m["capex_tl"]) for m in chosen)
        if total_capex > capex_budget_tl:
            continue

        sav_info = compute_multiplicative_savings(chosen, norm_shares, max_sectoral_cap=max_cap)
        sav_rate = float(sav_info["total_saving_rate"])
        saved_m3 = annual_water_m3 * sav_rate
        water_bill_saving_tl = saved_m3 * unit_tl

        # Su tasarrufu ve geri kazanım döngüsü, kuraklık kesintisi (üretim duruşu) günlerini azaltır
        resilience_reduction_ratio = min(0.85, 1.15 * sav_rate)
        avoided_downtime_days_p50 = eff_days_p50 * resilience_reduction_ratio
        avoided_downtime_tl = avoided_downtime_days_p50 * daily_downtime_cost_tl

        annual_opex_delta_tl = sum(float(m["annual_opex_change_tl"]) for m in chosen)
        net_annual_benefit_tl = water_bill_saving_tl + avoided_downtime_tl - annual_opex_delta_tl
        npv_5yr = net_annual_benefit_tl * pv_annuity_factor - total_capex

        if npv_5yr > best_npv:
            best_npv = npv_5yr
            best_mask = mask
            best_eval = {
                "chosen": chosen,
                "total_capex_tl": total_capex,
                "sav_info": sav_info,
                "saved_m3": saved_m3,
                "water_bill_saving_tl": water_bill_saving_tl,
                "avoided_downtime_days_p50": avoided_downtime_days_p50,
                "avoided_downtime_tl": avoided_downtime_tl,
                "annual_opex_delta_tl": annual_opex_delta_tl,
                "net_annual_benefit_tl": net_annual_benefit_tl,
                "npv_5yr_tl": npv_5yr,
            }

    assert best_eval is not None
    chosen_list = best_eval["chosen"]
    selected_ids = [m["measure_id"] for m in chosen_list]

    # Seçilen her önlemin tekil ve marjinal tablosunu oluştur
    portfolio_rows: list[dict[str, Any]] = []
    for m in chosen_list:
        p_key = m["target_process"]
        p_share = norm_shares[p_key] / 100.0
        standalone_m3 = annual_water_m3 * p_share * float(m["process_saving_rate"])
        standalone_tl = (
            standalone_m3 * unit_tl
            + (eff_days_p50 * min(0.85, 1.15 * p_share * float(m["process_saving_rate"])) * daily_downtime_cost_tl)
            - float(m["annual_opex_change_tl"])
        )
        payback_m = (
            round(12.0 * float(m["capex_tl"]) / max(standalone_tl, 1.0), 1)
            if standalone_tl > 0
            else 99.0
        )
        portfolio_rows.append(
            {
                "measure_id": m["measure_id"],
                "name": m["name"],
                "target_process": p_key,
                "target_process_label": PROCESS_LABELS_TR.get(p_key, p_key),
                "process_saving_rate_pct": round(100.0 * float(m["process_saving_rate"]), 1),
                "capex_tl": round(float(m["capex_tl"]), 0),
                "annual_opex_change_tl": round(float(m["annual_opex_change_tl"]), 0),
                "standalone_saved_m3": round(standalone_m3, 0),
                "estimated_payback_months": min(payback_m, 60.0),
                "nace_reference": m["nace_reference"],
                "description": m["description"],
            }
        )

    total_capex_tl = round(float(best_eval["total_capex_tl"]), 0)
    net_annual_benefit_tl = round(float(best_eval["net_annual_benefit_tl"]), 0)
    saved_m3 = round(float(best_eval["saved_m3"]), 0)
    saving_pct = float(best_eval["sav_info"]["total_saving_pct"])

    if total_capex_tl > 0 and net_annual_benefit_tl > 0:
        payback_years = round(total_capex_tl / net_annual_benefit_tl, 2)
        payback_months = round(12.0 * total_capex_tl / net_annual_benefit_tl, 1)
        roi_5yr_pct = round(100.0 * (5.0 * net_annual_benefit_tl - total_capex_tl) / total_capex_tl, 1)
    else:
        payback_years = 0.0
        payback_months = 0.0
        roi_5yr_pct = 0.0

    # 5 Yıllık Kümülatif Nakit Akışı Serisi (Yıl 0 .. Yıl 5)
    cashflow_years = [0, 1, 2, 3, 4, 5]
    cumulative_net_cashflow_tl = [
        round(-total_capex_tl + yr * net_annual_benefit_tl, 0) for yr in cashflow_years
    ]
    cumulative_do_nothing_loss_tl = [
        round(-yr * do_nothing_total_p50_tl, 0) for yr in cashflow_years
    ]

    # Edge-case #6: Çok düşük bütçe uyarısı (<280.000 TL)
    min_measure_cost = min(float(m["capex_tl"]) for m in candidate_measures)
    low_budget_advisory = None
    if capex_budget_tl < min_measure_cost:
        low_budget_advisory = (
            f"Girilen yatırım bütçesi ({capex_budget_tl:,.0f} TL), katalogdaki en düşük donanım yatırımı "
            f"olan {min_measure_cost:,.0f} TL'nin altındadır. Bu bütçeyle yalnızca sıfır/düşük maliyetli "
            f"işletme önlemleri (valf/hortum disiplini, gece hat basınç düşürme ve manuel kaçak taraması, "
            f"tahmini %2–4 tasarruf) uygulanabilir. 2029 Yeşil Belge uyumu için en az 620.000 TL bütçe önerilir."
        )

    cert_2029 = evaluate_2029_certificate_tier(
        saving_pct=saving_pct,
        selected_measure_ids=selected_ids,
        employee_count=employee_count,
    )

    return {
        "facility_summary": {
            "facility_name": facility_name,
            "location_type": "custom_basin" if is_custom_basin else "osb",
            "osb_id": osb_info["osb_id"],
            "osb_name": (
                f"{risk_eval['province_name']} Alt-Havzası (#{risk_eval['pfaf_id']} · Münferit Sanayi Parseli)"
                if is_custom_basin
                else osb_info["name"]
            ),
            "city": risk_eval["province_name"] if is_custom_basin else osb_info["city"],
            "pfaf_id": risk_eval["pfaf_id"],
            "string_id": sid,
            "sector": sec_key,
            "sector_label": risk_eval["sector_label"],
            "employee_count": employee_count,
            "annual_water_m3": round(annual_water_m3, 0),
            "process_shares_pct": norm_shares,
            "daily_downtime_cost_tl": round(daily_downtime_cost_tl, 0),
            "capex_budget_tl": round(capex_budget_tl, 0),
            "target_year": target_year,
            "scenario": scenario.upper(),
        },
        "water_source_economics": source_info,
        "location_risk": risk_eval,
        "do_nothing_projection": {
            "annual_water_bill_tl": annual_water_bill_tl,
            "expected_cutback_days": {
                "p10": eff_days_p10,
                "p50": eff_days_p50,
                "p90": eff_days_p90,
            },
            "expected_downtime_loss_tl": {
                "p10": downtime_loss_p10_tl,
                "p50": downtime_loss_p50_tl,
                "p90": downtime_loss_p90_tl,
            },
            "total_annual_exposure_tl": {
                "p10": do_nothing_total_p10_tl,
                "p50": do_nothing_total_p50_tl,
                "p90": do_nothing_total_p90_tl,
            },
            "five_year_unmitigated_exposure_p50_tl": round(5.0 * do_nothing_total_p50_tl, 0),
        },
        "optimized_portfolio": {
            "solver_method": f"0-1 Knapsack Kesin Çözüm ({1 << n_cand} kombinasyon, çarpımsal azalan verim)",
            "selected_measures_count": len(portfolio_rows),
            "selected_measures": portfolio_rows,
            "total_capex_tl": total_capex_tl,
            "budget_utilization_pct": round(100.0 * total_capex_tl / max(capex_budget_tl, 1.0), 1)
            if capex_budget_tl > 0
            else 0.0,
            "remaining_budget_tl": round(max(0.0, capex_budget_tl - total_capex_tl), 0),
            "multiplicative_savings_breakdown": best_eval["sav_info"],
            "annual_water_saved_m3": saved_m3,
            "post_investment_water_demand_m3": round(annual_water_m3 - saved_m3, 0),
            "annual_water_bill_saving_tl": round(float(best_eval["water_bill_saving_tl"]), 0),
            "avoided_cutback_days_p50": round(float(best_eval["avoided_downtime_days_p50"]), 1),
            "avoided_downtime_loss_p50_tl": round(float(best_eval["avoided_downtime_tl"]), 0),
            "annual_opex_change_tl": round(float(best_eval["annual_opex_delta_tl"]), 0),
            "net_annual_financial_benefit_tl": net_annual_benefit_tl,
            "npv_5yr_tl": round(float(best_eval["npv_5yr_tl"]), 0),
            "roi_5yr_pct": roi_5yr_pct,
            "payback_months": payback_months,
            "payback_years": payback_years,
            "low_budget_advisory": low_budget_advisory,
        },
        "cashflow_5yr": {
            "years": cashflow_years,
            "cumulative_net_cashflow_tl": cumulative_net_cashflow_tl,
            "cumulative_do_nothing_loss_tl": cumulative_do_nothing_loss_tl,
        },
        "certification_2029": cert_2029,
    }


def export_simulation_to_csv(sim_result: dict[str, Any]) -> str:
    """
    Simülasyon çıktısını kendi açık şemamızla uyumlu, herhangi bir kurumsal envanter
    veya su ayak izi aracına aktarılabilir CSV metnine dönüştürür.
    """
    buf = io.StringIO()
    writer = csv.writer(buf)
    fac = sim_result["facility_summary"]
    opt = sim_result["optimized_portfolio"]
    cert = sim_result["certification_2029"]

    writer.writerow(["# AquaSanayi AI — Endüstriyel Su Riski & ROI Optimizasyon Raporu (Açık Şema v1.0)"])
    writer.writerow(["Tesis Adı", fac["facility_name"]])
    writer.writerow(["OSB / Lokasyon", f"{fac['osb_name']} (Havza #{fac['pfaf_id']})"])
    writer.writerow(["Sektör", fac["sector_label"]])
    writer.writerow(["Yıllık Su Çekimi (m3/yıl)", fac["annual_water_m3"]])
    writer.writerow(["Yatırım Bütçesi (TL)", fac["capex_budget_tl"]])
    writer.writerow(["Seçilen Önlem CAPEX Toplamı (TL)", opt["total_capex_tl"]])
    writer.writerow(["Net Yıllık Su Tasarrufu (m3/yıl)", opt["annual_water_saved_m3"]])
    writer.writerow(["Net Tasarruf Oranı (%)", opt["multiplicative_savings_breakdown"]["total_saving_pct"]])
    writer.writerow(["Net Yıllık Finansal Kazanç (TL/yıl)", opt["net_annual_financial_benefit_tl"]])
    writer.writerow(["5 Yıllık NPV (TL)", opt["npv_5yr_tl"]])
    writer.writerow(["Geri Ödeme Süresi (Ay)", opt["payback_months"]])
    writer.writerow(["27.12.2029 Belge Kademesi", cert["achieved_tier"]])
    writer.writerow([])
    writer.writerow(
        [
            "Önlem Kodu",
            "Önlem Adı",
            "Hedef Proses",
            "Proses Tasarruf Oranı (%)",
            "CAPEX (TL)",
            "Yıllık OPEX Değişimi (TL)",
            "Tekil Su Tasarrufu (m3/yıl)",
            "Tahmini Geri Ödeme (Ay)",
            "SYGM / IFC Referansı",
        ]
    )
    for m in opt["selected_measures"]:
        writer.writerow(
            [
                m["measure_id"],
                m["name"],
                m["target_process_label"],
                m["process_saving_rate_pct"],
                m["capex_tl"],
                m["annual_opex_change_tl"],
                m["standalone_saved_m3"],
                m["estimated_payback_months"],
                m["nace_reference"],
            ]
        )
    return buf.getvalue()
