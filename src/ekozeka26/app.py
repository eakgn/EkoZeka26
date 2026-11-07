"""
WBS-5: AquaSanayi AI FastAPI Backend (`app.py`)

Uç Noktalar (REST API):
- `GET /` : 2 Sekmeli Etkileşimli Web Arayüzü (`static/index.html`)
- `GET /api/health` : Sistem durumu, veri soyu ve doğrulanan ML model metrikleri
- `GET /api/basins` : Türkiye'nin 639 alt-havzasının GeoJSON harita katmanı + seçilen yıl/senaryo/sektör risk özetleri
- `GET /api/osb-compare` & `POST /api/osb-compare` : Aday OSB'lerin şeffaf bileşik risk, P10-P90 kesinti günü ve iklim karşılaştırması
- `GET /api/predict-location` & `POST /api/predict-location` : Tıklanan (lat, lon) veya seçilen OSB için coğrafi sınır korumalı şeffaf risk + SHAP (<50 ms) + KMeans arketip + 7 CMIP6 model P10-P90 su dengesi serisi
- `POST /api/simulate-roi` & `GET /api/simulate-roi` : Bütçe kısıtlı 0-1 Knapsack su verimliliği portföy optimizasyonu, kuyu vs şebeke analizi ve 27.12.2029 Yeşil Belge kademesi
- `POST /api/executive-summary` : Hesaplanan kesin JSON çıktısından Gemini / Deterministik Yönetim Kurulu Raporu
- `GET /api/izsu-live` : İZSU 6 Kasım 2026 baraj dolulukları (%34,0 ağırlıklı vs %44,2 basit ort.), 23 günlük Balçova düşüşü (-7,43 puan) ve 137 aylık üretim kaydı üzerinde Isolation Forest anomali raporu
- `GET /api/facility-sample` : Açık tesis şeması (`facility.schema.json`) ve hazır örnek tesis profilleri (`kemalpasa_textile`, `manisa_food`, `aliaga_chemical`)
- `GET /api/export/json` & `POST /api/export/json` : Açık şema uyumlu JSON rapor indirme
- `GET /api/export/csv` & `POST /api/export/csv` : Kurumsal envanter eşlenebilir CSV rapor indirme
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from ekozeka26.anomaly import detect_izsu_and_gediz_anomalies
from ekozeka26.data_pipeline import PROCESSED_DIR, PROJECT_ROOT
from ekozeka26.llm_agent import generate_executive_summary
from ekozeka26.ml_engine import explain_basin_summer_peak_shap
from ekozeka26.risk_index import (
    _future_ws_col,
    _load_basins_df,
    _load_climate_osb,
    _load_osb_profiles,
    compare_candidate_osbs,
    compute_transparent_risk,
    find_basin_by_coords,
)
from ekozeka26.roi_optimizer import (
    export_simulation_to_csv,
    optimize_facility_roi,
)

STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
SCHEMA_PATH = PROJECT_ROOT / "data" / "schema" / "facility.schema.json"

app = FastAPI(
    title="AquaSanayi AI — Endüstriyel Su Kıtlığı Risk, Yer Seçimi ve ROI Karar Platformu",
    version="1.0.0",
    description=(
        "EkoZeka26 Hackathonu: Fizik-öncelikli + ML destekli (WRI Aqueduct 4.0 + ERA5 + 7 CMIP6 + İZSU) "
        "endüstriyel su kıtlığı risk, yer seçimi ve bütçe kısıtlı 2029 Yeşil Su Verimliliği Belgesi "
        "optimizasyon platformu."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

_GEOJSON_RAW_CACHE: dict[str, Any] | None = None
_MODEL_METRICS_CACHE: dict[str, Any] | None = None
_ANOMALY_CACHE: dict[str, Any] | None = None


def _get_geojson_dict() -> dict[str, Any]:
    global _GEOJSON_RAW_CACHE
    if _GEOJSON_RAW_CACHE is None:
        _GEOJSON_RAW_CACHE = json.loads((PROCESSED_DIR / "turkey_basins.geojson").read_text(encoding="utf-8"))
    return _GEOJSON_RAW_CACHE


def _get_model_metrics() -> dict[str, Any]:
    global _MODEL_METRICS_CACHE
    if _MODEL_METRICS_CACHE is None:
        p = PROCESSED_DIR / "model_metrics.json"
        if p.exists():
            _MODEL_METRICS_CACHE = json.loads(p.read_text(encoding="utf-8"))
        else:
            _MODEL_METRICS_CACHE = {}
    return _MODEL_METRICS_CACHE


def _get_anomaly_report() -> dict[str, Any]:
    global _ANOMALY_CACHE
    if _ANOMALY_CACHE is None:
        _ANOMALY_CACHE = detect_izsu_and_gediz_anomalies()
    return _ANOMALY_CACHE


class LocationPredictRequest(BaseModel):
    lat: float | None = Field(default=None, description="Enlem (derece)")
    lon: float | None = Field(default=None, description="Boylam (derece)")
    osb_id: str | None = Field(default="izmir_kemalpasa", description="OSB tanımlayıcısı")
    string_id: str | None = Field(default=None, description="Aqueduct 4.0 poligon tekil anahtarı")
    sector: str = Field(default="textile", description="Sektör kodu")
    year: int | str = Field(default=2050, description="Hedef yıl (Baseline, 2030, 2050, 2080)")
    scenario: str = Field(default="BAU", description="İklim senaryosu (OPT, BAU, PES)")


class OSBCompareRequest(BaseModel):
    osb_ids: list[str] | None = Field(default=None)
    sector: str = Field(default="textile")
    year: int | str = Field(default=2050)
    scenario: str = Field(default="BAU")


class ROISimulateRequest(BaseModel):
    facility_name: str = Field(default="EgeDokuma Tekstil Terbiye & Boyahane A.Ş. (Kemalpaşa OSB)")
    osb_id: str = Field(default="izmir_kemalpasa")
    sector: str = Field(default="textile")
    employee_count: int = Field(default=320, ge=1)
    annual_water_m3: float = Field(default=150000.0, gt=0)
    water_source: str = Field(default="izsu_grid")
    grid_share_pct: float = Field(default=100.0, ge=0, le=100)
    process_shares: dict[str, float] | None = Field(default=None)
    daily_downtime_cost_tl: float = Field(default=750000.0, ge=0)
    capex_budget_tl: float = Field(default=3500000.0, ge=0)
    target_year: int | str = Field(default=2030)
    scenario: str = Field(default="BAU")


class ExecutiveSummaryRequest(BaseModel):
    simulation_result: dict[str, Any] | None = Field(default=None)
    simulation_params: ROISimulateRequest | None = Field(default=None)
    prefer_online_llm: bool = Field(default=False)


@app.get("/", response_class=HTMLResponse)
def serve_index() -> HTMLResponse:
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return HTMLResponse(index_file.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>AquaSanayi AI Çalışıyor</h1>")


@app.get("/api/health")
def api_health() -> dict[str, Any]:
    metrics = _get_model_metrics()
    return {
        "status": "ok",
        "service": "AquaSanayi AI",
        "offline_ready": True,
        "last_verified_data_date": "2026-11-06",
        "turkey_basins_count": 639,
        "unique_pfaf_basins": 116,
        "model_metrics_summary": metrics.get("models_comparison", {}),
        "gediz_backtest_summary": metrics.get("gediz_hydrological_backtest_1984_2025", {}),
    }


@app.get("/api/basins")
def api_basins(
    sector: str = Query(default="textile"),
    year: str = Query(default="2050"),
    scenario: str = Query(default="BAU"),
) -> dict[str, Any]:
    """
    Türkiye'nin 639 alt-havzasının GeoJSON poligonlarını ve seçilen (sector, year, scenario)
    için aktif su stresi değerini (`active_ws_raw`) döner.
    """
    gj = _get_geojson_dict()
    ws_col = _future_ws_col(year, scenario)
    osb_meta = _load_osb_profiles()
    return {
        "type": "FeatureCollection",
        "metadata": {
            "polygon_count": len(gj.get("features", [])),
            "active_ws_column": ws_col,
            "sector": sector,
            "year": year,
            "scenario": scenario.upper(),
        },
        "osb_markers": osb_meta["osbs"],
        "features": gj.get("features", []),
    }


@app.get("/api/osb-compare")
def api_osb_compare_get(
    sector: str = Query(default="textile"),
    year: str = Query(default="2050"),
    scenario: str = Query(default="BAU"),
    osb_ids: str | None = Query(default=None, description="Virgülle ayrılmış OSB kodları"),
) -> dict[str, Any]:
    id_list = [x.strip() for x in osb_ids.split(",") if x.strip()] if osb_ids else None
    comp = compare_candidate_osbs(osb_ids=id_list, sector=sector, year=year, scenario=scenario)
    metrics = _get_model_metrics()
    return {
        **comp,
        "model_validation_metrics": metrics.get("models_comparison", {}),
        "gediz_backtest": metrics.get("gediz_hydrological_backtest_1984_2025", {}),
    }


@app.post("/api/osb-compare")
def api_osb_compare_post(req: OSBCompareRequest) -> dict[str, Any]:
    comp = compare_candidate_osbs(
        osb_ids=req.osb_ids, sector=req.sector, year=req.year, scenario=req.scenario
    )
    metrics = _get_model_metrics()
    return {
        **comp,
        "model_validation_metrics": metrics.get("models_comparison", {}),
        "gediz_backtest": metrics.get("gediz_hydrological_backtest_1984_2025", {}),
    }


def _evaluate_location_payload(req: LocationPredictRequest) -> dict[str, Any]:
    osb_meta = _load_osb_profiles()
    climate_all = _load_climate_osb()
    osb_projs = climate_all.get("osb_projections", {})
    df_basins = _load_basins_df().set_index("string_id")
    all_osbs = {o["osb_id"]: o for o in osb_meta["osbs"]}

    boundary_warning = None
    inside_turkey = True
    matched_osb: dict[str, Any] | None = None

    if req.lat is not None and req.lon is not None:
        geo_hit = find_basin_by_coords(req.lat, req.lon)
        inside_turkey = bool(geo_hit["inside_turkey"])
        boundary_warning = geo_hit["warning"]
        basin_row = geo_hit["basin_row"]
        # En yakın OSB'yi iklim serisi referansı için bul
        best_oid = min(
            all_osbs.keys(),
            key=lambda k: (all_osbs[k]["lat"] - float(req.lat)) ** 2 + (all_osbs[k]["lon"] - float(req.lon)) ** 2,
        )
        matched_osb = all_osbs[best_oid]
    elif req.string_id and req.string_id in df_basins.index:
        basin_row = df_basins.loc[req.string_id].to_dict()
        best_oid = next(
            (k for k, v in all_osbs.items() if v["pfaf_id"] == int(basin_row["pfaf_id"])),
            "izmir_kemalpasa",
        )
        matched_osb = all_osbs[best_oid]
    else:
        oid = req.osb_id if (req.osb_id and req.osb_id in all_osbs) else "izmir_kemalpasa"
        matched_osb = all_osbs[oid]
        sid = matched_osb["string_id"]
        basin_row = df_basins.loc[sid].to_dict() if sid in df_basins.index else matched_osb

    assert matched_osb is not None
    c_osb = osb_projs.get(matched_osb["osb_id"], {})
    c_scen = c_osb.get("scenarios", {}).get(str(req.scenario).upper(), {})
    decadal_wb_trend = float(c_scen.get("decadal_trend_mm", -32.0))
    spei_proxy_trend = round(decadal_wb_trend / 95.0, 2)

    gw_dep = float(matched_osb["groundwater_dependency_pct"]) if req.lat is None else None
    risk_res = compute_transparent_risk(
        basin_row=basin_row,
        sector=req.sector,
        year=req.year,
        scenario=req.scenario,
        groundwater_dependency_pct=gw_dep,
        spei12_trend=spei_proxy_trend,
    )
    shap_res = explain_basin_summer_peak_shap(basin_row=basin_row, month=8)

    return {
        "inside_turkey": inside_turkey,
        "boundary_warning": boundary_warning,
        "selected_osb": matched_osb,
        "transparent_risk": risk_res,
        "xgboost_shap_explanation": shap_res,
        "climate_water_balance_2026_2050": c_scen,
        "climate_metadata": {
            "ensemble_models": climate_all.get("ensemble_models", []),
            "et0_method": c_osb.get("et0_method", "FAO-56 / Hargreaves-Samani"),
            "bias_correction_method": c_osb.get("bias_correction_method", "QDM"),
            "historical_baseline_wb_mm": c_osb.get("historical_baseline_1991_2020_wb_mm", -420.0),
            "drought_2025_wb_mm": c_osb.get("drought_2025_observed_wb_mm", -680.0),
        },
        "model_validation_metrics": _get_model_metrics().get("models_comparison", {}),
    }


@app.get("/api/predict-location")
def api_predict_location_get(
    lat: float | None = Query(default=None),
    lon: float | None = Query(default=None),
    osb_id: str | None = Query(default="izmir_kemalpasa"),
    string_id: str | None = Query(default=None),
    sector: str = Query(default="textile"),
    year: str = Query(default="2050"),
    scenario: str = Query(default="BAU"),
) -> dict[str, Any]:
    req = LocationPredictRequest(
        lat=lat, lon=lon, osb_id=osb_id, string_id=string_id, sector=sector, year=year, scenario=scenario
    )
    return _evaluate_location_payload(req)


@app.post("/api/predict-location")
def api_predict_location_post(req: LocationPredictRequest) -> dict[str, Any]:
    return _evaluate_location_payload(req)


@app.post("/api/simulate-roi")
def api_simulate_roi_post(req: ROISimulateRequest) -> dict[str, Any]:
    try:
        sim = optimize_facility_roi(
            osb_id=req.osb_id,
            sector=req.sector,
            annual_water_m3=req.annual_water_m3,
            water_source=req.water_source,
            grid_share_pct=req.grid_share_pct,
            process_shares=req.process_shares,
            daily_downtime_cost_tl=req.daily_downtime_cost_tl,
            capex_budget_tl=req.capex_budget_tl,
            target_year=req.target_year,
            scenario=req.scenario,
            employee_count=req.employee_count,
            facility_name=req.facility_name,
        )
        exec_summary = generate_executive_summary(sim, prefer_online_llm=False)
        return {
            **sim,
            "executive_summary": exec_summary,
        }
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/api/simulate-roi")
def api_simulate_roi_get(
    osb_id: str = Query(default="izmir_kemalpasa"),
    sector: str = Query(default="textile"),
    annual_water_m3: float = Query(default=150000.0, gt=0),
    water_source: str = Query(default="izsu_grid"),
    daily_downtime_cost_tl: float = Query(default=750000.0, ge=0),
    capex_budget_tl: float = Query(default=3500000.0, ge=0),
    target_year: str = Query(default="2030"),
    scenario: str = Query(default="BAU"),
) -> dict[str, Any]:
    sim = optimize_facility_roi(
        osb_id=osb_id,
        sector=sector,
        annual_water_m3=annual_water_m3,
        water_source=water_source,
        daily_downtime_cost_tl=daily_downtime_cost_tl,
        capex_budget_tl=capex_budget_tl,
        target_year=target_year,
        scenario=scenario,
    )
    exec_summary = generate_executive_summary(sim, prefer_online_llm=False)
    return {
        **sim,
        "executive_summary": exec_summary,
    }


@app.post("/api/executive-summary")
def api_executive_summary(req: ExecutiveSummaryRequest) -> dict[str, Any]:
    if req.simulation_result is not None and "facility_summary" in req.simulation_result:
        sim = req.simulation_result
    else:
        p = req.simulation_params or ROISimulateRequest()
        sim = optimize_facility_roi(
            osb_id=p.osb_id,
            sector=p.sector,
            annual_water_m3=p.annual_water_m3,
            water_source=p.water_source,
            grid_share_pct=p.grid_share_pct,
            process_shares=p.process_shares,
            daily_downtime_cost_tl=p.daily_downtime_cost_tl,
            capex_budget_tl=p.capex_budget_tl,
            target_year=p.target_year,
            scenario=p.scenario,
            employee_count=p.employee_count,
            facility_name=p.facility_name,
        )
    return generate_executive_summary(sim, prefer_online_llm=req.prefer_online_llm)


@app.get("/api/izsu-live")
def api_izsu_live() -> dict[str, Any]:
    izsu = json.loads((PROCESSED_DIR / "izsu_snapshot.json").read_text(encoding="utf-8"))
    anomalies = _get_anomaly_report()
    return {
        "status": "verified_snapshot_and_anomaly_ready",
        "snapshot_date": izsu["snapshot_date"],
        "headline_metrics": izsu["headline_metrics"],
        "dams": izsu["dams"],
        "daily_production": izsu["daily_production"],
        "tariffs_2026": izsu["tariffs_2026"],
        "anomaly_analysis": anomalies,
    }


@app.get("/api/facility-sample")
def api_facility_sample(profile_id: str = Query(default="kemalpasa_textile")) -> dict[str, Any]:
    osb_meta = _load_osb_profiles()
    schema_obj = json.loads(SCHEMA_PATH.read_text(encoding="utf-8")) if SCHEMA_PATH.exists() else {}
    samples = osb_meta["sample_facilities"]
    selected = samples.get(profile_id, samples["kemalpasa_textile"])
    return {
        "schema": schema_obj,
        "selected_profile_id": profile_id if profile_id in samples else "kemalpasa_textile",
        "facility_data": selected,
        "available_profiles": samples,
        "sector_defaults": osb_meta["sector_defaults"],
        "osb_list": osb_meta["osbs"],
    }


@app.get("/api/export/json")
def api_export_json_get(
    osb_id: str = Query(default="izmir_kemalpasa"),
    sector: str = Query(default="textile"),
    annual_water_m3: float = Query(default=150000.0, gt=0),
    water_source: str = Query(default="izsu_grid"),
    daily_downtime_cost_tl: float = Query(default=750000.0, ge=0),
    capex_budget_tl: float = Query(default=3500000.0, ge=0),
) -> JSONResponse:
    sim = optimize_facility_roi(
        osb_id=osb_id,
        sector=sector,
        annual_water_m3=annual_water_m3,
        water_source=water_source,
        daily_downtime_cost_tl=daily_downtime_cost_tl,
        capex_budget_tl=capex_budget_tl,
    )
    return JSONResponse(
        content=sim,
        headers={"Content-Disposition": 'attachment; filename="aquasanayi_roi_raporu.json"'},
    )


@app.post("/api/export/json")
def api_export_json_post(req: ROISimulateRequest) -> JSONResponse:
    sim = optimize_facility_roi(
        osb_id=req.osb_id,
        sector=req.sector,
        annual_water_m3=req.annual_water_m3,
        water_source=req.water_source,
        grid_share_pct=req.grid_share_pct,
        process_shares=req.process_shares,
        daily_downtime_cost_tl=req.daily_downtime_cost_tl,
        capex_budget_tl=req.capex_budget_tl,
        target_year=req.target_year,
        scenario=req.scenario,
        employee_count=req.employee_count,
        facility_name=req.facility_name,
    )
    return JSONResponse(
        content=sim,
        headers={"Content-Disposition": 'attachment; filename="aquasanayi_roi_raporu.json"'},
    )


@app.get("/api/export/csv")
def api_export_csv_get(
    osb_id: str = Query(default="izmir_kemalpasa"),
    sector: str = Query(default="textile"),
    annual_water_m3: float = Query(default=150000.0, gt=0),
    water_source: str = Query(default="izsu_grid"),
    daily_downtime_cost_tl: float = Query(default=750000.0, ge=0),
    capex_budget_tl: float = Query(default=3500000.0, ge=0),
) -> PlainTextResponse:
    sim = optimize_facility_roi(
        osb_id=osb_id,
        sector=sector,
        annual_water_m3=annual_water_m3,
        water_source=water_source,
        daily_downtime_cost_tl=daily_downtime_cost_tl,
        capex_budget_tl=capex_budget_tl,
    )
    csv_text = export_simulation_to_csv(sim)
    return PlainTextResponse(
        content=csv_text,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="aquasanayi_roi_raporu.csv"'},
    )


@app.post("/api/export/csv")
def api_export_csv_post(req: ROISimulateRequest) -> PlainTextResponse:
    sim = optimize_facility_roi(
        osb_id=req.osb_id,
        sector=req.sector,
        annual_water_m3=req.annual_water_m3,
        water_source=req.water_source,
        grid_share_pct=req.grid_share_pct,
        process_shares=req.process_shares,
        daily_downtime_cost_tl=req.daily_downtime_cost_tl,
        capex_budget_tl=req.capex_budget_tl,
        target_year=req.target_year,
        scenario=req.scenario,
        employee_count=req.employee_count,
        facility_name=req.facility_name,
    )
    csv_text = export_simulation_to_csv(sim)
    return PlainTextResponse(
        content=csv_text,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="aquasanayi_roi_raporu.csv"'},
    )
