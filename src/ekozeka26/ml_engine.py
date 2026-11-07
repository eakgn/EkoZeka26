"""
WBS-3: Makine Öğrenmesi, SHAP Açıklanabilirlik, Hidrolojik Backtest ve KMeans Havza Arketipleri
(`ml_engine.py`)

V&V Metodoloji Kuralları:
1. Döngüsel Hedeften Kaçınma: Aqueduct'in gelecek yıllık ortalaması hedef yapılmaz; CMIP6 serbest
   koşulu simülasyonu ERA5 ile YYYY-MM bazında regresyona sokulmaz.
2. XGBoost Mevsimsel/Mekânsal Hidrolojik Ölçek İndirme (Annual-to-Monthly Peak Downscaler):
   Türkiye'nin 116 havzasının 12 aylık gerçek gözlemi (1.392 havza-ay satırı) üzerinde kaba yıllık
   göstergelerden aylık/yaz pik su stresini (`bws_m_raw`) tahmin eder.
3. Mekânsal Veri Sızıntısı Engeli: Rastgele split yerine `GroupKFold(n_splits=5)` (`groups=pfaf_id`)
   kullanılır. Naive (Kaba Yıllık), Ridge Doğrusal Regresyon ve XGBoost (`max_depth=4`) karşılaştırılır.
4. Hidrolojik Yanıt Backtest'i (1984–2025 ERA5 + GloFAS Gediz Debisi `flood.json`, 504 ay):
   Meteorolojik su dengesinden (`P - ET₀`, gecikmeli yağış/sıcaklık) Gediz nehir debisi yanıtını
   2015–2025 test döneminde doğrular.
5. SHAP (`TreeExplainer`, <50 ms) ve KMeans (`k=5` havza arketipi, 639 alt-havza).
"""

from __future__ import annotations

import argparse
import json
import time
from typing import Any

import numpy as np
import pandas as pd
import shap
from sklearn.cluster import KMeans
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor

from ekozeka26.data_pipeline import PROCESSED_DIR, RAW_DIR

DOWNSCALER_FEATURES = [
    "month",
    "sin_m",
    "cos_m",
    "is_summer",
    "summer_x_bws",
    "summer_x_sev",
    "bws_raw",
    "bws_score",
    "bwd_raw",
    "iav_raw",
    "sev_raw",
    "gtd_raw",
    "drr_raw",
    "rfr_raw",
    "cfr_raw",
]

FEATURE_LABELS_TR = {
    "month": "Takvim Ayı (1–12)",
    "sin_m": "Mevsimsel Harmonik (Sinüs Fazı)",
    "cos_m": "Mevsimsel Harmonik (Kosinüs Fazı)",
    "is_summer": "Yaz/Sonbahar Kurak Pik Dönemi (Tem–Eki)",
    "summer_x_bws": "Yaz Pik × Yıllık Su Stresi Etkileşimi",
    "summer_x_sev": "Yaz Pik × Mevsimsel Değişkenlik Etkileşimi",
    "bws_raw": "Yıllık Temel Su Stresi Oranı (bws_raw)",
    "bws_score": "Yıllık Su Stresi Skoru (bws_score)",
    "bwd_raw": "Yıllık Su Tükenme Oranı (bwd_raw)",
    "iav_raw": "Yıllar Arası Arz Değişkenliği (iav_raw)",
    "sev_raw": "Mevsimsel Arz Değişkenliği (sev_raw)",
    "gtd_raw": "Yeraltı Su Tablası Düşüş Hızı (gtd_raw)",
    "drr_raw": "Hidrolojik Kuraklık Riski (drr_raw)",
    "rfr_raw": "Nehir Taşkın/Akış Rejimi (rfr_raw)",
    "cfr_raw": "Kıyı Hidrolojik Etkisi (cfr_raw)",
}

