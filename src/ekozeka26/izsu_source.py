"""
İZSU veri kaynağı: canlı fetch + offline fallback zinciri.

Neden bu modül var?
- `/api/izsu-live` adı yanıltıcıydı: çalışma anında İZSU'ya istek atmıyor, yalnızca
  `data/processed/izsu_snapshot.json` dosyasını okuyordu.
- `data/fallback/izsu_snapshot.json` üretiliyordu ama hiçbir yerde kullanılmıyordu.

Bu modül şu protokolü uygular:
1. Taze canlı önbellek (`data/cache/izsu_live_snapshot.json`, varsayılan 6 saat) varsa onu kullan.
2. Yoksa doğrulanmış `data/processed/izsu_snapshot.json` dosyasını kullan.
3. O da yoksa/bozuksa `data/fallback/izsu_snapshot.json` dosyasına düş.
4. `--refresh` ile canlı İZSU baraj sayfası çekilir; başarılıysa aylık üretim ve tarife
   katmanı doğrulanmış snapshot'tan korunarak canlı önbelleğe yazılır.
5. Canlı fetch başarısız olursa API çökmez; kaynak modu ve fallback nedeni döner.

Kullanım:
    uv run python -m ekozeka26.izsu_source --status
    uv run python -m ekozeka26.izsu_source --refresh
"""

from __future__ import annotations

import argparse
import json
import os
import re
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import httpx

from ekozeka26.data_pipeline import (
    FALLBACK_DIR,
    PROCESSED_DIR,
    PROJECT_ROOT,
    _find_json_key,
)

IZSU_URL = "https://izsu.gov.tr/bilgi-merkezi/barajlar/su-durumu"
LIVE_CACHE_PATH = PROJECT_ROOT / "data" / "cache" / "izsu_live_snapshot.json"
LIVE_CACHE_TTL_HOURS = 6.0
MIN_DAMS = 5
REQUEST_TIMEOUT_S = 4.0

# Testlerde monkeypatch ile değiştirilebilen modül seviyesi yollar:
_PROCESSED_PATH = PROCESSED_DIR / "izsu_snapshot.json"
_FALLBACK_PATH = FALLBACK_DIR / "izsu_snapshot.json"


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None
    return obj if isinstance(obj, dict) else None


def _valid_snapshot(snapshot: dict[str, Any] | None) -> bool:
    if not isinstance(snapshot, dict):
        return False
    dams = snapshot.get("dams")
    if not isinstance(dams, list) or len(dams) < MIN_DAMS:
        return False
    if not isinstance(snapshot.get("headline_metrics"), dict):
        return False
    # Canlı birleştirmede aylık seri/tarife doğrulanmış snapshot'tan korunur; yine de
    # tam bir snapshot olduğundan emin olalım.
    if not snapshot.get("monthly_production_2025"):
        return False
    if not snapshot.get("tariffs_2026"):
        return False
    return True


def _age_days(snapshot_date: Any) -> int | None:
    try:
        d = date.fromisoformat(str(snapshot_date)[:10])
    except (TypeError, ValueError):
        return None
    return max(0, (date.today() - d).days)


