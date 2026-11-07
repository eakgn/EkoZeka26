"""
WBS-3: Şeffaf Bileşik Endüstriyel Su Kesintisi Risk İndeksi (`risk_index.py`)

Metodoloji İlkesi:
- Risk skoru kara kutu değildir; her bileşenin ağırlığı, ham fiziksel göstergesi ve
  toplam skora (0–100) katkı puanı açık formülüyle birlikte döndürülür.
- Coğrafi sınır koruması (Edge-Case #1): Türkiye'nin 639 alt-havzası dışındaki veya
  deniz üzerindeki tıklamalarda model körlemesine çalıştırılmaz; kullanıcıya açık uyarı
  ve en yakın kara alt-havzası önerilir.
"""

from __future__ import annotations

import json
from typing import Any

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point

from ekozeka26.data_pipeline import PROCESSED_DIR, SECTOR_AWR_MAP

_GDF_CACHE: gpd.GeoDataFrame | None = None
_PARQUET_CACHE: pd.DataFrame | None = None
_CLIMATE_CACHE: dict[str, Any] | None = None
_OSB_CACHE: dict[str, Any] | None = None


def _load_basins_gdf() -> gpd.GeoDataFrame:
    global _GDF_CACHE
    if _GDF_CACHE is None:
        _GDF_CACHE = gpd.read_file(PROCESSED_DIR / "turkey_basins.geojson")
    return _GDF_CACHE


def _load_basins_df() -> pd.DataFrame:
    global _PARQUET_CACHE
    if _PARQUET_CACHE is None:
        _PARQUET_CACHE = pd.read_parquet(PROCESSED_DIR / "turkey_basins.parquet")
    return _PARQUET_CACHE


def _load_climate_osb() -> dict[str, Any]:
    global _CLIMATE_CACHE
    if _CLIMATE_CACHE is None:
        path = PROCESSED_DIR / "climate_osb.json"
        if path.exists():
            _CLIMATE_CACHE = json.loads(path.read_text(encoding="utf-8"))
        else:
            _CLIMATE_CACHE = {"osb_projections": {}}
    return _CLIMATE_CACHE


def _load_osb_profiles() -> dict[str, Any]:
    global _OSB_CACHE
    if _OSB_CACHE is None:
        _OSB_CACHE = json.loads((PROCESSED_DIR / "osb_profiles.json").read_text(encoding="utf-8"))
    return _OSB_CACHE


def _future_ws_col(year: int | str, scenario: str = "BAU") -> str:
    yr_str = str(year).lower()
    if yr_str in ("baseline", "2025", "2026", "base"):
        return "bws_raw"
    scen = scenario.lower()
    if scen not in ("opt", "bau", "pes"):
        scen = "bau"
    yr_code = "30" if "30" in yr_str else ("80" if "80" in yr_str else "50")
    return f"{scen}{yr_code}_ws_x_r"


def classify_risk_score(score: float) -> str:
    if score >= 70.0:
        return "Çok Yüksek / Kritik Risk"
    if score >= 50.0:
        return "Yüksek Risk"
    if score >= 30.0:
        return "Orta Risk"
    return "Düşük / Yönetilebilir Risk"


