"""WBS-2 Kuraklık İndeksi (SPI-3/12 & SPEI-3/12) Testleri (`test_drought_index.py`)."""

from __future__ import annotations

import pandas as pd

from ekozeka26.data_pipeline import PROCESSED_DIR
from ekozeka26.drought_index import build_drought_indices, classify_drought_index


def test_spi_and_spei_series_and_historical_droughts() -> None:
    df, summary = build_drought_indices()
    parquet_path = PROCESSED_DIR / "drought_indices.parquet"
    assert parquet_path.exists()

    loaded = pd.read_parquet(parquet_path)
    assert len(loaded) == len(df)
    for col in ["spi_3", "spi_12", "spei_3", "spei_12", "drought_class_spei12"]:
        assert col in loaded.columns

    # İndeks sınırları [-3.5, +3.5] aralığında olmalı
    valid_spei = loaded["spei_12"].dropna()
    assert valid_spei.min() >= -3.5
    assert valid_spei.max() <= 3.5

    # 2025 Türkiye rekor kuraklık yılı negatif SPEI-12 göstermeli
    assert summary["drought_2025_min_spei12"] < -0.8
    assert classify_drought_index(-2.1) == "Aşırı Kurak (Extreme Drought)"
    assert classify_drought_index(-1.6) == "Şiddetli Kurak (Severe Drought)"