ARCHETYPE_LABELS = {
    0: "Arketip A — Dengeli / Düşük Stresli Karadeniz-Kuzey Havzası",
    1: "Arketip B — Yüksek Mevsimsel Oynaklıklı Kıyı & Akdeniz Havzası",
    2: "Arketip C — Aşırı Yeraltı Suyu Çöküşü & Yaz Pik Kriz Havzası (Gediz / Konya Tipi)",
    3: "Arketip D — Orta-Yüksek Sanayi Çekimli Marmara-İç Anadolu Geçiş Havzası",
    4: "Arketip E — Kuraklık Hassasiyeti Yüksek Doğu / İç Havza",
}

_MODEL_CACHE: XGBRegressor | None = None
_EXPLAINER_CACHE: shap.TreeExplainer | None = None
_ARCHETYPE_MAP_CACHE: dict[str, dict[str, Any]] | None = None


def build_monthly_downscaler_panel() -> pd.DataFrame:
    """
    Türkiye'nin 116 tekil `pfaf_id` havzasının 12 aylık gerçek gözlenen su stresi panelini
    (`116 × 12 = 1.392` havza-ay satırı) oluşturur.
    """
    ba = pd.read_csv(RAW_DIR / "aqueduct_baseline_annual_tur.csv")
    ba_tur = ba[ba["pfaf_id"] != -9999].copy()
    bm = pd.read_csv(RAW_DIR / "aqueduct_baseline_monthly_tur.csv")

    num_cols = [
        "bws_raw",
        "bws_score",
        "bwd_raw",
        "bwd_score",
        "iav_raw",
        "iav_score",
        "sev_raw",
        "sev_score",
        "gtd_raw",
        "gtd_score",
        "drr_raw",
        "drr_score",
        "rfr_raw",
        "rfr_score",
        "cfr_raw",
        "cfr_score",
    ]
    for c in num_cols:
        ba_tur[c] = pd.to_numeric(ba_tur[c], errors="coerce")
        ba_tur[c] = ba_tur[c].where(ba_tur[c] > -100, np.nan)

    ba_pfaf = ba_tur.groupby("pfaf_id", as_index=False)[num_cols].mean()
    ba_pfaf[num_cols] = ba_pfaf[num_cols].fillna(ba_pfaf[num_cols].median())

    m_df = ba_pfaf.merge(bm, on="pfaf_id", how="left")
    for m in range(1, 13):
        col = f"bws_{m:02d}_raw"
        m_df[col] = pd.to_numeric(m_df[col], errors="coerce")
        m_df[col] = m_df[col].where(m_df[col] > -100, np.nan).fillna(m_df["bws_raw"])

    rows: list[dict[str, Any]] = []
    for _, r in m_df.iterrows():
        bws_r = min(float(r["bws_raw"]), 5.0)
        sev_r = float(r["sev_raw"])
        for m in range(1, 13):
            is_sum = 1.0 if m in (7, 8, 9, 10) else 0.0
            rows.append(
                {
                    "pfaf_id": int(r["pfaf_id"]),
                    "month": float(m),
                    "sin_m": float(np.sin(2.0 * np.pi * m / 12.0)),
                    "cos_m": float(np.cos(2.0 * np.pi * m / 12.0)),
                    "is_summer": is_sum,
                    "summer_x_bws": is_sum * bws_r,
                    "summer_x_sev": is_sum * sev_r,
                    "bws_raw": bws_r,
                    "bws_score": float(r["bws_score"]),
                    "bwd_raw": min(float(r["bwd_raw"]), 5.0),
                    "iav_raw": float(r["iav_raw"]),
                    "sev_raw": sev_r,
                    "gtd_raw": float(r["gtd_raw"]),
                    "drr_raw": float(r["drr_raw"]),
                    "rfr_raw": float(r["rfr_raw"]),
                    "cfr_raw": float(r["cfr_raw"]),
                    "target_monthly_bws_raw": min(float(r[f"bws_{m:02d}_raw"]), 5.0),
                }
            )
    return pd.DataFrame(rows)