def compute_transparent_risk(
    basin_row: dict[str, Any] | pd.Series,
    sector: str = "textile",
    year: int | str = 2050,
    scenario: str = "BAU",
    groundwater_dependency_pct: float | None = None,
    spei12_trend: float = -0.32,
) -> dict[str, Any]:
    """
    Bir alt-havza veya OSB için 0–100 aralığında tamamen şeffaf, denetlenebilir
    bileşik endüstriyel su kesintisi risk skorunu, bileşen katkılarını ve
    P10 / P50 / P90 beklenen yıllık kısıt/kesinti günü aralığını hesaplar.

    Ağırlık Kırılımı (Toplam 100 Puan):
      1. Gelecek & Yaz Pik Su Stresi (`water_stress`): max 25 puan
      2. Yeraltı Suyu Düşüşü & Kuyu Bağımlılığı (`groundwater_depletion`): max 25 puan
      3. SPEI-12 Kuraklık Rejimi & İklim Su Açığı (`drought_spei`): max 20 puan
      4. Sektörel Tahsis & Kalite/2029 Regülasyon Baskısı (`sectoral_pressure`): max 15 puan
      5. Mevsimsel & Yıllar Arası Arz Oynaklığı (`variability`): max 15 puan
    """
    sec_key = sector if sector in SECTOR_AWR_MAP else "general"
    awr_raw_col, awr_score_col, sec_label = SECTOR_AWR_MAP[sec_key]

    ws_col = _future_ws_col(year, scenario)
    ws_future_raw = float(basin_row.get(ws_col, basin_row.get("bws_raw", 0.5)))
    summer_bws_raw = float(basin_row.get("summer_bws_raw", ws_future_raw * 1.35))
    bws_base_raw = max(float(basin_row.get("bws_raw", 0.5)), 0.05)

    future_multiplier = float(np.clip(ws_future_raw / bws_base_raw, 0.65, 2.80))
    projected_summer_ws = summer_bws_raw * future_multiplier

    # 1. Bileşen: Gelecek & Yaz Pik Su Stresi (max 25 puan)
    ws_norm = float(np.clip(0.55 * (ws_future_raw / 1.60) + 0.45 * (projected_summer_ws / 2.40), 0.0, 1.0))
    pts_water_stress = round(25.0 * ws_norm, 2)

    # 2. Bileşen: Yeraltı Suyu Düşüşü & Kuyu Bağımlılığı (max 25 puan)
    gtd_raw = float(basin_row.get("gtd_raw", 0.0))
    gtd_score = float(basin_row.get("gtd_score", 2.0))
    pfaf_id = int(basin_row.get("pfaf_id", 0))
    if groundwater_dependency_pct is None:
        if pfaf_id in (211055, 211056):
            gw_dep = 95.0
            gw_prov = "Resmi Plan (SYGM Gediz Tahsis Planı)"
        elif pfaf_id == 221002:
            gw_dep = 92.0
            gw_prov = "Resmi Rapor (Konya Kapalı Havza YAS)"
        else:
            # Aqueduct yeraltı su tablası düşüş hızı (gtd_raw) ve su stresinden sürekli tahmin
            gtd_pos = max(0.0, gtd_raw)
            gw_dep = round(float(np.clip(35.0 + 260.0 * gtd_pos + 12.0 * min(bws_base_raw, 2.0), 30.0, 92.0)), 1)
            gw_prov = "Havza Göstergesinden Tahmin (Aqueduct gtd_raw)"
    else:
        gw_dep = float(groundwater_dependency_pct)
        gw_prov = (
            "Resmi Plan (SYGM Gediz / Konya)"
            if pfaf_id in (211056, 221002)
            else "Kalibre Varsayım (OSB Su Temin Profili)"
        )

    gtd_norm = float(np.clip(max(gtd_raw / 0.18, gtd_score / 4.5), 0.0, 1.0))
    gw_norm = float(np.clip(0.58 * gtd_norm + 0.42 * (gw_dep / 100.0), 0.0, 1.0))
    pts_groundwater = round(25.0 * gw_norm, 2)

    # 3. Bileşen: SPEI-12 Kuraklık Rejimi & İklim Su Açığı (max 20 puan)
    drr_raw = float(basin_row.get("drr_raw", 0.5))
    scen_upper = str(scenario).upper()
    scen_drought_boost = 1.22 if scen_upper == "PES" else (0.85 if scen_upper == "OPT" else 1.0)
    spei_severity = float(np.clip(abs(min(0.0, spei12_trend)) / 0.50, 0.0, 1.0))
    drought_norm = float(np.clip((0.65 * (drr_raw / 0.72) + 0.35 * spei_severity) * scen_drought_boost, 0.0, 1.0))
    pts_drought = round(20.0 * drought_norm, 2)

    # 4. Bileşen: Sektörel Tahsis & Kalite/2029 Regülasyon Baskısı (max 15 puan)
    awr_score = float(basin_row.get(awr_score_col, basin_row.get("w_awr_def_tot_score", 2.5)))
    sector_water_intensity = {
        "textile": 1.15,
        "food": 1.12,
        "chemical": 1.10,
        "semiconductor": 1.18,
        "energy": 1.08,
        "metal": 0.96,
        "mining": 1.02,
        "general": 1.00,
    }.get(sec_key, 1.0)
    sec_norm = float(np.clip((awr_score / 4.2) * sector_water_intensity, 0.0, 1.0))
    pts_sectoral = round(15.0 * sec_norm, 2)

    # 5. Bileşen: Mevsimsel & Yıllar Arası Arz Oynaklığı (max 15 puan)
    sev_raw = float(basin_row.get("sev_raw", 1.0))
    iav_raw = float(basin_row.get("iav_raw", 0.5))
    var_norm = float(np.clip(0.60 * (sev_raw / 2.2) + 0.40 * (iav_raw / 1.1), 0.0, 1.0))
    pts_variability = round(15.0 * var_norm, 2)

    total_score = round(
        float(np.clip(pts_water_stress + pts_groundwater + pts_drought + pts_sectoral + pts_variability, 0.0, 100.0)),
        1,
    )

    # Beklenen Yıllık Kısıt/Kesinti Günü (P10 İyimser / P50 Beklenen / P90 Kurak Kriz)
    base_days = max(0.0, (total_score - 18.0) / 82.0) ** 1.35 * 46.0
    p50_days = round(base_days, 1)
    p10_days = round(max(0.0, base_days * 0.52), 1)
    p90_days = round(min(120.0, base_days * 1.68 + (4.5 if gw_dep >= 85.0 else 1.5)), 1)

    components = [
        {
            "key": "groundwater_depletion",
            "label": "Yeraltı Suyu Düşüşü & Kuyu Bağımlılığı",
            "weight_max": 25.0,
            "points": pts_groundwater,
            "raw_indicator": f"gtd={gtd_raw:.3f} cm/yıl, kuyu bağımlılığı=%{gw_dep:.0f}",
            "formula_note": "25 × (0.58·norm(gtd) + 0.42·kuyu_oranı)",
            "provenance": gw_prov,
            "info_summary": "Akifer su tablasının yıllık düşüş hızını (gtd_raw) ve sanayinin kuyulara bağımlılığını ölçer. Kuyu seviyesi düştükçe pompaj maliyeti artar ve kuraklıkta DSİ/SYGM tahsis kısıtı riski doğar.",
        },
        {
            "key": "water_stress",
            "label": f"Gelecek ({year} {scenario}) & Yaz Pik Su Stresi",
            "weight_max": 25.0,
            "points": pts_water_stress,
            "raw_indicator": f"yıllık ws={ws_future_raw:.2f}, yaz pik={projected_summer_ws:.2f}",
            "formula_note": "25 × (0.55·norm(ws_yıllık) + 0.45·norm(ws_yaz_pik))",
            "provenance": "Ölçülmüş + CMIP6 Model (WRI Aqueduct 4.0)",
            "info_summary": "Havzadaki toplam su çekiminin yenilenebilir su arzına oranıdır (>1.0 aşırı stres). Yaz aylarında (Ağustos) tarımsal sulama ile sanayi aynı kaynağı paylaştığı için pik stres kesintiyi belirler.",
        },
        {
            "key": "drought_spei",
            "label": "SPEI-12 Kuraklık Trendi & Hidrolojik Kuraklık Riski",
            "weight_max": 20.0,
            "points": pts_drought,
            "raw_indicator": f"drr={drr_raw:.2f}, SPEI-12 eğim={spei12_trend:.2f}/on-yıl",
            "formula_note": "20 × (0.65·norm(drr) + 0.35·norm(|SPEI_trend|)) × senaryo_çarpanı",
            "provenance": "Model (ERA5 + CMIP6 QDM + Aqueduct drr)",
            "info_summary": "Yağış eksi buharlaşma (P − ET₀) dengesinin 12 aylık standartlaştırılmış eğilimini ve tarihsel kuraklık şiddetini gösterir. Negatif eğilim baraj ve akiferlerin beslenemediğini kanıtlar.",
        },
        {
            "key": "sectoral_pressure",
            "label": f"Sektörel Tahsis & 2029 Belge Baskısı ({sec_label})",
            "weight_max": 15.0,
            "points": pts_sectoral,
            "raw_indicator": f"{awr_score_col}={awr_score:.2f}/5.0",
            "formula_note": "15 × norm(w_awr_sektör × su_yoğunluk_katsayısı)",
            "provenance": "Ölçülmüş (Aqueduct Sektörel AWR) + Regülasyon",
            "info_summary": "Seçilen sanayi sektörünün havzadaki fiziksel, kalite ve regülasyon (27.12.2029 Yeşil Su Verimliliği Belgesi) baskısına duyarlılığını ölçer.",
        },
        {
            "key": "variability",
            "label": "Mevsimsel & Yıllar Arası Arz Oynaklığı",
            "weight_max": 15.0,
            "points": pts_variability,
            "raw_indicator": f"mevsimsel sev={sev_raw:.2f}, yıllar-arası iav={iav_raw:.2f}",
            "formula_note": "15 × (0.60·norm(sev) + 0.40·norm(iav))",
            "provenance": "Ölçülmüş (WRI Aqueduct 4.0 sev_raw & iav_raw)",
            "info_summary": "Yıllık toplam su yeterli görünse bile suyun aylara ve yıllara düzensiz dağılmasını ölçer. Yüksek oynaklık, depolama veya geri kazanım olmayan fabrikalarda ani yaz kesintilerine yol açar.",
        },
    ]
    components.sort(key=lambda x: x["points"], reverse=True)

    return {
        "string_id": str(basin_row.get("string_id", "")),
        "pfaf_id": pfaf_id,
        "province_name": str(basin_row.get("name_1", "")),
        "sector": sec_key,
        "sector_label": sec_label,
        "target_year": year,
        "scenario": scenario.upper(),
        "composite_risk_score": total_score,
        "risk_category": classify_risk_score(total_score),
        "expected_cutback_days": {
            "p10": p10_days,
            "p50": p50_days,
            "p90": p90_days,
            "provenance": "Sezgisel Risk-Süre İndeksi (Kalibre Model)",
            "methodology_note": (
                "Fabrika bazında tarihsel kesinti günü verisi kamuya açık olmadığından bileşik risk skorundan "
                "üretilmiş gösterge niteliğinde endekstir (P10 = 0.52×P50, P90 ≈ 1.68×P50 + kuyu eki)."
            ),
        },
        "indicators": {
            "baseline_bws_raw": round(bws_base_raw, 3),
            "projected_annual_ws_raw": round(ws_future_raw, 3),
            "projected_summer_peak_ws_raw": round(projected_summer_ws, 3),
            "gtd_raw": round(gtd_raw, 3),
            "drr_raw": round(drr_raw, 3),
            "sev_raw": round(sev_raw, 3),
            "iav_raw": round(iav_raw, 3),
            "groundwater_dependency_pct": round(gw_dep, 1),
            "groundwater_provenance": gw_prov,
            "spei12_decadal_trend": round(spei12_trend, 3),
        },
        "component_breakdown": components,
    }


