"""
WBS-3: İZSU & Gediz Hidrolojik Anomali Tespiti (`anomaly.py`)

V&V Veri Kuralı:
- `baraj.csv` (14.10.2026) ve `gunluk.csv` tek günlük anlık kesitlerdir.
- Gerçek aylık zaman serisi `izsu_aylik.html` içindeki 137 ham satırdan (126 tekil tesis-ay)
  (2025 yılı 12 ay × 11 baraj/kuyu tesisi) çıkarılmıştır (`izsu_snapshot.json`).
- Isolation Forest (Liu, Ting & Zhou 2008) ile:
  1. Kasım 2025'te Tahtalı Barajı üretiminin 6,91 Mm³ -> 1,62 Mm³'e (-%76,5) çöküp
     yeraltı kuyularının (Göksu, Halkapınar, Sarıkız, Menemen) toplam arzın >%62'sini
     üstlendiği rejim kayması anomalisi yakalanır.
  2. `baraj.csv` (14 Ekim 2026) -> `izsu.html` (6 Kasım 2026) arasındaki 23 günlük kesitte
     Balçova Barajı'ndaki -%7,43 puanlık hızlı düşüş ve Gördes/Balçova günlük üretiminin
     0 m³/gün'e inmesi tespit edilir.
"""

from __future__ import annotations

import json
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

from ekozeka26.data_pipeline import PROCESSED_DIR


