"""WaterZero FastAPI application – complete backend for AI water-risk forecasting,
decision support, evidence verification, and operational reporting.
"""
from __future__ import annotations

import json
import os
import sqlite3
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

import frontend_data_source
import frontend_page_data
import frontend_schemas as f_schemas
import frontend_schemas_pages as f_pages
from evidence import detect_conflicts, enrich_fetched, normalize_search
from models_schema import (
    EvidenceDashboardResponse,
    EvidenceVerificationAction,
    ForecastsResponse,
    MethodologyResponse,
    ModelHealthResponse,
    OverviewResponse,
    ReportGenerateRequest,
    ReportRecord,
    ReportsDashboardResponse,
    ReportStatusUpdate,
    ReservoirInfo,
    StressTestRequest,
    StressTestResponse,
    TeamResponse,
    TopInsightsResponse,
)
from prediction_service import prediction_service
from tinyfish_client import TinyFishError, fetch, search

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
if not STATIC_DIR.exists():
    STATIC_DIR = BASE_DIR / "fronend" / "backend" / "static"
PAGE_TEMPLATE = (STATIC_DIR / "page.html").read_text(encoding="utf-8")

app = FastAPI(
    title="WaterZero API",
    description=(
        "Production AI water-risk decision support platform. Powers reservoir storage forecasting, "
        "conformal uncertainty bounds, scenario demand stress testing, live official-source evidence "
        "verification (TinyFish), model health auditing, and decision reports."
    ),
    version="1.1.0",
)

# Enable CORS for local and web UI clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------
# Frontend Static Pages (8-Screen Figma Implementation)
# -------------------------------------------------------------
PAGES = {
    "forecasts": "forecast",
    "stress-test": "stress-test",
    "evidence": "evidence",
    "model-health": "model-health",
    "methodology": "methodology",
    "about-team": "about-team",
    "reports": "reports",
}


def _page_handler(page_key: str):
    def handler() -> HTMLResponse:
        html = PAGE_TEMPLATE.replace("<body>", f'<body data-page="{page_key}">', 1)
        return HTMLResponse(html)

    return handler


for _path, _key in PAGES.items():
    app.add_api_route(f"/{_path}", _page_handler(_key), methods=["GET"], include_in_schema=False)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")



# -------------------------------------------------------------
# Research Request Schema (Preserved)
# -------------------------------------------------------------
class ResearchRequest(BaseModel):
    reservoir: str = Field(min_length=2, max_length=120, examples=["Hirakud"])
    state: str = Field(min_length=2, max_length=100, examples=["Odisha"])
    district: str | None = Field(default=None, max_length=120)
    date_from: date = Field(default_factory=lambda: date.today() - timedelta(days=90))
    date_to: date = Field(default_factory=date.today)
    forecast_horizon_days: int = Field(default=14, ge=1, le=90)
    max_sources: int = Field(default=8, ge=1, le=10)
    stale_after_days: int = Field(default=90, ge=1, le=730)
    additional_context: str = Field(default="", max_length=1000)


def _db_path() -> Path:
    path = Path(os.getenv("WATERZERO_EVIDENCE_DB", "data/waterzero_evidence.sqlite3"))
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _save_run(payload: dict[str, Any]) -> int:
    with sqlite3.connect(_db_path()) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS research_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                reservoir TEXT NOT NULL,
                state TEXT NOT NULL,
                date_from TEXT NOT NULL,
                date_to TEXT NOT NULL,
                forecast_horizon_days INTEGER NOT NULL,
                evidence_json TEXT NOT NULL
            )
        """)
        cursor = conn.execute(
            """INSERT INTO research_runs
               (created_at, reservoir, state, date_from, date_to, forecast_horizon_days, evidence_json)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                datetime.now(timezone.utc).isoformat(),
                payload["reservoir"], payload["state"], payload["date_from"], payload["date_to"],
                payload["forecast_horizon_days"],
                json.dumps(payload["evidence"], ensure_ascii=False),
            ),
        )
        return int(cursor.lastrowid)