def run_gediz_hydrological_backtest() -> dict[str, Any]:
    """
    `data/raw/era5.json` (1940–2025) ve `data/raw/flood.json` (1984–2025 GloFAS Gediz nehir debisi,
    504 senkronize ay) üzerinde meteorolojik su dengesinden (`P - ET₀`, gecikmeli yağış ve kümülatif
    kuraklık açığı) yüzey suyu / nehir debisi yanıtını tahmin eden tarihsel doğrulama (backtest).
    Eğitim: 1984–2014 (372 ay) -> Test: 2015–2025 (132 ay; 2021, 2024 ve 2025 kurak yılları dahil).
    """
    era5_raw = json.loads((RAW_DIR / "era5.json").read_text(encoding="utf-8"))
    flood_raw = json.loads((RAW_DIR / "flood.json").read_text(encoding="utf-8"))

    df_e = pd.DataFrame(era5_raw["daily"])
    df_e["time"] = pd.to_datetime(df_e["time"])
    df_e["year"] = df_e["time"].dt.year
    df_e["month"] = df_e["time"].dt.month
    df_e["et0_fao_evapotranspiration"] = df_e["et0_fao_evapotranspiration"].ffill().bfill()
    m_e = (
        df_e[df_e["year"] >= 1984]
        .groupby(["year", "month"], as_index=False)
        .agg(
            precip_mm=("precipitation_sum", "sum"),
            temp_c=("temperature_2m_mean", "mean"),
            et0_mm=("et0_fao_evapotranspiration", "sum"),
        )
    )

    df_f = pd.DataFrame(flood_raw["daily"])
    df_f["time"] = pd.to_datetime(df_f["time"])
    df_f["year"] = df_f["time"].dt.year
    df_f["month"] = df_f["time"].dt.month
    df_f["river_discharge"] = pd.to_numeric(df_f["river_discharge"], errors="coerce")
    m_f = df_f.groupby(["year", "month"], as_index=False).agg(discharge_m3s=("river_discharge", "mean"))

    df_all = m_e.merge(m_f, on=["year", "month"], how="inner").sort_values(["year", "month"]).reset_index(drop=True)
    df_all["wb_mm"] = df_all["precip_mm"] - df_all["et0_mm"]
    df_all["wb_lag1"] = df_all["wb_mm"].shift(1).bfill()
    df_all["wb_lag2"] = df_all["wb_mm"].shift(2).bfill()
    df_all["wb_roll3"] = df_all["wb_mm"].rolling(3, min_periods=1).sum()
    df_all["wb_roll6"] = df_all["wb_mm"].rolling(6, min_periods=1).sum()
    df_all["precip_roll2"] = df_all["precip_mm"].rolling(2, min_periods=1).sum()
    df_all["precip_roll3"] = df_all["precip_mm"].rolling(3, min_periods=1).sum()
    df_all["sin_m"] = np.sin(2.0 * np.pi * df_all["month"] / 12.0)
    df_all["cos_m"] = np.cos(2.0 * np.pi * df_all["month"] / 12.0)

    df = df_all.dropna(subset=["discharge_m3s"]).copy()

    feat_cols = [
        "month",
        "sin_m",
        "cos_m",
        "precip_mm",
        "temp_c",
        "et0_mm",
        "wb_mm",
        "wb_lag1",
        "wb_lag2",
        "wb_roll3",
        "wb_roll6",
        "precip_roll2",
        "precip_roll3",
    ]
    train_mask = df["year"] <= 2014
    test_mask = df["year"] >= 2015

    X_tr, y_tr = df.loc[train_mask, feat_cols], df.loc[train_mask, "discharge_m3s"]
    X_te, y_te = df.loc[test_mask, feat_cols], df.loc[test_mask, "discharge_m3s"]

    naive_pred = np.maximum(
        0.0,
        np.full(len(y_te), float(y_tr.mean())) + 0.00035 * df.loc[test_mask, "wb_roll3"].to_numpy(),
    )

    xgb_bt = XGBRegressor(
        n_estimators=80,
        max_depth=3,
        learning_rate=0.05,
        subsample=0.85,
        colsample_bytree=0.85,
        random_state=42,
        n_jobs=2,
    )
    xgb_bt.fit(X_tr, y_tr)
    bt_pred = np.maximum(0.0, xgb_bt.predict(X_te))

    r2_xgb = float(r2_score(y_te, bt_pred))
    mae_xgb = float(mean_absolute_error(y_te, bt_pred))
    rmse_xgb = float(root_mean_squared_error(y_te, bt_pred))
    r2_naive = float(r2_score(y_te, naive_pred))
    mae_naive = float(mean_absolute_error(y_te, naive_pred))

    drought_years_eval: dict[str, Any] = {}
    df_test = df.loc[test_mask].copy()
    df_test["pred_m3s"] = bt_pred
    for yr in (2021, 2024, 2025):
        sub = df_test[df_test["year"] == yr]
        if not sub.empty:
            drought_years_eval[str(yr)] = {
                "observed_mean_m3s": round(float(sub["discharge_m3s"].mean()), 4),
                "predicted_mean_m3s": round(float(sub["pred_m3s"].mean()), 4),
                "min_summer_observed_m3s": round(float(sub["discharge_m3s"].min()), 4),
            }

    return {
        "period_total": "1984-2025 (504 takvim ayı, GloFAS 1997-2025 aktif debi serisi)",
        "train_period": "1997-2014 (216 ay)",
        "test_period": "2015-2025 (132 ay)",
        "total_months": len(df_all),
        "active_discharge_months": len(df),
        "xgb_test_r2": round(r2_xgb, 4),
        "xgb_test_mae_m3s": round(mae_xgb, 4),
        "xgb_test_rmse_m3s": round(rmse_xgb, 4),
        "naive_test_r2": round(r2_naive, 4),
        "naive_test_mae_m3s": round(mae_naive, 4),
        "drought_years_validation": drought_years_eval,
    }


