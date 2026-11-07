"""WBS-3 ML Downscaler, GroupKFold, SHAP, Backtest ve KMeans Testleri (`test_ml_engine.py`)."""

from __future__ import annotations

from ekozeka26.data_pipeline import PROCESSED_DIR
from ekozeka26.ml_engine import (
    explain_basin_summer_peak_shap,
    train_and_evaluate_models,
)
from ekozeka26.risk_index import find_basin_by_coords


def test_xgboost_downscaler_groupkfold_and_backtest() -> None:
    metrics = train_and_evaluate_models()
    assert (PROCESSED_DIR / "xgb_downscaler.json").exists()
    assert (PROCESSED_DIR / "model_metrics.json").exists()

    assert metrics["sample_size_rows"] == 1392
    assert metrics["unique_basins"] == 116

    mc = metrics["models_comparison"]
    naive_mae = mc["naive_coarse_annual"]["mae"]
    ridge_mae = mc["ridge_linear_regression"]["mae"]
    xgb_mae = mc["xgboost_downscaler"]["mae"]
    xgb_r2 = mc["xgboost_downscaler"]["r2"]

    # XGBoost hem Naive hem de Ridge regresyondan anlamlı biçimde üstün olmalı
    assert xgb_mae < ridge_mae < naive_mae
    assert xgb_r2 > 0.78
    assert xgb_mae < 0.18

    # Gediz 1984-2025 hidrolojik backtest
    bt = metrics["gediz_hydrological_backtest_1984_2025"]
    assert bt["total_months"] == 504
    assert bt["xgb_test_r2"] > 0.55
    assert bt["xgb_test_r2"] > bt["naive_test_r2"]

    # KMeans 5 arketip
    km = metrics["kmeans_basin_archetypes"]
    assert km["n_clusters"] == 5
    assert km["total_polygons"] == 639


def test_shap_latency_and_drivers() -> None:
    hit = find_basin_by_coords(38.4622, 27.4285)
    explanation = explain_basin_summer_peak_shap(hit["basin_row"], month=8)
    assert explanation["inference_latency_ms"] < 50.0
    assert len(explanation["top_drivers"]) == 7
    assert explanation["predicted_summer_peak_bws_raw"] >= 0.0
