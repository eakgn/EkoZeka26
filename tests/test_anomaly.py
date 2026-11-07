"""WBS-3 İZSU & Gediz Hidrolojik Anomali Tespiti Testleri (`test_anomaly.py`)."""

from __future__ import annotations

from ekozeka26.anomaly import detect_izsu_and_gediz_anomalies


def test_izsu_monthly_isolation_forest_and_23d_dam_delta() -> None:
    res = detect_izsu_and_gediz_anomalies()
    assert res["monthly_records_analyzed"] == 137
    assert res["facilities_count"] >= 11

    nov = res["november_2025_regime_shift"]
    assert nov["month"] == "2025-11"
    # Tahtalı üretimi Ağustos 2025 pikinde 6.91 Mm³'ten Kasım 2025'te 1.62 Mm³'e (-%76.5) çökmeli
    assert abs(nov["tahtali_peak_aug_2025_mm3"] - 6.91) < 0.05
    assert abs(nov["tahtali_nov_2025_mm3"] - 1.62) < 0.05
    assert abs(nov["tahtali_collapse_pct"] - (-76.5)) < 0.2
    assert nov["well_share_nov_2025_pct"] > 62.0
    assert nov["is_flagged_anomaly"] is True

    # 23 günlük baraj kesit farkında Balçova Barajı -7.43 puan düşüş uyarısı üretmeli
    alerts = res["snapshot_23d_dam_alerts"]
    balcova_alerts = [a for a in alerts if "Balçova" in a["dam_name"]]
    assert len(balcova_alerts) == 1
    assert abs(balcova_alerts[0]["delta_23d_pct_points"] - (-7.43)) < 0.05
