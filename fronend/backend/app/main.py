import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from . import page_data
from .data_source import get_dashboard
from .schemas import DashboardResponse
from .schemas_pages import (
    AboutTeamResponse,
    EvidenceResponse,
    ForecastResponse,
    MethodologyResponse,
    ModelHealthResponse,
    ReportsResponse,
    StressTestResponse,
)

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
PAGE_TEMPLATE = (STATIC_DIR / "page.html").read_text(encoding="utf-8")

app = FastAPI(title="WaterZero API", version="1.1.0")

# Comma-separated list of origins allowed to call the API from a browser.
# Only needed when the frontend is hosted on a different origin than this API.
_origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_methods=["GET"],
    allow_headers=["*"],
)


# ---------- JSON API ----------

@app.get("/api/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/dashboard", response_model=DashboardResponse, tags=["dashboard"])
def dashboard() -> DashboardResponse:
    return get_dashboard()


@app.get("/api/forecast", response_model=ForecastResponse, tags=["screens"])
def forecast() -> dict:
    return page_data.forecast()


@app.get("/api/stress-test", response_model=StressTestResponse, tags=["screens"])
def stress_test() -> dict:
    return page_data.stress_test()


@app.get("/api/evidence", response_model=EvidenceResponse, tags=["screens"])
def evidence() -> dict:
    return page_data.evidence()


@app.get("/api/model-health", response_model=ModelHealthResponse, tags=["screens"])
def model_health() -> dict:
    return page_data.model_health()


@app.get("/api/methodology", response_model=MethodologyResponse, tags=["screens"])
def methodology() -> dict:
    return page_data.methodology()


@app.get("/api/about-team", response_model=AboutTeamResponse, tags=["screens"])
def about_team() -> dict:
    return page_data.about_team()


@app.get("/api/reports", response_model=ReportsResponse, tags=["screens"])
def reports() -> dict:
    return page_data.reports()


# ---------- Pages ----------

# URL path -> page key (matches static/pages/<key>.js and /api/<key>)
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