def _cache_age_hours(snapshot: dict[str, Any], path: Path) -> float:
    fetched_at = snapshot.get("fetched_at")
    if fetched_at:
        try:
            dt = datetime.fromisoformat(str(fetched_at).replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return max(0.0, (datetime.now(timezone.utc) - dt).total_seconds() / 3600.0)
        except (TypeError, ValueError):
            pass
    try:
        return max(0.0, (datetime.now().timestamp() - path.stat().st_mtime) / 3600.0)
    except OSError:
        return float("inf")


def _parse_live_html(html: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """İZSU Next.js sayfasındaki `initialTodayData` / `initialOneYearAgoData` dizilerini çıkarır."""
    today: list[dict[str, Any]] = []
    last_year: list[dict[str, Any]] = []
    for m in re.finditer(r"self\.__next_f\.push\(\[1,(\".*?\")\]\)", html):
        try:
            s = json.loads(m.group(1))
        except json.JSONDecodeError:
            continue
        if "initialTodayData" not in s:
            continue
        arr = json.loads(s.split(":", 1)[1])
        props = _find_json_key(arr, "initialTodayData")
        if props:
            today = props.get("initialTodayData", {}).get("data", []) or []
            last_year = props.get("initialOneYearAgoData", {}).get("data", []) or []
        break
    return today, last_year


def _merge_live(
    base: dict[str, Any],
    today: list[dict[str, Any]],
    last_year: list[dict[str, Any]],
    fetched_at: str | None = None,
) -> dict[str, Any]:
    """Canlı baraj kesitini doğrulanmış snapshot'ın aylık/tarife katmanıyla birleştirir."""
    if len(today) < MIN_DAMS:
        raise ValueError(f"Canlı İZSU verisinde yeterli baraj yok: {len(today)}")

    base_dams = {d.get("name"): d for d in base.get("dams", []) if d.get("name")}
    last_by_name = {
        d.get("damWellFacility", {}).get("name"): d
        for d in last_year
        if d.get("damWellFacility", {}).get("name")
    }

    dams: list[dict[str, Any]] = []
    total_usable_m3 = 0.0
    total_capacity_m3 = 0.0
    for item in today:
        name = item.get("damWellFacility", {}).get("name")
        if not name:
            continue
        usable_m3 = float(item.get("usableWaterStatus", 0.0) or 0.0)
        cap_m3 = float(item.get("usableWaterCapacity", 0.0) or 0.0)
        occ_today = float(item.get("occupancyRate", 0.0) or 0.0)
        if not (0.0 <= occ_today <= 100.0) or cap_m3 <= 0.0:
            continue

        prev = base_dams.get(name, {})
        ly = last_by_name.get(name, {})
        occ_last_year = float(ly.get("occupancyRate", prev.get("last_year_occupancy_pct", 0.0)) or 0.0)
        occ_oct = float(prev.get("oct14_occupancy_pct", occ_today) or occ_today)
        delta_23d = round(occ_today - occ_oct, 2) if prev else 0.0

        total_usable_m3 += usable_m3
        total_capacity_m3 += cap_m3
        dams.append(
            {
                "name": name,
                "date": item.get("date", base.get("snapshot_date")),
                "occupancy_pct": round(occ_today, 2),
                "last_year_occupancy_pct": round(occ_last_year, 2),
                "oct14_occupancy_pct": round(occ_oct, 2),
                "delta_23d_pct_points": delta_23d,
                "usable_volume_m3": usable_m3,
                "usable_capacity_m3": cap_m3,
                "capacity_share_pct": 0.0,
                "daily_production_m3": float(prev.get("daily_production_m3", 0.0) or 0.0),
                "lat": prev.get("lat", 38.3),
                "lon": prev.get("lon", 27.1),
            }
        )

    if len(dams) < MIN_DAMS:
        raise ValueError(f"Geçerli canlı baraj sayısı yetersiz: {len(dams)}")

    for item in dams:
        item["capacity_share_pct"] = round(
            100.0 * item["usable_capacity_m3"] / max(total_capacity_m3, 1.0), 2
        )

    weighted_occ_pct = round(100.0 * total_usable_m3 / max(total_capacity_m3, 1.0), 2)
    simple_avg_occ_pct = round(float(sum(x["occupancy_pct"] for x in dams) / len(dams)), 2)
    base_headline = base.get("headline_metrics", {})

    def _by_name(fragment: str, key: str, default: Any) -> Any:
        return next((d[key] for d in dams if fragment.lower() in d["name"].lower()), default)

    merged = dict(base)
    merged.update(
        {
            "snapshot_date": max((str(d.get("date") or "") for d in dams), default="")
            or date.today().isoformat(),
            "source": (
                "İZSU Resmi Baraj Su Durumu (canlı fetch) + doğrulanmış snapshot "
                "aylık üretim/tarife katmanı"
            ),
            "source_mode": "live_fetch",
            "fetched_at": fetched_at or datetime.now(timezone.utc).isoformat(),
            "live_fetch_metadata": {
                "url": IZSU_URL,
                "fetched_at": fetched_at or datetime.now(timezone.utc).isoformat(),
                "base_snapshot_date": base.get("snapshot_date"),
                "note": (
                    "Canlı sayfa yalnızca baraj/kuyu doluluk kesitini içerir; aylık üretim "
                    "serisi, 23 günlük kesit ve 2026 tarifeleri doğrulanmış snapshot'tan korunur."
                ),
            },
            "headline_metrics": {
                "capacity_weighted_occupancy_pct": weighted_occ_pct,
                "simple_average_occupancy_pct": simple_avg_occ_pct,
                "total_usable_water_mm3": round(total_usable_m3 / 1e6, 2),
                "total_usable_capacity_mm3": round(total_capacity_m3 / 1e6, 2),
                "gordes_occupancy_pct": _by_name(
                    "Gördes", "occupancy_pct", base_headline.get("gordes_occupancy_pct")
                ),
                "gordes_capacity_share_pct": _by_name(
                    "Gördes", "capacity_share_pct", base_headline.get("gordes_capacity_share_pct")
                ),
                "tahtali_today_pct": _by_name(
                    "Tahtalı", "occupancy_pct", base_headline.get("tahtali_today_pct")
                ),
                "tahtali_last_year_pct": _by_name(
                    "Tahtalı", "last_year_occupancy_pct", base_headline.get("tahtali_last_year_pct")
                ),
                "balcova_23d_drop_pct_points": _by_name(
                    "Balçova", "delta_23d_pct_points", base_headline.get("balcova_23d_drop_pct_points")
                ),
                "daily_well_share_pct": base_headline.get("daily_well_share_pct"),
            },
            "dams": dams,
        }
    )
    return merged


def fetch_live_izsu_snapshot(
    base: dict[str, Any] | None = None,
    timeout_s: float = REQUEST_TIMEOUT_S,
) -> dict[str, Any] | None:
    """
    İZSU baraj sayfasını canlı çeker. Başarılıysa canlı önbelleğe yazar ve döner.
    Herhangi bir hata (ağ, HTTP, ayrıştırma, doğrulama) durumunda `None` döner;
    çağıran taraf doğrulanmış snapshot'a düşer.
    """
    if base is None:
        base, _, _ = _load_cached()
    if base is None:
        return None
    try:
        response = httpx.get(
            IZSU_URL,
            timeout=timeout_s,
            follow_redirects=True,
            headers={"User-Agent": "AquaSanayi-AI/1.0 (offline-first demo)"},
        )
        response.raise_for_status()
        today, last_year = _parse_live_html(response.text)
        merged = _merge_live(base, today, last_year)
        if not _valid_snapshot(merged):
            return None
        LIVE_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        LIVE_CACHE_PATH.write_text(
            json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return merged
    except (httpx.HTTPError, ValueError, json.JSONDecodeError, OSError):
        return None


def _load_cached() -> tuple[dict[str, Any] | None, str | None, str | None]:
    """
    Önbellek zinciri: taze canlı önbellek → doğrulanmış processed → fallback.
    Dönen üçüncü değer, neden daha aşağıdaki katmana düşüldüğünü açıklar.
    """
    reasons: list[str] = []

    if LIVE_CACHE_PATH.exists():
        live = _read_json(LIVE_CACHE_PATH)
        if _valid_snapshot(live):
            age_h = _cache_age_hours(live, LIVE_CACHE_PATH)  # type: ignore[arg-type]
            if age_h <= LIVE_CACHE_TTL_HOURS:
                return live, str(LIVE_CACHE_PATH), None
            reasons.append(f"canlı önbellek eski ({age_h:.1f} saat > {LIVE_CACHE_TTL_HOURS:.0f} saat)")
        else:
            reasons.append("canlı önbellek geçersiz")

    for label, path in (("doğrulanmış", _PROCESSED_PATH), ("fallback", _FALLBACK_PATH)):
        snapshot = _read_json(path)
        if _valid_snapshot(snapshot):
            return snapshot, str(path), "; ".join(reasons) or None
        reasons.append(f"{label} snapshot yok/geçersiz: {path.name}")

    return None, None, "; ".join(reasons)


def load_izsu_snapshot(
    prefer_live: bool = False,
    force_live: bool = False,
    timeout_s: float = REQUEST_TIMEOUT_S,
) -> dict[str, Any]:
    """
    API'nin kullanacağı tek giriş noktası.

    - Varsayılan `prefer_live=False`: demo/offline için yalnızca yerel önbellek zinciri.
    - `prefer_live=True` ve `IZSU_OFFLINE != 1`: önce yerel zinciri yükler, sonra canlı
      fetch dener; başarısız olursa yerel snapshot'ı `fallback_reason` ile döner.
    - `force_live=True`: CLI `--refresh` için ortam değişkenini yok sayar.
    """
    base, path, reason = _load_cached()
    if base is None:
        raise FileNotFoundError(
            "İZSU snapshot bulunamadı. `uv run python -m ekozeka26.data_pipeline --offline` "
            f"çalıştırın. Ayrıntı: {reason}"
        )

    snapshot = dict(base)
    snapshot["source_mode"] = (
        "live_cache"
        if path == str(LIVE_CACHE_PATH)
        else ("verified_snapshot" if path == str(_PROCESSED_PATH) else "fallback_snapshot")
    )
    snapshot["resolved_path"] = path
    snapshot["age_days"] = _age_days(snapshot.get("snapshot_date"))
    snapshot["fallback_reason"] = reason

    should_try_live = (prefer_live or force_live) and (
        force_live or os.getenv("IZSU_OFFLINE", "0") != "1"
    )
    if should_try_live:
        live = fetch_live_izsu_snapshot(base, timeout_s=timeout_s)
        if live is not None:
            live["source_mode"] = "live_fetch"
            live["resolved_path"] = str(LIVE_CACHE_PATH)
            live["age_days"] = _age_days(live.get("snapshot_date"))
            live["fallback_reason"] = None
            return live
        snapshot["fallback_reason"] = (
            (reason + "; ") if reason else ""
        ) + "canlı İZSU fetch başarısız; doğrulanmış snapshot kullanıldı"

    return snapshot


def _status_payload() -> dict[str, Any]:
    snapshot = load_izsu_snapshot(prefer_live=False)
    return {
        "source_mode": snapshot.get("source_mode"),
        "snapshot_date": snapshot.get("snapshot_date"),
        "age_days": snapshot.get("age_days"),
        "resolved_path": snapshot.get("resolved_path"),
        "fallback_reason": snapshot.get("fallback_reason"),
        "live_cache_path": str(LIVE_CACHE_PATH),
        "live_cache_exists": LIVE_CACHE_PATH.exists(),
        "live_cache_ttl_hours": LIVE_CACHE_TTL_HOURS,
        "dams_count": len(snapshot.get("dams", [])),
        "headline_metrics": snapshot.get("headline_metrics", {}),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="İZSU canlı/offline veri kaynağı")
    parser.add_argument("--refresh", action="store_true", help="Canlı İZSU sayfasını çek ve önbelleğe yaz")
    parser.add_argument("--status", action="store_true", help="Mevcut kaynak modunu ve önbellek yaşını göster")
    args = parser.parse_args()

    if args.refresh:
        snapshot = load_izsu_snapshot(force_live=True)
    else:
        snapshot = load_izsu_snapshot(prefer_live=False)

    print(
        json.dumps(
            {
                "source_mode": snapshot.get("source_mode"),
                "snapshot_date": snapshot.get("snapshot_date"),
                "age_days": snapshot.get("age_days"),
                "fallback_reason": snapshot.get("fallback_reason"),
                "dams_count": len(snapshot.get("dams", [])),
                "headline_metrics": snapshot.get("headline_metrics", {}),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
