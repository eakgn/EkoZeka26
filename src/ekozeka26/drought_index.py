"""
WBS-2: Standartlaştırılmış Yağış (SPI-3/12) ve Yağış-Evapotranspirasyon (SPEI-3/12)
Kuraklık İndeksi Motoru (`drought_index.py`).

Metodolojik Dayanaklar:
- SPI-3 ve SPI-12: McKee, Doesken & Kleist (1993), 8th Conf. on Applied Climatology (Gamma dağılımı).
- SPEI-3 ve SPEI-12: Vicente-Serrano, Beguería & López-Moreno (2010), Journal of Climate 23(7)
  (Su dengesi D = P - ET₀ üzerinde 3-parametreli Log-Logistic / Fisk dağılımı -> Standart Normal Z dönüşümü).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

from ekozeka26.climate_engine import load_reference_era5_and_cmip6
from ekozeka26.data_pipeline import PROCESSED_DIR


def classify_drought_index(z_val: float) -> str:
    """WMO / McKee (1993) & Vicente-Serrano (2010) kuraklık şiddet sınıflandırması."""
    if np.isnan(z_val):
        return "Veri Yok"
    if z_val <= -2.0:
        return "Aşırı Kurak (Extreme Drought)"
    if z_val <= -1.5:
        return "Şiddetli Kurak (Severe Drought)"
    if z_val <= -1.0:
        return "Orta Kurak (Moderate Drought)"
    if z_val <= -0.5:
        return "Hafif Kurak (Mild Drought)"
    if z_val < 1.0:
        return "Normal"
    return "Nemli (Wet)"


def compute_spi_series(
    monthly_df: pd.DataFrame,
    precip_col: str = "precip_mm",
    scale_months: int = 12,
    ref_end_year: int = 2025,
) -> np.ndarray:
    """
    Aylık yağış serisinden k-aylık (örn. 3 veya 12) hareketli toplamlar üzerinden
    ay bazında Gamma dağılımı (sıfır yağış olasılığı q düzeltmeli) ile SPI hesaplar.
    """
    df = monthly_df.sort_values(["year", "month"]).reset_index(drop=True)
    rolled = df[precip_col].rolling(window=scale_months, min_periods=scale_months).sum().to_numpy()
    months = df["month"].to_numpy()
    years = df["year"].to_numpy()
    spi = np.full(len(df), np.nan, dtype=float)

    for m in range(1, 13):
        mask_all = (months == m) & (~np.isnan(rolled))
        mask_ref = mask_all & (years <= ref_end_year)
        ref_vals = rolled[mask_ref] if np.sum(mask_ref) >= 15 else rolled[mask_all]
        if len(ref_vals) < 8:
            continue

        zero_prob = float(np.mean(ref_vals <= 0.01))
        pos_ref = ref_vals[ref_vals > 0.01]
        if len(pos_ref) < 5 or np.std(pos_ref) < 1e-6:
            mu = float(np.mean(ref_vals))
            sd = max(float(np.std(ref_vals)), 1.0)
            z = (rolled[mask_all] - mu) / sd
            spi[mask_all] = np.clip(z, -3.5, 3.5)
            continue

        try:
            shape_a, loc_g, scale_g = stats.gamma.fit(pos_ref, floc=0.0)
            target_vals = rolled[mask_all]
            cdf_gamma = stats.gamma.cdf(np.maximum(0.01, target_vals), shape_a, loc=loc_g, scale=scale_g)
            prob = zero_prob + (1.0 - zero_prob) * cdf_gamma
            prob = np.where(target_vals <= 0.01, zero_prob / 2.0, prob)
            prob = np.clip(prob, 0.0005, 0.9995)
            spi[mask_all] = np.clip(stats.norm.ppf(prob), -3.5, 3.5)
        except Exception:
            mu = float(np.mean(ref_vals))
            sd = max(float(np.std(ref_vals)), 1.0)
            spi[mask_all] = np.clip((rolled[mask_all] - mu) / sd, -3.5, 3.5)

    return np.round(spi, 4)


def compute_spei_series(
    monthly_df: pd.DataFrame,
    wb_col: str = "water_balance_mm",
    scale_months: int = 12,
    ref_end_year: int = 2025,
) -> np.ndarray:
    """
    Vicente-Serrano vd. (2010) standardına göre k-aylık (3 veya 12) kümülatif iklimsel su dengesi
    (D = P - ET₀) üzerine 3-parametreli Log-Logistic (`scipy.stats.fisk`) dağılımı uydurarak
    SPEI-3 / SPEI-12 serisini hesaplar.
    """
    df = monthly_df.sort_values(["year", "month"]).reset_index(drop=True)
    rolled = df[wb_col].rolling(window=scale_months, min_periods=scale_months).sum().to_numpy()
    months = df["month"].to_numpy()
    years = df["year"].to_numpy()
    spei = np.full(len(df), np.nan, dtype=float)

    for m in range(1, 13):
        mask_all = (months == m) & (~np.isnan(rolled))
        mask_ref = mask_all & (years <= ref_end_year)
        ref_vals = rolled[mask_ref] if np.sum(mask_ref) >= 15 else rolled[mask_all]
        if len(ref_vals) < 8:
            continue

        all_vals = rolled[mask_all]
        # Log-logistic (fisk) pozitif destek gerektirdiği için güvenli kaydırma (shift) uygula
        shift = min(float(np.min(ref_vals)), float(np.min(all_vals))) - 25.0
        shifted_ref = ref_vals - shift
        shifted_all = all_vals - shift

        try:
            c_param, loc_param, scale_param = stats.fisk.fit(shifted_ref, floc=0.0)
            cdf = stats.fisk.cdf(shifted_all, c_param, loc=loc_param, scale=scale_param)
            cdf = np.clip(cdf, 0.0005, 0.9995)
            spei[mask_all] = np.clip(stats.norm.ppf(cdf), -3.5, 3.5)
        except Exception:
            mu = float(np.mean(ref_vals))
            sd = max(float(np.std(ref_vals)), 1.0)
            spei[mask_all] = np.clip((all_vals - mu) / sd, -3.5, 3.5)

    return np.round(spei, 4)


def build_drought_indices() -> tuple[pd.DataFrame, dict[str, Any]]:
    """
    1940–2025 ERA5 gözlemi ve 2026–2050 QDM-kalibreli CMIP6 serisi üzerinde
    SPI-3, SPI-12, SPEI-3, SPEI-12 indekslerini, kuraklık sınıflarını, on-yıllık trend eğimini
    ve 2021/2024/2025 kurak yıllarının tarihsel doğrulamasını üretip
    `data/processed/drought_indices.parquet` dosyasına yazar.
    """
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    era5_m, cmip_m, _ = load_reference_era5_and_cmip6(lat_deg=38.45)

    hist = era5_m[["year", "month", "precip_mm", "temp_mean_c", "et0_mm", "water_balance_mm"]].copy()
    hist["period"] = "historical_era5"

    proj = cmip_m[cmip_m["year"] >= 2026][
        ["year", "month", "precip_qdm_mm", "temp_qdm_c", "et0_qdm_mm", "water_balance_qdm_mm"]
    ].copy()
    proj = proj.rename(
        columns={
            "precip_qdm_mm": "precip_mm",
            "temp_qdm_c": "temp_mean_c",
            "et0_qdm_mm": "et0_mm",
            "water_balance_qdm_mm": "water_balance_mm",
        }
    )
    proj["period"] = "projected_cmip6_qdm"

    full_df = pd.concat([hist, proj], ignore_index=True).sort_values(["year", "month"]).reset_index(drop=True)
    full_df["spi_3"] = compute_spi_series(full_df, precip_col="precip_mm", scale_months=3, ref_end_year=2025)
    full_df["spi_12"] = compute_spi_series(full_df, precip_col="precip_mm", scale_months=12, ref_end_year=2025)
    full_df["spei_3"] = compute_spei_series(full_df, wb_col="water_balance_mm", scale_months=3, ref_end_year=2025)
    full_df["spei_12"] = compute_spei_series(full_df, wb_col="water_balance_mm", scale_months=12, ref_end_year=2025)
    full_df["drought_class_spei12"] = [classify_drought_index(v) for v in full_df["spei_12"]]

    out_parquet = PROCESSED_DIR / "drought_indices.parquet"
    full_df.to_parquet(out_parquet, index=False)

    # Trend ve tarihsel doğrulama özeti (1980-2025 ve 2000-2050)
    recent_df = full_df[(full_df["year"] >= 1980) & (full_df["year"] <= 2025)].dropna(subset=["spei_12"])
    t_years = recent_df["year"] + (recent_df["month"] - 0.5) / 12.0
    spei12_slope_decade = float(np.polyfit(t_years, recent_df["spei_12"], 1)[0] * 10.0)

    drought_2025_min_spei12 = float(full_df[full_df["year"] == 2025]["spei_12"].min())
    drought_2024_min_spei12 = float(full_df[full_df["year"] == 2024]["spei_12"].min())
    proj_2050_mean_spei12 = float(full_df[full_df["year"] >= 2045]["spei_12"].mean())

    summary = {
        "total_months": len(full_df),
        "spei12_trend_per_decade_1980_2025": round(spei12_slope_decade, 3),
        "drought_2024_min_spei12": round(drought_2024_min_spei12, 3),
        "drought_2025_min_spei12": round(drought_2025_min_spei12, 3),
        "drought_2025_class": classify_drought_index(drought_2025_min_spei12),
        "projected_2045_2050_mean_spei12": round(proj_2050_mean_spei12, 3),
    }
    return full_df, summary


if __name__ == "__main__":
    _, stats_summary = build_drought_indices()
    print(stats_summary)