def detect_izsu_and_gediz_anomalies() -> dict[str, Any]:
    """
    İZSU 2025 aylık üretim zaman serisi (137 ham satır → 126 tekil tesis-ay) üzerinde Isolation Forest çalıştırır
    ve 23 günlük baraj kesit deltası (14 Ekim -> 6 Kasım 2026) ile birleştirilmiş
    anomali raporunu döner.
    """
    izsu_path = PROCESSED_DIR / "izsu_snapshot.json"
    izsu = json.loads(izsu_path.read_text(encoding="utf-8"))

    records = izsu["monthly_production_2025"]
    df_raw = pd.DataFrame(records)
    # İZSU verisinde aynı (yıl, ay, tesis) için mükerrer satır varsa (137 ham -> 126 tekil tesis-ay) tekilleştir
    df = df_raw.drop_duplicates(subset=["year", "month", "facility_name"]).copy()

    monthly_source = (
        df.groupby(["year", "month", "source_type"], as_index=False)["production_mm3"]
        .sum()
        .pivot(index=["year", "month"], columns="source_type", values="production_mm3")
        .fillna(0.0)
        .reset_index()
    )
    monthly_source["total_mm3"] = monthly_source.get("Baraj", 0.0) + monthly_source.get("Kuyu", 0.0)
    monthly_source["well_share_pct"] = np.round(
        100.0 * monthly_source.get("Kuyu", 0.0) / np.maximum(monthly_source["total_mm3"], 0.001), 2
    )

    tahtali_df = (
        df[df["facility_name"].str.contains("Tahtalı", case=False, na=False)]
        .groupby(["year", "month"], as_index=False)["production_mm3"]
        .sum()
        .rename(columns={"production_mm3": "tahtali_mm3"})
    )
    goksu_halkapinar_df = (
        df[df["facility_name"].str.contains("Göksu|Halkapınar|Sarıkız|Menemen", case=False, na=False)]
        .groupby(["year", "month"], as_index=False)["production_mm3"]
        .sum()
        .rename(columns={"production_mm3": "major_wells_mm3"})
    )

    m_panel = (
        monthly_source.merge(tahtali_df, on=["year", "month"], how="left")
        .merge(goksu_halkapinar_df, on=["year", "month"], how="left")
        .fillna(0.0)
        .sort_values(["year", "month"])
        .reset_index(drop=True)
    )

    tahtali_peak_mm3 = float(m_panel["tahtali_mm3"].max())  # Ağustos 2025: 6.91 Mm³
    m_panel["tahtali_vs_peak_pct"] = np.round(
        100.0 * (m_panel["tahtali_mm3"] - tahtali_peak_mm3) / max(tahtali_peak_mm3, 0.01), 1
    )

    feat_cols = ["tahtali_mm3", "well_share_pct", "major_wells_mm3", "tahtali_vs_peak_pct"]
    iso = IsolationForest(n_estimators=150, contamination=0.17, random_state=42)
    labels = iso.fit_predict(m_panel[feat_cols])
    scores = -iso.score_samples(m_panel[feat_cols])
    m_panel["is_anomaly"] = labels == -1
    m_panel["anomaly_score"] = np.round(scores, 4)

    nov_row = m_panel[m_panel["month"] == 11].iloc[0]
    aug_row = m_panel[m_panel["month"] == 8].iloc[0]
    tahtali_drop_pct = round(
        100.0 * (float(nov_row["tahtali_mm3"]) - float(aug_row["tahtali_mm3"])) / max(float(aug_row["tahtali_mm3"]), 0.01),
        1,
    )

    dam_alerts: list[dict[str, Any]] = []
    for d in izsu["dams"]:
        delta = float(d["delta_23d_pct_points"])
        occ = float(d["occupancy_pct"])
        daily_m3 = float(d["daily_production_m3"])
        if delta <= -4.0 or occ < 30.0 or daily_m3 == 0.0:
            severity = "KRİTİK" if (delta <= -6.0 or occ < 30.0) else "UYARI"
            dam_alerts.append(
                {
                    "dam_name": d["name"],
                    "severity": severity,
                    "occupancy_today_pct": occ,
                    "occupancy_oct14_pct": d["oct14_occupancy_pct"],
                    "delta_23d_pct_points": delta,
                    "daily_production_m3": daily_m3,
                    "alert_message": (
                        f"{d['name']}: 23 günde {delta:+.2f} puan değişim "
                        f"(%{d['oct14_occupancy_pct']:.2f} → %{occ:.2f}); "
                        f"günlük üretim {daily_m3:,.0f} m³/gün."
                    ),
                }
            )

    anomalies_detected = m_panel[m_panel["is_anomaly"]].to_dict(orient="records")

    return {
        "detector": "IsolationForest (n_estimators=150, contamination=0.17) + 23-Günlük Baraj Kesit Deltası",
        "monthly_records_analyzed": len(df_raw),
        "unique_facility_months": len(df),
        "facilities_count": int(df["facility_name"].nunique()),
        "november_2025_regime_shift": {
            "month": "2025-11",
            "tahtali_peak_aug_2025_mm3": round(float(aug_row["tahtali_mm3"]), 2),
            "tahtali_nov_2025_mm3": round(float(nov_row["tahtali_mm3"]), 2),
            "tahtali_collapse_pct": tahtali_drop_pct,
            "well_share_nov_2025_pct": round(float(nov_row["well_share_pct"]), 2),
            "isolation_forest_anomaly_score": round(float(nov_row["anomaly_score"]), 4),
            "is_flagged_anomaly": bool(nov_row["is_anomaly"]),
            "explanation": (
                f"Kasım 2025 kuraklığında Tahtalı Barajı aylık üretimi {float(aug_row['tahtali_mm3']):.2f} Mm³ "
                f"yaz zirvesinden {float(nov_row['tahtali_mm3']):.2f} Mm³'e ({tahtali_drop_pct:+.1f}%) çökerken, "
                f"yeraltı kuyuları (Göksu, Halkapınar, Sarıkız, Menemen) toplam İzmir arzının "
                f"%{float(nov_row['well_share_pct']):.1f}'ini üstlenmiştir."
            ),
        },
        "snapshot_23d_dam_alerts": dam_alerts,
        "monthly_series_2025": m_panel.to_dict(orient="records"),
        "flagged_monthly_anomalies": anomalies_detected,
    }


if __name__ == "__main__":
    res = detect_izsu_and_gediz_anomalies()
    print(json.dumps(res["november_2025_regime_shift"], ensure_ascii=False, indent=2))
