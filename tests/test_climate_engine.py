"""WBS-2 İklim Motoru Testleri (`test_climate_engine.py`)."""

from __future__ import annotations

import json
import numpy as np

from ekozeka26.climate_engine import (
    PROCESSED_DIR,
    build_osb_climate_projections,
    compute_hargreaves_et0,
    quantile_delta_mapping,
)


def test_hargreaves_et0_physical_bounds() -> None:
    # Kış ve yaz günleri için fiziksel anlamlılık kontrolü
    t_mean = np.array([6.0, 28.5])
    t_max = np.array([10.0, 35.0])
    t_min = np.array([2.0, 22.0])
    doy = np.array([15, 195])
    et0 = compute_hargreaves_et0(t_mean, t_max, t_min, lat_deg=38.45, day_of_year=doy)
    assert et0.shape == (2,)
    assert 0.5 < et0[0] < 3.0  # Ocak ayında düşük buharlaşma
    assert 5.0 < et0[1] < 9.5  # Temmuz ayında yüksek buharlaşma


def test_qdm_distributional_correction_and_short_series_fallback() -> None:
    rng = np.random.default_rng(42)
    obs = rng.normal(loc=18.0, scale=2.5, size=60)
    # Simülasyon +3°C sıcak yanlı (warm bias)
    sim_ref = obs + 3.0
    sim_proj = rng.normal(loc=22.5, scale=2.5, size=60)

    corr, method = quantile_delta_mapping(obs, sim_ref, sim_proj, variable="temp", min_samples_for_qdm=24)
    assert method == "QDM"
    # +3°C yanlılık kaldırıldığı için düzeltilmiş ortalama ~19.5°C civarında olmalı
    assert abs(float(np.mean(corr)) - (float(np.mean(sim_proj)) - 3.0)) < 0.6

    # Kısa seri (<24) olduğunda delta_change_fallback devreye girmeli
    short_corr, short_method = quantile_delta_mapping(obs[:5], sim_ref[:5], sim_proj[:10], variable="temp", min_samples_for_qdm=24)
    assert short_method == "delta_change_fallback"
    assert len(short_corr) == 10


def test_build_osb_climate_projections_ensemble_and_uncertainty() -> None:
    payload = build_osb_climate_projections()
    assert (PROCESSED_DIR / "climate_osb.json").exists()
    assert len(payload["ensemble_models"]) == 7
    assert "izmir_kemalpasa" in payload["osb_projections"]

    kemalpasa = payload["osb_projections"]["izmir_kemalpasa"]
    bau = kemalpasa["scenarios"]["BAU"]
    assert len(bau["years"]) == 25  # 2026..2050
    for p10, p50, p90 in zip(bau["water_balance_p10_mm"], bau["water_balance_p50_mm"], bau["water_balance_p90_mm"]):
        assert p10 <= p50 <= p90
    assert 50.0 <= bau["drying_agreement_pct"] <= 100.0