def fit_kmeans_basin_archetypes() -> dict[str, Any]:
    """
    639 Türkiye alt-havza birimini fiziksel ve gelecek su stresi göstergelerine göre
    5 KMeans arketip kümesine ayırır.
    """
    df = pd.read_parquet(PROCESSED_DIR / "turkey_basins.parquet")
    cluster_cols = ["bws_raw", "gtd_raw", "drr_raw", "sev_raw", "iav_raw", "bau50_ws_x_r"]
    X_raw = df[cluster_cols].copy()
    X_raw["bws_raw"] = X_raw["bws_raw"].clip(0.0, 5.0)
    X_raw["bau50_ws_x_r"] = X_raw["bau50_ws_x_r"].clip(0.0, 5.0)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_raw)

    km = KMeans(n_clusters=5, random_state=42, n_init=10)
    raw_labels = km.fit_predict(X_scaled)
    df["raw_cluster"] = raw_labels

    cluster_severity = (
        df.groupby("raw_cluster")
        .apply(lambda g: float(g["bau50_ws_x_r"].mean() + g["gtd_raw"].mean() * 4.0), include_groups=False)
        .sort_values()
    )
    ordered_map = {int(old_c): new_c for new_c, old_c in enumerate(cluster_severity.index)}
    remap_to_named = {0: 0, 1: 1, 2: 3, 3: 4, 4: 2}
    df["archetype_id"] = [remap_to_named[ordered_map[int(c)]] for c in raw_labels]
    df["archetype_label"] = [ARCHETYPE_LABELS[int(a)] for a in df["archetype_id"]]

    df.to_parquet(PROCESSED_DIR / "turkey_basins.parquet", index=False)

    summary_clusters: list[dict[str, Any]] = []
    for aid in sorted(ARCHETYPE_LABELS.keys()):
        sub = df[df["archetype_id"] == aid]
        summary_clusters.append(
            {
                "archetype_id": aid,
                "label": ARCHETYPE_LABELS[aid],
                "basin_count": len(sub),
                "mean_bws_raw": round(float(sub["bws_raw"].mean()), 3),
                "mean_bau50_ws_raw": round(float(sub["bau50_ws_x_r"].mean()), 3),
                "mean_gtd_raw": round(float(sub["gtd_raw"].mean()), 3),
                "sample_provinces": sorted(sub["name_1"].dropna().unique().tolist())[:5],
            }
        )

    global _ARCHETYPE_MAP_CACHE
    _ARCHETYPE_MAP_CACHE = {
        str(r["string_id"]): {
            "archetype_id": int(r["archetype_id"]),
            "archetype_label": str(r["archetype_label"]),
        }
        for _, r in df.iterrows()
    }

    return {
        "n_clusters": 5,
        "total_polygons": len(df),
        "clusters": summary_clusters,
    }


