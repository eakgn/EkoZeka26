"""WBS-4 ROI ve Portföy Optimizasyon Motoru Testleri (`test_roi_optimizer.py`)."""

from __future__ import annotations

import pytest

from ekozeka26.roi_optimizer import (
    compute_multiplicative_savings,
    export_simulation_to_csv,
    optimize_facility_roi,
)


def test_multiplicative_diminishing_returns_and_sectoral_cap() -> None:
    # Aynı proseste iki %50 tasarruflu önlem %100 değil, %75 tasarruf etmeli: 1 - (0.5 * 0.5) = 0.75
    fake_measures = [
        {"target_process": "process", "process_saving_rate": 0.50},
        {"target_process": "process", "process_saving_rate": 0.50},
    ]
    shares = {"cooling": 0.0, "process": 100.0, "boiler": 0.0, "domestic": 0.0}
    res = compute_multiplicative_savings(fake_measures, shares, max_sectoral_cap=0.78)
    assert abs(res["process_saving_rates"]["process"] - 0.75) < 1e-4
    assert abs(res["total_saving_pct"] - 75.0) < 1e-2

    # 3. önlem eklendiğinde (%50) proses içi 0.875 olur ama sektörel tavan %78'de kırpmalı!
    fake_measures.append({"target_process": "process", "process_saving_rate": 0.50})
    res_capped = compute_multiplicative_savings(fake_measures, shares, max_sectoral_cap=0.78)
    assert res_capped["total_saving_rate"] == 0.78
    assert res_capped["total_saving_pct"] == 78.0
    assert res_capped["was_capped_at_sectoral_limit"] is True


def test_knapsack_budget_constraint_and_kemalpasa_textile_scenario() -> None:
    sim = optimize_facility_roi(
        osb_id="izmir_kemalpasa",
        sector="textile",
        annual_water_m3=150000,
        water_source="izsu_grid",
        daily_downtime_cost_tl=750000,
        capex_budget_tl=3500000,
        target_year=2030,
        scenario="BAU",
    )
    opt = sim["optimized_portfolio"]
    assert 0 < opt["total_capex_tl"] <= 3500000
    assert opt["selected_measures_count"] >= 3
    assert opt["annual_water_saved_m3"] > 25000
    assert opt["npv_5yr_tl"] > 0
    assert 0 < opt["payback_months"] < 36
    assert sim["certification_2029"]["compliant_with_2029_green_mandate"] is True

    csv_str = export_simulation_to_csv(sim)
    assert "AquaSanayi AI" in csv_str
    assert "27.12.2029 Belge Kademesi" in csv_str


def test_groundwater_well_vs_grid_economics() -> None:
    sim_grid = optimize_facility_roi(
        osb_id="izmir_kemalpasa",
        sector="textile",
        annual_water_m3=150000,
        water_source="izsu_grid",
        daily_downtime_cost_tl=750000,
        capex_budget_tl=3500000,
    )
    sim_well = optimize_facility_roi(
        osb_id="izmir_kemalpasa",
        sector="textile",
        annual_water_m3=150000,
        water_source="groundwater_well",
        daily_downtime_cost_tl=750000,
        capex_budget_tl=3500000,
    )
    # Kuyu suyunda birim su faturası düşük ama kuraklıkta kesinti günü ve üretim duruşu zararı daha yüksek olmalı
    assert sim_well["do_nothing_projection"]["annual_water_bill_tl"] < sim_grid["do_nothing_projection"]["annual_water_bill_tl"]
    assert (
        sim_well["do_nothing_projection"]["expected_downtime_loss_tl"]["p50"]
        > sim_grid["do_nothing_projection"]["expected_downtime_loss_tl"]["p50"]
    )


def test_edge_cases_low_budget_and_invalid_inputs() -> None:
    # Çok düşük bütçe (100.000 TL) çökmemeli, low_budget_advisory döndürmeli
    sim_low = optimize_facility_roi(capex_budget_tl=100000)
    assert sim_low["optimized_portfolio"]["selected_measures_count"] == 0
    assert sim_low["optimized_portfolio"]["low_budget_advisory"] is not None

    with pytest.raises(ValueError):
        optimize_facility_roi(annual_water_m3=0)
    with pytest.raises(ValueError):
        optimize_facility_roi(capex_budget_tl=-500)
