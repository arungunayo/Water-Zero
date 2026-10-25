"""Groq LLM integration client for WaterZero decision support and report generation."""
from __future__ import annotations

import json
import os
import re
from typing import Any
from dotenv import load_dotenv
import httpx

load_dotenv()

GROQ_API_BASE = "https://api.groq.com/openai/v1/chat/completions"


def get_groq_model() -> str:
    return os.getenv("GROQ_MODEL", "openai/gpt-oss-120b").strip() or "openai/gpt-oss-120b"


def is_groq_configured() -> bool:
    key = os.getenv("GROQ_API_KEY", "").strip()
    return bool(key and not key.lower().startswith(("replace_", "your_")))


async def generate_mitigation_recommendations(
    reservoir: str,
    state: str,
    basin: str,
    current_storage_pct: float,
    current_storage_bcm: float,
    gross_capacity_bcm: float,
    forecast_horizon_days: int,
    predicted_pct: float,
    conformal_range: list[float],
    cover_days: int,
    monsoon_gap: int,
    evidence_claims: list[str],
) -> dict[str, Any]:
    """Uses Groq LLM to synthesize executive recommendations and summary based on ML metrics and TinyFish evidence."""
    if not is_groq_configured():
        return _fallback_recommendations(
            current_storage_pct, predicted_pct, cover_days, monsoon_gap, evidence_claims
        )

    model_name = get_groq_model()
    evidence_text = "\n".join(f"- {c}" for c in evidence_claims) if evidence_claims else "No conflicting advisories reported."

    system_prompt = (
        "You are an expert hydrological advisor and water resources engineer for India's Central Water Commission (CWC). "
        "Your task is to review machine learning storage forecasts, stress-test water runway, and verified official evidence, "
        "and generate professional, prioritized, actionable decision-support recommendations. "
        "Return ONLY a clean JSON object with keys 'executive_summary' (string) and 'recommendations' (array of 3-4 strings). "
        "Do NOT include conversational filler, preamble, or markdown formatting outside the JSON."
    )

    user_prompt = f"""
Reservoir: {reservoir} ({state}, {basin})
Current Storage: {current_storage_pct}% ({current_storage_bcm} BCM / {gross_capacity_bcm} BCM capacity)
Forecast: {forecast_horizon_days}-day machine learning outlook predicts {predicted_pct}% (80% conformal interval: {conformal_range}%)
Demand Stress Test: {cover_days} days of operational water cover (Monsoon arrival gap: {monsoon_gap} days)
Verified Official Evidence Excerpts (TinyFish):
{evidence_text}

Generate:
1. 'executive_summary': A concise 2-sentence executive hydrological briefing.
2. 'recommendations': 3 to 4 specific, actionable operational directives (e.g. municipal conservation tiers, agricultural canal release scheduling, upstream rainfall monitoring, gate maintenance).
"""

    headers = {
        "Authorization": f"Bearer {os.getenv('GROQ_API_KEY', '').strip()}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 800,
    }

    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            resp = await client.post(GROQ_API_BASE, headers=headers, json=payload)
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"].strip()
                # Clean any markdown code blocks
                clean_json = re.sub(r"^```(?:json)?\s*|\s*```$", "", content, flags=re.DOTALL).strip()
                data = json.loads(clean_json)
                return {
                    "source": "groq",
                    "model": model_name,
                    "executive_summary": data.get("executive_summary", ""),
                    "recommendations": data.get("recommendations", []),
                }
            else:
                print(f"[Groq Error {resp.status_code}] {resp.text}")
    except Exception as ex:
        print(f"[Groq LLM Warning] Falling back to rule engine: {ex}")

    return _fallback_recommendations(
        current_storage_pct, predicted_pct, cover_days, monsoon_gap, evidence_claims
    )


def _fallback_recommendations(
    current_storage_pct: float,
    predicted_pct: float,
    cover_days: int,
    monsoon_gap: int,
    evidence_claims: list[str],
) -> dict[str, Any]:
    """Deterministic fallback recommendations when Groq API key is not configured."""
    recs = []
    if current_storage_pct < 35.0 or predicted_pct < 30.0:
        recs.append("Implement Tier-1 municipal water conservation and limit non-essential bulk industrial supply.")
        recs.append("Coordinate with state irrigation division to stagger seasonal canal discharges.")
    else:
        recs.append("Maintain baseline multi-purpose release gate schedules while monitoring dry-season ramp-up.")
        recs.append("Verify canal headworks maintenance window prior to agricultural peak withdrawal.")

    if monsoon_gap < 0 or cover_days < 50:
        recs.append(f"Storage runway ({cover_days} days) faces potential pre-monsoon deficit; activate auxiliary groundwater pumping wells.")
    else:
        recs.append(f"Storage buffer provides {cover_days} days of safe operational runway; continue bi-weekly bulletin audits.")

    recs.append("Cross-reference upstream IMD radar and catchment gauges before authorizing emergency flood cushions.")

    summary = (
        f"Storage currently stands at {current_storage_pct}%, projected to reach {predicted_pct}% over the evaluation horizon. "
        f"Simulated runway provides approximately {cover_days} days of operational water cover under current withdrawal patterns."
    )

    return {
        "source": "rule_engine",
        "model": "deterministic_hydrology_matrix",
        "executive_summary": summary,
        "recommendations": recs,
    }
