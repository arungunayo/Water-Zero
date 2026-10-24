"""WaterZero FastAPI application with TinyFish live water-signal research."""
from __future__ import annotations

import json
import os
import sqlite3
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from tinyfish_client import TinyFishError, fetch, search
from evidence import detect_conflicts, enrich_fetched, normalize_search

load_dotenv()

app = FastAPI(
    title="WaterZero API",
    description="Live official-source research for reservoir risk evidence using TinyFish Search and Fetch.",
    version="0.3.0",
)


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
    """Explicit research objectives; official domains are preferred in query wording."""
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


@app.get("/")
async def root():
    return {
        "message": "WaterZero API is running",
        "tinyfish_configured": bool(os.getenv("TINYFISH_API_KEY")),
        "research_endpoint": "/api/research",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "ok", "tinyfish_configured": bool(os.getenv("TINYFISH_API_KEY"))}


@app.post("/api/research")
async def research(req: ResearchRequest):
    """Search all four water-risk signal classes, fetch pages, extract dates/claims and flag conflicts."""
    if req.date_from > req.date_to:
        raise HTTPException(status_code=422, detail="date_from must be on or before date_to")
    if not os.getenv("TINYFISH_API_KEY", "").strip():
        raise HTTPException(status_code=503, detail="TINYFISH_API_KEY is missing. Set it in your local .env file.")

    objectives = _build_queries(req)
    evidence: list[dict[str, Any]] = []
    search_errors: list[dict[str, str]] = []

    # Search each objective independently so a failure in one category does not stop others.
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

    # Deduplicate by URL and prefer official domains, then keep a balanced spread by category.
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
    # Make old records visible rather than silently dropping them.
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
        # Keep research usable if local evidence storage is temporarily unavailable.
        result["storage_warning"] = f"Could not persist this run ({type(exc).__name__})."
    return result


@app.get("/api/research/runs/{run_id}")
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


@app.get("/hello/{name}")
async def say_hello(name: str):
    # Original starter route preserved.
    return {"message": f"Hello {name}"}