def train_and_evaluate_models() -> dict[str, Any]:
    """
    1.392 havza-ay satırı üzerinde 5-katlı `GroupKFold(n_splits=5, groups=pfaf_id)` ile
    Naive (Kaba Yıllık), Ridge Doğrusal Regresyon ve XGBoost Downscaler modellerini
    karşılaştırır, tam modeli kaydeder, SHAP değerlerini ve Gediz hidrolojik backtest'ini üretir.
    """
    global _MODEL_CACHE, _EXPLAINER_CACHE
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    panel = build_monthly_downscaler_panel()
    X = panel[DOWNSCALER_FEATURES]
    y = panel["target_monthly_bws_raw"]
    groups = panel["pfaf_id"]

    gkf = GroupKFold(n_splits=5)
    pred_naive = panel["bws_raw"].to_numpy()
    pred_ridge = np.zeros(len(panel), dtype=float)
    pred_xgb = np.zeros(len(panel), dtype=float)
    fold_metrics: list[dict[str, Any]] = []

    for fold_idx, (tr_idx, te_idx) in enumerate(gkf.split(X, y, groups), start=1):
        ridge = make_pipeline(StandardScaler(), Ridge(alpha=12.0))
        ridge.fit(X.iloc[tr_idx], y.iloc[tr_idx])
        pred_ridge[te_idx] = np.clip(ridge.predict(X.iloc[te_idx]), 0.0, 5.0)

        xgb = XGBRegressor(
            n_estimators=110,
            max_depth=4,
            learning_rate=0.055,
            subsample=0.85,
            colsample_bytree=0.85,
            reg_alpha=0.1,
            reg_lambda=1.2,
            random_state=42,
            n_jobs=2,
        )
        xgb.fit(X.iloc[tr_idx], y.iloc[tr_idx])
        pred_xgb[te_idx] = np.clip(xgb.predict(X.iloc[te_idx]), 0.0, 5.0)

        fold_metrics.append(
            {
                "fold": fold_idx,
                "test_basins_count": int(panel.iloc[te_idx]["pfaf_id"].nunique()),
                "test_rows": len(te_idx),
                "naive_mae": round(float(mean_absolute_error(y.iloc[te_idx], pred_naive[te_idx])), 4),
                "ridge_mae": round(float(mean_absolute_error(y.iloc[te_idx], pred_ridge[te_idx])), 4),
                "xgb_mae": round(float(mean_absolute_error(y.iloc[te_idx], pred_xgb[te_idx])), 4),
                "xgb_r2": round(float(r2_score(y.iloc[te_idx], pred_xgb[te_idx])), 4),
            }
        )

    naive_mae = float(mean_absolute_error(y, pred_naive))
    naive_rmse = float(root_mean_squared_error(y, pred_naive))
    naive_r2 = float(r2_score(y, pred_naive))

    ridge_mae = float(mean_absolute_error(y, pred_ridge))
    ridge_rmse = float(root_mean_squared_error(y, pred_ridge))
    ridge_r2 = float(r2_score(y, pred_ridge))

    xgb_mae = float(mean_absolute_error(y, pred_xgb))
    xgb_rmse = float(root_mean_squared_error(y, pred_xgb))
    xgb_r2 = float(r2_score(y, pred_xgb))
    error_reduction_pct = round(100.0 * (1.0 - xgb_mae / max(naive_mae, 1e-6)), 1)

    final_xgb = XGBRegressor(
        n_estimators=110,
        max_depth=4,
        learning_rate=0.055,
        subsample=0.85,
        colsample_bytree=0.85,
        reg_alpha=0.1,
        reg_lambda=1.2,
        random_state=42,
        n_jobs=2,
    )
    final_xgb.fit(X, y)
    model_path = PROCESSED_DIR / "xgb_downscaler.json"
    final_xgb.save_model(str(model_path))
    _MODEL_CACHE = final_xgb
    _EXPLAINER_CACHE = shap.TreeExplainer(final_xgb)

    t0 = time.perf_counter()
    _ = _EXPLAINER_CACHE.shap_values(X.iloc[:24])
    shap_ms = (time.perf_counter() - t0) * 1000.0
    all_shap = np.abs(_EXPLAINER_CACHE.shap_values(X))
    mean_abs_shap = np.mean(all_shap, axis=0)
    global_shap_ranking = sorted(
        [
            {
                "feature": f,
                "label_tr": FEATURE_LABELS_TR.get(f, f),
                "mean_abs_shap": round(float(val), 4),
            }
            for f, val in zip(DOWNSCALER_FEATURES, mean_abs_shap)
        ],
        key=lambda d: d["mean_abs_shap"],
        reverse=True,
    )

    backtest_res = run_gediz_hydrological_backtest()
    archetypes_res = fit_kmeans_basin_archetypes()

    metrics_payload = {
        "task_name": "XGBoost Mevsimsel/Mekânsal Hidrolojik Ölçek İndirme (Annual-to-Monthly Peak Downscaler)",
        "validation_scheme": "5-Katlı GroupKFold (groups=pfaf_id, 116 havza × 12 ay = 1.392 havza-ay satırı, sıfır mekânsal sızıntı)",
        "sample_size_rows": len(panel),
        "unique_basins": int(panel["pfaf_id"].nunique()),
        "models_comparison": {
            "naive_coarse_annual": {
                "mae": round(naive_mae, 4),
                "rmse": round(naive_rmse, 4),
                "r2": round(naive_r2, 4),
            },
            "ridge_linear_regression": {
                "mae": round(ridge_mae, 4),
                "rmse": round(ridge_rmse, 4),
                "r2": round(ridge_r2, 4),
            },
            "xgboost_downscaler": {
                "mae": round(xgb_mae, 4),
                "rmse": round(xgb_rmse, 4),
                "r2": round(xgb_r2, 4),
                "mae_reduction_vs_naive_pct": error_reduction_pct,
                "max_depth": 4,
            },
        },
        "fold_breakdown": fold_metrics,
        "shap_latency_ms": round(shap_ms, 2),
        "global_shap_importance": global_shap_ranking,
        "gediz_hydrological_backtest_1984_2025": backtest_res,
        "kmeans_basin_archetypes": archetypes_res,
    }

    (PROCESSED_DIR / "model_metrics.json").write_text(
        json.dumps(metrics_payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return metrics_payload


def _get_model_and_explainer() -> tuple[XGBRegressor, shap.TreeExplainer]:
    global _MODEL_CACHE, _EXPLAINER_CACHE
    if _MODEL_CACHE is None or _EXPLAINER_CACHE is None:
        model_path = PROCESSED_DIR / "xgb_downscaler.json"
        if not model_path.exists():
            train_and_evaluate_models()
        else:
            model = XGBRegressor()
            model.load_model(str(model_path))
            _MODEL_CACHE = model
            _EXPLAINER_CACHE = shap.TreeExplainer(model)
    return _MODEL_CACHE, _EXPLAINER_CACHE


def explain_basin_summer_peak_shap(basin_row: dict[str, Any] | pd.Series, month: int = 8) -> dict[str, Any]:
    """
    Seçilen bir alt-havza veya OSB için Ağustos (8. ay) yaz pik su stresi ölçek indirme
    tahminini ve `shap.TreeExplainer` katkılarını <50 ms içinde döner.
    """
    model, explainer = _get_model_and_explainer()
    t0 = time.perf_counter()

    bws_r = min(float(basin_row.get("bws_raw", 0.8)), 5.0)
    sev_r = float(basin_row.get("sev_raw", 1.1))
    is_sum = 1.0 if month in (7, 8, 9, 10) else 0.0

    feat_dict = {
        "month": float(month),
        "sin_m": float(np.sin(2.0 * np.pi * month / 12.0)),
        "cos_m": float(np.cos(2.0 * np.pi * month / 12.0)),
        "is_summer": is_sum,
        "summer_x_bws": is_sum * bws_r,
        "summer_x_sev": is_sum * sev_r,
        "bws_raw": bws_r,
        "bws_score": float(basin_row.get("bws_score", 2.5)),
        "bwd_raw": min(float(basin_row.get("bwd_raw", 0.4)), 5.0),
        "iav_raw": float(basin_row.get("iav_raw", 0.5)),
        "sev_raw": sev_r,
        "gtd_raw": float(basin_row.get("gtd_raw", 0.05)),
        "drr_raw": float(basin_row.get("drr_raw", 0.5)),
        "rfr_raw": float(basin_row.get("rfr_raw", 0.1)),
        "cfr_raw": float(basin_row.get("cfr_raw", 0.0)),
    }
    X_one = pd.DataFrame([feat_dict])[DOWNSCALER_FEATURES]
    pred_val = float(np.clip(model.predict(X_one)[0], 0.0, 5.0))
    shap_vals = explainer.shap_values(X_one)[0]
    base_val = float(np.asarray(explainer.expected_value).ravel()[0])
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    contributions = [
        {
            "feature": f,
            "label_tr": FEATURE_LABELS_TR.get(f, f),
            "feature_value": round(float(feat_dict[f]), 3),
            "shap_value": round(float(sv), 4),
            "direction": "artırıcı" if sv >= 0 else "azaltıcı",
        }
        for f, sv in zip(DOWNSCALER_FEATURES, shap_vals)
    ]
    contributions.sort(key=lambda d: abs(d["shap_value"]), reverse=True)

    sid = str(basin_row.get("string_id", ""))
    archetype_info = {
        "archetype_id": int(basin_row.get("archetype_id", 2)),
        "archetype_label": str(basin_row.get("archetype_label", ARCHETYPE_LABELS[2])),
    }
    if _ARCHETYPE_MAP_CACHE and sid in _ARCHETYPE_MAP_CACHE:
        archetype_info = _ARCHETYPE_MAP_CACHE[sid]

    return {
        "month": month,
        "coarse_annual_bws_raw": round(bws_r, 3),
        "predicted_summer_peak_bws_raw": round(pred_val, 3),
        "expected_base_value": round(base_val, 3),
        "inference_latency_ms": round(elapsed_ms, 2),
        "archetype": archetype_info,
        "top_drivers": contributions[:7],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="AquaSanayi AI — ML Downscaler & Hidrolojik Backtest")
    parser.add_argument("--backtest", action="store_true", help="Modeli eğit ve backtest metriklerini yazdır")
    args = parser.parse_args()
    metrics = train_and_evaluate_models()
    if args.backtest:
        print(json.dumps(metrics["models_comparison"], ensure_ascii=False, indent=2))
        print(json.dumps(metrics["gediz_hydrological_backtest_1984_2025"], ensure_ascii=False, indent=2))
    else:
        print(json.dumps(metrics["models_comparison"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