def _build_queries(req: ResearchRequest) -> list[dict[str, str]]:
    geo = f'"{req.reservoir}" "{req.state}"'
    if req.district:
        geo += f' "{req.district}"'
    dates = f'after:{req.date_from.isoformat()} before:{(req.date_to + timedelta(days=1)).isoformat()}'
    extra = f" {req.additional_context.strip()}" if req.additional_context.strip() else ""
    return [
        {
            "query_type": "reservoir_storage_bulletin",
            "query": f'{geo} official reservoir storage live storage bulletin CWC {dates}{extra}',
        },
        {
            "query_type": "district_drought_advisory",
            "query": f'"{req.state}" {("district " + req.district) if req.district else "district"} official drought advisory rainfall deficit government {dates}{extra}',
        },
        {
            "query_type": "rainfall_and_catchment_warning",
            "query": f'{geo} IMD official rainfall forecast catchment warning heavy rainfall bulletin {dates}{extra}',
        },
        {
            "query_type": "municipal_water_supply_restrictions",
            "query": f'{geo} {("district " + req.district) if req.district else ""} municipal corporation official water supply restrictions rationing supply schedule {dates}{extra}',
        },
    ]


# -------------------------------------------------------------
# Core Info & Health Endpoints
# -------------------------------------------------------------
@app.get("/api/info", tags=["System"])
async def api_info():
    return {
        "message": "WaterZero API is operational",
        "version": "1.1.0",
        "active_reservoir": "Hirakud Reservoir (Odisha)",
        "features": {
            "dashboard": "/api/dashboard",
            "forecast": "/api/forecast",
            "stress_test": "/api/stress-test",
            "evidence": "/api/evidence",
            "model_health": "/api/model-health",
            "reports": "/api/reports",
            "methodology": "/api/methodology",
            "about_team": "/api/about-team",
            "research": "/api/research",
        },
        "docs": "/docs",
    }


@app.get("/api/health", tags=["System"])
async def api_health():
    return {"status": "ok"}


