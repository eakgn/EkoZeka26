"""WBS-5 FastAPI Backend ve Gemini/Fallback Ajanı Testleri (`test_api.py`)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from ekozeka26.app import app

client = TestClient(app)


def test_all_rest_endpoints_200_ok_and_fast_fallback() -> None:
    # 0. Ana Sayfa (2 sekmeli Web UI)
    r_ui = client.get("/")
    assert r_ui.status_code == 200
    html_text = r_ui.text
    assert "AquaSanayi AI" in html_text
    assert "1. Yatırım & Yer Seçimi" in html_text
    assert "2. Mevcut Fabrika ROI & 2029 Yeşil Belge Simülatörü" in html_text
    assert "CarbonEmit" not in html_text  # Ticari platform bağımsızlığı kuralı

    # 1. /api/health
    r_health = client.get("/api/health")
    assert r_health.status_code == 200
    assert r_health.json()["turkey_basins_count"] == 639

    # 2. /api/basins
    r_basins = client.get("/api/basins?sector=textile&year=2050&scenario=BAU")
    assert r_basins.status_code == 200
    b_data = r_basins.json()
    assert b_data["metadata"]["polygon_count"] == 639
    assert len(b_data["osb_markers"]) >= 10

    # 3. /api/osb-compare
    r_comp = client.get("/api/osb-compare?sector=textile&year=2050&scenario=BAU")
    assert r_comp.status_code == 200
    c_data = r_comp.json()
    assert c_data["candidate_count"] >= 4
    assert "safest_osb" in c_data

    # 4. /api/predict-location (hem OSB hem deniz tıklaması koruması)
    r_pred = client.post(
        "/api/predict-location",
        json={"osb_id": "izmir_kemalpasa", "sector": "textile", "year": 2050, "scenario": "BAU"},
    )
    assert r_pred.status_code == 200
    p_data = r_pred.json()
    assert p_data["inside_turkey"] is True
    assert p_data["xgboost_shap_explanation"]["inference_latency_ms"] < 50.0

    r_sea = client.post(
        "/api/predict-location",
        json={"lat": 38.10, "lon": 25.20, "sector": "textile", "year": 2050, "scenario": "BAU"},
    )
    assert r_sea.status_code == 200
    assert r_sea.json()["inside_turkey"] is False
    assert r_sea.json()["boundary_warning"] is not None

    # 5. /api/simulate-roi
    r_sim = client.post(
        "/api/simulate-roi",
        json={
            "facility_name": "Test Tekstil A.Ş.",
            "osb_id": "izmir_kemalpasa",
            "sector": "textile",
            "annual_water_m3": 150000,
            "water_source": "izsu_grid",
            "daily_downtime_cost_tl": 750000,
            "capex_budget_tl": 3500000,
            "target_year": 2030,
            "scenario": "BAU",
        },
    )
    assert r_sim.status_code == 200
    sim_data = r_sim.json()
    assert sim_data["optimized_portfolio"]["total_capex_tl"] <= 3500000
    assert sim_data["executive_summary"]["latency_ms"] < 100.0

    # 6. /api/executive-summary (offline fallback <100 ms)
    r_exec = client.post(
        "/api/executive-summary",
        json={"simulation_result": sim_data, "prefer_online_llm": False},
    )
    assert r_exec.status_code == 200
    exec_data = r_exec.json()
    assert exec_data["latency_ms"] < 100.0
    assert "Yönetici Özeti" in exec_data["markdown_report"]

    # 7. /api/izsu-live
    r_izsu = client.get("/api/izsu-live")
    assert r_izsu.status_code == 200
    izsu_data = r_izsu.json()
    assert abs(izsu_data["headline_metrics"]["capacity_weighted_occupancy_pct"] - 34.01) < 0.1
    assert izsu_data["anomaly_analysis"]["november_2025_regime_shift"]["is_flagged_anomaly"] is True

    # 8. /api/facility-sample
    r_sample = client.get("/api/facility-sample?profile_id=kemalpasa_textile")
    assert r_sample.status_code == 200
    assert r_sample.json()["facility_data"]["annual_water_m3"] == 150000

    # 9. /api/export/json & /api/export/csv
    r_exp_json = client.get("/api/export/json?osb_id=izmir_kemalpasa")
    assert r_exp_json.status_code == 200
    assert "optimized_portfolio" in r_exp_json.json()

    r_exp_csv = client.get("/api/export/csv?osb_id=izmir_kemalpasa")
    assert r_exp_csv.status_code == 200
    assert "AquaSanayi AI" in r_exp_csv.text

    # 10. Geçersiz girdi koruması (annual_water_m3 <= 0 -> 422)
    r_bad = client.post("/api/simulate-roi", json={"annual_water_m3": -10, "capex_budget_tl": 100000})
    assert r_bad.status_code == 422
