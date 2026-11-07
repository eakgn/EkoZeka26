"""WBS-3 Şeffaf Bileşik Risk İndeksi ve Coğrafi Sınır Koruması Testleri (`test_risk_index.py`)."""

from __future__ import annotations

from ekozeka26.risk_index import (
    compare_candidate_osbs,
    compute_transparent_risk,
    find_basin_by_coords,
)


def test_transparent_risk_score_and_component_sum() -> None:
    hit = find_basin_by_coords(38.4622, 27.4285)  # İzmir Kemalpaşa OSB
    assert hit["inside_turkey"] is True
    assert hit["warning"] is None

    res = compute_transparent_risk(
        basin_row=hit["basin_row"],
        sector="textile",
        year=2050,
        scenario="BAU",
        groundwater_dependency_pct=100.0,
    )
    assert 0.0 <= res["composite_risk_score"] <= 100.0
    assert len(res["component_breakdown"]) == 5

    comp_sum = round(sum(c["points"] for c in res["component_breakdown"]), 1)
    assert abs(comp_sum - res["composite_risk_score"]) <= 0.2

    days = res["expected_cutback_days"]
    assert 0.0 <= days["p10"] <= days["p50"] <= days["p90"] <= 120.0


def test_geographic_boundary_guard_for_sea_and_outside_clicks() -> None:
    # Ege Denizi ortası (sakız adası / açık deniz)
    sea_hit = find_basin_by_coords(38.10, 25.20)
    assert sea_hit["inside_turkey"] is False
    assert sea_hit["warning"] is not None
    assert "dışında veya deniz üzerindedir" in sea_hit["warning"]
    assert "string_id" in sea_hit["basin_row"]


def test_candidate_osbs_comparison_and_ranking() -> None:
    comp = compare_candidate_osbs(
        osb_ids=["izmir_kemalpasa", "manisa_osb", "bursa_osb", "konya_osb", "kocaeli_gosb"],
        sector="textile",
        year=2050,
        scenario="BAU",
    )
    assert comp["candidate_count"] == 5
    assert comp["safest_osb"]["composite_risk_score"] <= comp["riskiest_osb"]["composite_risk_score"]
    assert "Yatırım için en güvenli bölge" in comp["recommendation_summary"]
