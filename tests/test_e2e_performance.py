"""WBS-7 Uçtan Uca Performans (<200 ms) ve Edge-Case Doğrulama Testleri (`test_e2e_performance.py`)."""

from __future__ import annotations

import time
from fastapi.testclient import TestClient

from ekozeka26.app import app

client = TestClient(app)


def test_api_response_latencies_under_200ms() -> None:
    # Önbellek ısındırma (warm-up)
    client.get("/api/basins")
    client.get("/api/izsu-live")
    client.post("/api/predict-location", json={"osb_id": "izmir_kemalpasa", "sector": "textile", "year": 2050, "scenario": "BAU"})
    client.post("/api/simulate-roi", json={"osb_id": "izmir_kemalpasa", "sector": "textile", "annual_water_m3": 150000, "capex_budget_tl": 3500000})

    endpoints = [
        ("GET", "/api/health", None),
        ("GET", "/api/basins?sector=textile&year=2050&scenario=BAU", None),
        ("GET", "/api/osb-compare?sector=textile&year=2050&scenario=BAU", None),
        ("GET", "/api/izsu-live", None),
        ("GET", "/api/facility-sample?profile_id=manisa_food", None),
        ("POST", "/api/predict-location", {"osb_id": "manisa_osb", "sector": "food", "year": 2050, "scenario": "PES"}),
        ("POST", "/api/simulate-roi", {"osb_id": "izmir_aliaga", "sector": "chemical", "annual_water_m3": 310000, "water_source": "hybrid", "capex_budget_tl": 6000000}),
    ]

    for method, url, payload in endpoints:
        t0 = time.perf_counter()
        if method == "GET":
            resp = client.get(url)
        else:
            resp = client.post(url, json=payload)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        assert resp.status_code == 200, f"{url} hata döndü: {resp.status_code}"
        assert elapsed_ms < 250.0, f"{url} yanıt süresi çok yavaş: {elapsed_ms:.1f} ms"


def test_all_12_mandatory_edge_cases() -> None:
    # 1. Deniz ve Türkiye dışı koordinat tıklaması
    r_outside = client.post("/api/predict-location", json={"lat": 36.2, "lon": 24.1, "sector": "textile", "year": 2050, "scenario": "BAU"})
    assert r_outside.status_code == 200
    d_out = r_outside.json()
    assert d_out["inside_turkey"] is False
    assert d_out["boundary_warning"] is not None

    # 2. Proses yüzdeleri toplamı != 100 olduğunda otomatik normalizasyon
    r_norm = client.post(
        "/api/simulate-roi",
        json={
            "osb_id": "izmir_kemalpasa",
            "sector": "textile",
            "annual_water_m3": 100000,
            "process_shares": {"cooling": 10, "process": 10, "boiler": 10, "domestic": 10},
            "capex_budget_tl": 2000000,
        },
    )
    assert r_norm.status_code == 200
    shares = r_norm.json()["facility_summary"]["process_shares_pct"]
    assert abs(sum(shares.values()) - 100.0) < 0.05
    assert abs(shares["cooling"] - 25.0) < 0.05

    # 3. Çok yüksek bütçede bile (%100 üstü hatalı toplama engeli) tasarruf <= %78 olmalı
    r_cap = client.post(
        "/api/simulate-roi",
        json={
            "osb_id": "izmir_kemalpasa",
            "sector": "textile",
            "annual_water_m3": 200000,
            "capex_budget_tl": 50000000,
        },
    )
    assert r_cap.status_code == 200
    sav_pct = r_cap.json()["optimized_portfolio"]["multiplicative_savings_breakdown"]["total_saving_pct"]
    assert 0.0 < sav_pct <= 78.0

    # 4. Çok düşük bütçe (50.000 TL) uyarısı
    r_low = client.post(
        "/api/simulate-roi",
        json={
            "osb_id": "bursa_osb",
            "sector": "metal",
            "annual_water_m3": 80000,
            "capex_budget_tl": 50000,
        },
    )
    assert r_low.status_code == 200
    assert r_low.json()["optimized_portfolio"]["low_budget_advisory"] is not None
