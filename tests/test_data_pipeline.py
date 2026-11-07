"""WBS-1 Birim ve Doğrulama Testleri (`test_data_pipeline.py`)."""

from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import pandas as pd

from ekozeka26.data_pipeline import (
    PROCESSED_DIR,
    RAW_DIR,
    run_pipeline,
)


def test_wbs1_pipeline_outputs_and_vv_rules() -> None:
    summary = run_pipeline(offline=True)

    # 1. 639 Türkiye poligonu ve tekil string_id kuralı
    assert summary["basin_polygon_count"] == 639
    assert summary["unique_string_id_count"] == 639
    assert summary["unique_pfaf_id_count"] == 116  # -9999 olanlar en yakın geçerli pfaf_id ile eşlendi

    # 2. GeoJSON boyutu < 5 MB kuralı
    geojson_path = PROCESSED_DIR / "turkey_basins.geojson"
    parquet_path = PROCESSED_DIR / "turkey_basins.parquet"
    assert geojson_path.exists()
    assert parquet_path.exists()
    assert summary["geojson_size_mb"] < 5.0

    # 3. Eksik (-9999) değer kalmaması ve m:1 join doğrulaması
    df = pd.read_parquet(parquet_path)
    assert len(df) == 639
    assert df["string_id"].nunique() == 639
    for col in ["bws_raw", "bwd_raw", "gtd_raw", "drr_raw", "bau30_ws_x_r", "bau50_ws_x_r", "summer_bws_raw"]:
        assert col in df.columns
        assert (df[col] <= -999).sum() == 0, f"{col} içinde -9999 benzeri eksik değer kaldı!"
        # Aqueduct +9999 "veri yok" işaretidir; temizlenmezse UI'da ws=9999.00 görünür.
        assert (df[col] == 9999).sum() == 0, f"{col} içinde 9999 sentinel değeri kaldı!"
        assert (df[col] >= 9999).sum() == 0, f"{col} içinde 9999 ve üzeri geçersiz değer var!"
        assert df[col].isna().sum() == 0, f"{col} içinde NaN değer kaldı!"

    # 4. İZSU gerçek veri doğrulaması (137 aylık kayıt, %34.0 ağırlıklı doluluk, Balçova -7.43 puan)
    izsu_path = PROCESSED_DIR / "izsu_snapshot.json"
    assert izsu_path.exists()
    izsu = json.loads(izsu_path.read_text(encoding="utf-8"))
    assert izsu["monthly_production_2025_count"] == 137
    assert abs(izsu["headline_metrics"]["capacity_weighted_occupancy_pct"] - 34.01) < 0.1
    assert abs(izsu["headline_metrics"]["balcova_23d_drop_pct_points"] - (-7.43)) < 0.05
    assert abs(izsu["tariffs_2026"]["tier_21_plus_tl_m3"] - 403.79) < 0.01

    # 5. 12 SYGM/IFC önlemi ve OSB profilleri
    measures = json.loads((PROCESSED_DIR / "measures_catalog.json").read_text(encoding="utf-8"))
    assert len(measures["measures"]) == 12
    assert measures["max_sectoral_saving_cap"] == 0.78

    osbs = json.loads((PROCESSED_DIR / "osb_profiles.json").read_text(encoding="utf-8"))
    assert len(osbs["osbs"]) >= 10
    assert "tofas_bursa" in osbs["sample_facilities"]
    assert len(osbs["sample_facilities"]) == 3

    # 6. data/raw/ içinde 250 MB aq.zip olmamalı
    assert not (RAW_DIR / "aq.zip").exists()