def find_basin_by_coords(lat: float, lon: float) -> dict[str, Any]:
    """
    Edge-Case #1 (Coğrafi Sınır Koruması):
    Verilen (lat, lon) koordinatının Türkiye'nin 639 alt-havza poligonu içinde olup olmadığını
    kontrol eder. Deniz üzerinde veya Türkiye sınırları dışındaysa model körlemesine çalıştırılmaz;
    açık uyarı mesajı ile en yakın kara alt-havzası önerilir.
    """
    gdf = _load_basins_gdf()
    pt = Point(float(lon), float(lat))

    in_bbox = (35.5 <= lat <= 42.3) and (25.5 <= lon <= 45.0)
    contains_hits = gdf[gdf.geometry.contains(pt)] if in_bbox else gdf.iloc[0:0]

    if not contains_hits.empty:
        row = contains_hits.iloc[0]
        return {
            "inside_turkey": True,
            "warning": None,
            "clicked_lat": round(float(lat), 4),
            "clicked_lon": round(float(lon), 4),
            "basin_row": row.drop(labels=["geometry"]).to_dict(),
        }

    lons = gdf["centroid_lon"].to_numpy()
    lats = gdf["centroid_lat"].to_numpy()
    dist_deg = np.sqrt((lons - float(lon)) ** 2 + (lats - float(lat)) ** 2)
    nearest_idx = int(np.argmin(dist_deg))
    nearest_row = gdf.iloc[nearest_idx]

    return {
        "inside_turkey": False,
        "warning": (
            f"Seçilen nokta ({lat:.3f}°K, {lon:.3f}°D) Türkiye kara sınırları / 639 alt-havza "
            f"poligonu dışında veya deniz üzerindedir. En yakın kara alt-havzası "
            f"({nearest_row['name_1']} — Havza #{nearest_row['pfaf_id']}) önerilmiştir."
        ),
        "clicked_lat": round(float(lat), 4),
        "clicked_lon": round(float(lon), 4),
        "nearest_distance_km": round(float(dist_deg[nearest_idx]) * 111.0, 1),
        "basin_row": nearest_row.drop(labels=["geometry"]).to_dict(),
    }