@app.get("/health", tags=["System"])
async def health():
    return {
        "status": "healthy",
        "model_loaded": True,
        "tinyfish_configured": bool(os.getenv("TINYFISH_API_KEY")),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# -------------------------------------------------------------
# 00 Frontend Dashboard & Screen Endpoints
# -------------------------------------------------------------
@app.get("/api/dashboard", response_model=f_schemas.DashboardResponse, tags=["Screens"])
async def dashboard_endpoint(reservoir: str = Query(default="hirakud")):
    """Complete payload for WaterZero Overview / Dashboard screen."""
    return frontend_data_source.get_dashboard(reservoir)


@app.get("/api/forecast", response_model=f_pages.ForecastResponse, tags=["Screens"])
async def forecast_endpoint(reservoir: str = Query(default="hirakud")):
    """Complete payload for WaterZero Storage Forecast screen."""
    return frontend_page_data.forecast(reservoir)


# -------------------------------------------------------------
# 01 Reservoirs & Top Navigation Insights
# -------------------------------------------------------------
@app.get("/api/reservoirs", response_model=list[ReservoirInfo], tags=["Reservoirs"])
async def list_reservoirs():
    """List all supported reservoirs (Hirakud with active ML model and KRS demo)."""
    return prediction_service.list_reservoirs()


@app.get("/api/reservoirs/{reservoir_id}", response_model=ReservoirInfo, tags=["Reservoirs"])
async def get_reservoir(reservoir_id: str):
    """Retrieve metadata and physical characteristics of a specific reservoir."""
    return prediction_service.get_reservoir(reservoir_id)


@app.get("/api/overview/insights", response_model=TopInsightsResponse, tags=["Overview"])
async def get_top_insights(reservoir: str = Query(default="hirakud")):
    """Returns the 5 primary insight metric cards shown in the UI top navigation banner:
    01. Current Reservoir Storage & capacity
    02. 30-Day Storage Outlook & confidence range
    03. Simulated Water Cover & monsoon gap
    04. Source Verification counts (verified vs stale)
    05. Model Reliability (MAE / RMSE pts & horizon bars)
    """
    return prediction_service.get_top_insights(reservoir)


# -------------------------------------------------------------
# 02 Overview Screen
# -------------------------------------------------------------
@app.get("/api/overview", response_model=OverviewResponse, tags=["Overview"])
async def get_overview(reservoir: str = Query(default="hirakud")):
    """Complete payload for the Overview dashboard:
    - Live Storage card (storage %, BCM, gross capacity, 7D & 14D outlooks)
    - 01 / Storage Trajectory (observed history, 30-day forecast steps with bands, critical threshold line)
    - 02 / Threshold Watch (estimated days to threshold, daily depletion rate, warning status)
    - 03 / Decision Lab summary (base vs deficient rainfall, simulated cover)
    - 04 / Evidence Log preview (recent official signals with verification tags)
    """
    return prediction_service.get_overview(reservoir)


# -------------------------------------------------------------
# 03 Storage Forecast Screen
# -------------------------------------------------------------
@app.get("/api/forecasts", response_model=ForecastsResponse, tags=["Forecasts"])
async def get_forecasts(reservoir: str = Query(default="hirakud")):
    """Complete payload for the Storage Forecast screen:
    - 7-Day, 14-Day, 30-Day forecast horizon cards (predicted, low, high, change pts)
    - Stepped historical observations vs forecast trajectory with conformal prediction intervals
    - Demand stress test summary (Low, Base, High demand days of cover)
    - 03A Threshold Risk gauge (calibrated probability of falling below critical line)
    - 03B Storage Composition donut (usable storage, dead storage, buffer)
    - 04 Forecast Reliability (backtest error by horizon, event recall %, false alarm rate %)
    - Provenance & model version metadata
    """
    return prediction_service.get_forecasts(reservoir)


# -------------------------------------------------------------
# 04 Demand Stress Test Screen
# -------------------------------------------------------------
@app.get("/api/stress-test", response_model=f_pages.StressTestResponse, tags=["Stress Test"])
async def get_stress_test_screen(reservoir: str = Query(default="hirakud")):
    """Complete payload for Demand Stress Test frontend screen."""
    return frontend_page_data.stress_test(reservoir)


@app.get("/api/stress-test/simulation", response_model=StressTestResponse, tags=["Stress Test"])
async def get_default_stress_test(reservoir: str = Query(default="hirakud")):
    """Returns default demand stress-test scenario, water cover runway, and sensitivity ranking."""
    return prediction_service.simulate_stress_test(StressTestRequest(), reservoir)


@app.post("/api/stress-test/simulate", response_model=StressTestResponse, tags=["Stress Test"])
async def simulate_stress_test(req: StressTestRequest, reservoir: str = Query(default="hirakud")):
    """Interactive what-if scenario simulation:
    - Adjust water demand (baseline / low -15% / high +20% / contingency -30%)
    - Adjust inflow conditions (normal / deficient -30% / severe -50% / surplus +30%)
    - Adjust monsoon timing (on_schedule / delayed 14d / delayed 30d / early 7d)
    - Returns estimated water cover days, monsoon gap, scenario risk rating, and sensitivity ranking.
    """
    return prediction_service.simulate_stress_test(req, reservoir)


# -------------------------------------------------------------
# 05 Evidence & Verification Screen
# -------------------------------------------------------------
@app.get("/api/evidence", response_model=f_pages.EvidenceResponse, tags=["Evidence"])
async def get_evidence_screen(reservoir: str = Query(default="hirakud")):
    """Complete payload for Evidence & Verification frontend screen."""
    return frontend_page_data.evidence(reservoir)


@app.get("/api/evidence/dashboard", response_model=EvidenceDashboardResponse, tags=["Evidence"])
async def get_evidence_dashboard(reservoir: str = Query(default="hirakud")):
    """Complete payload for Evidence & Verification backend audit:
    - Workflow progress: Search -> Fetch -> Verify -> Evidence Ready
    - Summary counts (sources found, verified, needs review, latest update)
    - Source review queue (bulletins, advisories, claims, stance, freshness)
    - Evidence quality stats (freshness breakdown, source type distribution)
    - Conflicting signals list
    - Official source comparison table
    - Audit trail log
    """
    return prediction_service.get_evidence_dashboard(reservoir)


@app.post("/api/evidence/verify", tags=["Evidence"])
async def verify_evidence(action: EvidenceVerificationAction):
    """Human-in-the-loop verification action:
    Mark an evidence item as 'verified', 'needs_review', 'stale', or 'context_only',
    with optional stance update and hydrologist notes.
    """
    res = prediction_service.verify_evidence_item(action)
    if not res.get("success"):
        raise HTTPException(status_code=404, detail=res.get("error", "Evidence item not found"))
    return res


# -------------------------------------------------------------
# Live Official Research (TinyFish Client – Preserved)
# -------------------------------------------------------------
@app.post("/api/research", tags=["Evidence"])
async def research(req: ResearchRequest):
    """Search all four water-risk signal classes using TinyFish Search & Fetch,
    extract dates/claims, flag conflicts, and record in local database.
    """
    if req.date_from > req.date_to:
        raise HTTPException(status_code=422, detail="date_from must be on or before date_to")
    if not os.getenv("TINYFISH_API_KEY", "").strip():
        raise HTTPException(status_code=503, detail="TINYFISH_API_KEY is missing. Set it in your local .env file.")

    objectives = _build_queries(req)
    evidence: list[dict[str, Any]] = []
    search_errors: list[dict[str, str]] = []

    for objective in objectives:
        try:
            raw = await search(objective["query"])
            rows = normalize_search(
                raw, reservoir=req.reservoir, state=req.state,
                query_type=objective["query_type"],
            )
            evidence.extend(rows)
        except TinyFishError as exc:
            search_errors.append({"query_type": objective["query_type"], "error": str(exc)})

    dedup: dict[str, dict[str, Any]] = {}
    for item in evidence:
        key = item["source_url"].rstrip("/")
        if key not in dedup or (item["is_official_domain"] and not dedup[key]["is_official_domain"]):
            dedup[key] = item
    candidates = list(dedup.values())
    candidates.sort(key=lambda item: (not item["is_official_domain"], item["query_type"], item["source_url"]))
    candidates = candidates[:req.max_sources]

    fetch_errors: list[str] = []
    if candidates:
        try:
            fetch_result = await fetch([item["source_url"] for item in candidates])
            candidates = enrich_fetched(
                candidates, fetch_result, state=req.state, reservoir=req.reservoir,
                stale_after_days=req.stale_after_days,
            )
        except TinyFishError as exc:
            fetch_errors.append(str(exc))
            for item in candidates:
                item["verification_status"] = "fetch_api_error"
                item["fetch_error"] = str(exc)

    candidates = detect_conflicts(candidates)
    stale_sources = [
        {"title": item["title"], "source_url": item["source_url"], "publication_date": item["publication_date"]}
        for item in candidates if item["staleness"] == "stale"
    ]
    conflicts = [
        {"title": item["title"], "source_url": item["source_url"], "stance": item["stance"]}
        for item in candidates if item["conflict_group"]
    ]

    result = {
        "reservoir": req.reservoir,
        "state": req.state,
        "district": req.district,
        "date_range": {"from": req.date_from.isoformat(), "to": req.date_to.isoformat()},
        "forecast_horizon_days": req.forecast_horizon_days,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "search_objectives": objectives,
        "sources_found": len(evidence),
        "sources_fetched": sum(bool(item.get("fetched_content_excerpt")) for item in candidates),
        "evidence": candidates,
        "stale_sources": stale_sources,
        "conflicting_signals": conflicts,
        "search_errors": search_errors,
        "fetch_errors": fetch_errors,
        "validation_policy": {
            "official_source_priority": "Government and recognized official domains are prioritized, not automatically trusted.",
            "date_extraction": "Publication date is extracted from API metadata or page text; null means it was not reliably found.",
            "verification_status": "A fetched page is not automatically considered verified. Human/source validation remains required.",
            "forecast_integrity": "Research evidence does not change the numerical forecast.",
        },
    }
    try:
        result["research_run_id"] = _save_run(result)
    except Exception as exc:
        result["storage_warning"] = f"Could not persist this run ({type(exc).__name__})."
    return result


@app.get("/api/research/runs/{run_id}", tags=["Evidence"])
async def get_research_run(run_id: int):
    """Retrieve a previously stored evidence snapshot."""
    if run_id < 1:
        raise HTTPException(status_code=422, detail="run_id must be positive")
    if not _db_path().exists():
        raise HTTPException(status_code=404, detail="No research runs have been saved.")
    with sqlite3.connect(_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM research_runs WHERE id = ?", (run_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Research run not found.")
    return {
        "id": row["id"],
        "created_at": row["created_at"],
        "reservoir": row["reservoir"],
        "state": row["state"],
        "date_range": {"from": row["date_from"], "to": row["date_to"]},
        "forecast_horizon_days": row["forecast_horizon_days"],
        "evidence": json.loads(row["evidence_json"]),
    }


# -------------------------------------------------------------
# 06 Model Health Screen
# -------------------------------------------------------------
@app.get("/api/model-health", response_model=f_pages.ModelHealthResponse, tags=["Model Health"])
async def get_model_health_screen(reservoir: str = Query(default="hirakud")):
    """Complete payload for Model Health & Evaluation frontend screen."""
    return frontend_page_data.model_health(reservoir)


@app.get("/api/model-health/metrics", response_model=ModelHealthResponse, tags=["Model Health"])
async def get_model_health(reservoir: str = Query(default="hirakud")):
    """Complete payload for Model Health & Evaluation raw metrics:
    - Active Model metadata & status
    - KPI cards: Forecast MAE/RMSE, Improvement vs Seasonal & Persistence, Recall %, False Alarm %
    - 01 / Horizon comparison: Model vs Persistence vs Seasonal across 7D, 14D, 30D
    - 02 / Time-series evaluation: Actual vs Predicted with conformal intervals
    - 03 / Residual analysis: Error distribution, mean, median, skew
    - 04 / Error breakdown: Monsoon vs Dry season performance per horizon
    - 05 / Historical backtesting: Chronological train/validation/test window splits
    - 06 / Input data health: Missingness and observation freshness for reservoir, rainfall, temp, discharge
    - 07 / Forecast uncertainty: Empirical coverage vs nominal 80% conformal level
    - 08 / Early-warning performance: Confusion matrix, recall, precision, lead time
    - 09 / Health assessment: Drift checks suite (MAE ratio, skill floor, coverage band, age)
    - 10 / Model version & audit trail: Retrain history log
    """
    return prediction_service.get_model_health(reservoir)


# -------------------------------------------------------------
# 07 Reports Screen
# -------------------------------------------------------------
@app.get("/api/reports", response_model=f_pages.ReportsResponse, tags=["Reports"])
async def get_reports_screen(reservoir: str = Query(default="hirakud")):
    """Complete payload for Reports frontend screen."""
    return frontend_page_data.reports(reservoir)


@app.get("/api/reports/dashboard", response_model=ReportsDashboardResponse, tags=["Reports"])
async def get_reports_dashboard():
    """Returns report overview metrics, featured templates, and list of previous reports."""
    return prediction_service.get_reports_dashboard()


@app.post("/api/reports/generate", response_model=ReportRecord, tags=["Reports"])
async def generate_report(req: ReportGenerateRequest):
    """Generate a new decision-support assessment report:
    Select reservoir, horizon, sections to include (forecasts, stress test, evidence, recommendations),
    and output format. Generates executive summary and structured findings.
    """
    return await prediction_service.generate_report(req)


@app.get("/api/groq/status", tags=["System"])
async def groq_status():
    """Returns Groq LLM integration status and model configuration."""
    from groq_client import is_groq_configured, DEFAULT_MODEL
    return {
        "groq_configured": is_groq_configured(),
        "model": DEFAULT_MODEL,
        "role": "Hydrological Decision Support & Mitigation Recommendations Synthesizer",
    }


@app.get("/api/reports/{report_id}", response_model=ReportRecord, tags=["Reports"])
async def get_report_by_id(report_id: int):
    """Retrieve full details and content of a specific report by ID."""
    rep = prediction_service.get_report_by_id(report_id)
    if not rep:
        raise HTTPException(status_code=404, detail="Report not found")
    return rep


@app.post("/api/reports/{report_id}/status", response_model=ReportRecord, tags=["Reports"])
async def update_report_status(report_id: int, req: ReportStatusUpdate):
    """Workflow state transition for reports:
    Transition report status between 'draft', 'in_review', and 'approved' with reviewer notes.
    """
    rep = prediction_service.update_report_status(report_id, req)
    if not rep:
        raise HTTPException(status_code=404, detail="Report not found")
    return rep


# -------------------------------------------------------------
# 08 Methodology & Team Screens
# -------------------------------------------------------------
@app.get("/api/methodology", response_model=f_pages.MethodologyResponse, tags=["Methodology"])
async def get_methodology():
    """Returns methodology details from 'How WaterZero thinks ahead':
    5 connected stages, simplified water-balance equation, core pillars, and decision principles.
    """
    return frontend_page_data.methodology()


@app.get("/api/about-team", response_model=f_pages.AboutTeamResponse, tags=["Team"])
async def get_about_team():
    """Returns team information: Arohan Arora (Team Leader) & Kunal Chawla (Team Member)."""
    return frontend_page_data.about_team()


@app.get("/api/team", response_model=TeamResponse, tags=["Team"])
async def get_team():
    """Returns raw team info model."""
    return prediction_service.get_team()


# -------------------------------------------------------------
# Legacy / Test Starter Route (Preserved)
# -------------------------------------------------------------
@app.get("/hello/{name}", tags=["System"])
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