def compare_candidate_osbs(
    osb_ids: list[str] | None = None,
    sector: str = "textile",
    year: int | str = 2050,
    scenario: str = "BAU",
) -> dict[str, Any]:
    """
    Seçilen aday OSB'leri şeffaf bileşik risk skoru, P10/P50/P90 kesinti günü,
    yeraltı suyu düşüş trendi ve iklim su dengesi açısından karşılaştırıp sıralar ve
    yatırım için en güvenli lokasyon önerisini üretir.
    """
    osb_meta = _load_osb_profiles()
    climate_meta = _load_climate_osb().get("osb_projections", {})
    df_basins = _load_basins_df().set_index("string_id")

    all_osbs = {o["osb_id"]: o for o in osb_meta["osbs"]}
    if not osb_ids:
        osb_ids = [
            "kocaeli_gosb",
            "bursa_osb",
            "izmir_aliaga",
            "izmir_iaosb",
            "konya_osb",
            "izmir_kemalpasa",
            "manisa_osb",
        ]

    results: list[dict[str, Any]] = []
    for oid in osb_ids:
        if oid not in all_osbs:
            continue
        o_info = all_osbs[oid]
        sid = o_info["string_id"]
        basin_row = df_basins.loc[sid].to_dict() if sid in df_basins.index else o_info

        c_proj = climate_meta.get(oid, {}).get("scenarios", {}).get(scenario.upper(), {})
        decadal_wb_trend = float(c_proj.get("decadal_trend_mm", -32.0))
        spei_proxy_trend = round(decadal_wb_trend / 95.0, 2)

        risk_eval = compute_transparent_risk(
            basin_row=basin_row,
            sector=sector,
            year=year,
            scenario=scenario,
            groundwater_dependency_pct=float(o_info["groundwater_dependency_pct"]),
            spei12_trend=spei_proxy_trend,
        )

        results.append(
            {
                "osb_id": oid,
                "name": o_info["name"],
                "city": o_info["city"],
                "corridor_region": o_info.get("corridor_region", o_info["city"]),
                "in_focus_corridor": bool(o_info.get("in_focus_corridor", True)),
                "basin_name": o_info["basin_name"],
                "lat": o_info["lat"],
                "lon": o_info["lon"],
                "drought_cutback_risk_pct": o_info["drought_cutback_risk_pct"],
                "gw_provenance": o_info.get("gw_provenance", "Kalibre Varsayım"),
                "osb_grid_tariff_tl_m3": o_info.get("osb_grid_tariff_tl_m3", 118.50),
                "tariff_provenance": o_info.get("tariff_provenance", "Kalibre Varsayım"),
                "drying_agreement_pct": c_proj.get("drying_agreement_pct", 100.0),
                "delta_wb_2050_mm": c_proj.get("delta_wb_2050_vs_baseline_mm", -85.0),
                **risk_eval,
            }
        )

    results.sort(key=lambda x: x["composite_risk_score"])
    for rank_i, item in enumerate(results, start=1):
        item["safety_rank"] = rank_i

    safest = results[0] if results else None
    riskiest = results[-1] if results else None
    recommendation_text = ""
    if safest and riskiest:
        diff_pts = round(riskiest["composite_risk_score"] - safest["composite_risk_score"], 1)
        diff_days = round(
            riskiest["expected_cutback_days"]["p50"] - safest["expected_cutback_days"]["p50"], 1
        )
        recommendation_text = (
            f"Yatırım için en güvenli bölge: {safest['name']} (Risk Skoru: {safest['composite_risk_score']}/100, "
            f"Beklenen Kesinti: {safest['expected_cutback_days']['p50']} gün/yıl [P10–P90: "
            f"{safest['expected_cutback_days']['p10']}–{safest['expected_cutback_days']['p90']} gün]). "
            f"En yüksek riskli aday olan {riskiest['name']} ({riskiest['composite_risk_score']}/100) ile "
            f"karşılaştırıldığında risk skoru {diff_pts} puan daha düşük olup yılda ortalama {diff_days} gün "
            f"daha az su kısıtı/üretim duruşu beklenmektedir."
        )

    return {
        "sector": sector,
        "target_year": year,
        "scenario": scenario.upper(),
        "candidate_count": len(results),
        "safest_osb": safest,
        "riskiest_osb": riskiest,
        "recommendation_summary": recommendation_text,
        "rankings": results,
    }
