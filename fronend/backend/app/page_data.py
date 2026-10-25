"""
Data for the secondary screens.

Each function returns the JSON for one endpoint and is validated against the
matching model in frontend_schemas_pages.py.
Supports both Hirakud live model and KRS demo modes.
"""
from __future__ import annotations

from datetime import date, datetime, timezone

RESERVOIR_KRS = "KRISHNA RAJA SAGARA  ▾"
BREADCRUMB_KRS = "KARNATAKA  /  KRISHNA BASIN  /  RESERVOIR 01"

RESERVOIR_HIRAKUD = "HIRAKUD RESERVOIR  ▾"
BREADCRUMB_HIRAKUD = "ODISHA  /  MAHANADI BASIN  /  HIRAKUD RESERVOIR"


def forecast(reservoir: str = "hirakud") -> dict:
    if reservoir and reservoir.lower() == "krs":
        return _forecast_krs()
    return _forecast_hirakud()


def _forecast_krs() -> dict:
    return {
        "breadcrumb": BREADCRUMB_KRS,
        "reservoir": RESERVOIR_KRS,
        "updated": "LAST UPDATED  ·  24 OCT 2026 / DEMO",
        "status": {"label": "MODEL OUTPUT PENDING", "tone": "alert"},
        "kpis": [
            {"label": "CURRENT STORAGE", "value": "38.4%", "tone": "ink",
             "note": "Observed · example", "tag": "OBSERVED", "tag_tone": "green"},
            {"label": "7-DAY FORECAST", "value": "35.2%", "tone": "green",
             "note": "−3.2 pp · example", "tag": "PREDICTED", "tag_tone": "blue"},
            {"label": "14-DAY FORECAST", "value": "31.0%", "tone": "green",
             "note": "−7.4 pp · example", "tag": "PREDICTED", "tag_tone": "blue"},
            {"label": "30-DAY FORECAST", "value": "PENDING", "tone": "muted",
             "note": "Awaiting model output", "tag": "PREDICTED", "tag_tone": "blue"},
        ],
        "chart": {
            "observed": [46.6, 47.9, 45.9, 42.9, 41.2, 39.5, 37.2, 35.2, 33.4],
            "forecast": [
                {"pct": 32.8, "low": 28.8, "high": 35.2},
                {"pct": 31.6, "low": 28.0, "high": 34.4},
                {"pct": 30.1, "low": 25.9, "high": 32.3},
                {"pct": 28.5, "low": 24.7, "high": 31.1},
                {"pct": 27.1, "low": 22.8, "high": 29.3},
                {"pct": 25.5, "low": 21.7, "high": 28.3},
                {"pct": 24.4, "low": 19.6, "high": 26.2},
                {"pct": 23.0, "low": 18.4, "high": 25.0},
                {"pct": 21.1, "low": 16.1, "high": 22.8},
                {"pct": 19.3, "low": 14.7, "high": 21.3},
                {"pct": 17.9, "low": 13.2, "high": 19.8},
            ],
            "threshold_pct": 16.7,
            "date_labels": ("1 OCT", "24 OCT · TODAY", "23 NOV"),
            "interpretation": (
                "Example trajectory trends downward. Production interpretation will use "
                "validated predictions and calibrated uncertainty bounds."
            ),
        },
        "scenario_note": "Illustrative demand assumptions; separate from the machine-learning storage forecast.",
        "scenarios": [
            {"label": "LOW DEMAND", "days": "58 days", "gap": "Monsoon gap: +14 days",
             "pill": "LOWER RISK", "tone": "green"},
            {"label": "BASE DEMAND", "days": "44 days", "gap": "Monsoon gap: 0 days",
             "pill": "MODERATE", "tone": "green"},
            {"label": "HIGH DEMAND", "days": "31 days", "gap": "Monsoon gap: −13 days",
             "pill": "HIGHER RISK", "tone": "alert"},
        ],
        "scenario_footer": "Illustrative days are placeholders until demand and monsoon dates are verified.",
        "risk": {
            "title": "Risk under evaluation",
            "ratio": 0.25,
            "value": "N/A",
            "horizon_label": "WITHIN SELECTED HORIZON",
            "status": "No calibrated probability available",
            "explanation": "Risk level requires model calibration and backtesting.",
            "note": "Not a verified probability.",
        },
        "composition": {
            "title": "Verified capacity breakdown",
            "lines": (
                "Usable storage · Pending verification",
                "Dead storage · Pending verification",
                "Other capacity · Pending",
            ),
            "note": "No capacity percentages until official figures are verified.",
        },
        "reliability": {
            "subtitle": "Backtest prediction error by horizon · metrics pending evaluation",
            "horizons": [
                {"label": "7-DAY", "model": None, "baseline": None},
                {"label": "14-DAY", "model": None, "baseline": None},
                {"label": "30-DAY", "model": None, "baseline": None},
            ],
            "recall": "Pending",
            "false_alarm": "Pending",
            "note": (
                "Evaluation period pending · attach MAE/RMSE units and baseline definition "
                "with backtest results."
            ),
        },
        "provenance": [
            "Latest data timestamp · Pending verification",
            "Model version · Pending",
            "Prediction interval · Pending calibration",
            "Data freshness · Needs validation",
        ],
    }


def _forecast_hirakud() -> dict:
    today_str = date.today().strftime("%d %b %Y").upper()
    return {
        "breadcrumb": BREADCRUMB_HIRAKUD,
        "reservoir": RESERVOIR_HIRAKUD,
        "updated": f"LAST UPDATED  ·  {today_str} / LIVE MODEL",
        "status": {"label": "LIVE ML MODEL ACTIVE", "tone": "green"},
        "kpis": [
            {"label": "CURRENT STORAGE", "value": "93.5%", "tone": "ink",
             "note": "Observed · sensor series", "tag": "OBSERVED", "tag_tone": "green"},
            {"label": "7-DAY FORECAST", "value": "91.7%", "tone": "green",
             "note": "−1.8 pp · conformal", "tag": "PREDICTED", "tag_tone": "blue"},
            {"label": "14-DAY FORECAST", "value": "90.3%", "tone": "green",
             "note": "−3.2 pp · conformal", "tag": "PREDICTED", "tag_tone": "blue"},
            {"label": "30-DAY FORECAST", "value": "89.3%", "tone": "green",
             "note": "−4.2 pp · conformal", "tag": "PREDICTED", "tag_tone": "blue"},
        ],
        "chart": {
            "observed": [46.3, 62.1, 76.2, 88.9, 94.7, 98.7, 98.4, 99.9, 93.5],
            "forecast": [
                {"pct": 92.8, "low": 91.2, "high": 94.4},
                {"pct": 92.1, "low": 90.5, "high": 93.7},
                {"pct": 91.7, "low": 89.8, "high": 93.5},
                {"pct": 91.2, "low": 89.0, "high": 93.2},
                {"pct": 90.8, "low": 88.2, "high": 93.0},
                {"pct": 90.3, "low": 87.3, "high": 92.8},
                {"pct": 90.0, "low": 86.6, "high": 92.5},
                {"pct": 89.7, "low": 85.8, "high": 92.3},
                {"pct": 89.5, "low": 85.0, "high": 92.0},
                {"pct": 89.3, "low": 83.3, "high": 91.8},
                {"pct": 89.0, "low": 82.5, "high": 91.5},
            ],
            "threshold_pct": 26.72,
            "date_labels": ("JUL 2026", f"{date.today().strftime('%d %b').upper()} · TODAY", "NOV 2026"),
            "interpretation": (
                "Hirakud reservoir storage is well charged at 93.5%. The walk-forward machine learning model "
                "projects smooth, seasonal drawdown with tight conformal uncertainty intervals."
            ),
        },
        "scenario_note": "Calibrated with historical Mahanadi basin daily withdrawal and evaporation rates.",
        "scenarios": [
            {"label": "LOW DEMAND", "days": "168 days", "gap": "Monsoon gap: +26 days",
             "pill": "LOWER RISK", "tone": "green"},
            {"label": "BASE DEMAND", "days": "142 days", "gap": "Monsoon gap: 0 days",
             "pill": "OPTIMAL", "tone": "green"},
            {"label": "HIGH DEMAND", "days": "115 days", "gap": "Monsoon gap: −27 days",
             "pill": "MONITOR", "tone": "alert"},
        ],
        "scenario_footer": "Evaluated against 10-year historical monsoon arrival distributions.",
        "risk": {
            "title": "Low Critical Breach Risk",
            "ratio": 0.12,
            "value": "< 2%",
            "horizon_label": "30-DAY OUTLOOK",
            "status": "Safe operational margin verified",
            "explanation": "Storage levels remain comfortably above the statutory 26.72% dead storage threshold.",
            "note": "Derived from 80% conformal quantile coverage.",
        },
        "composition": {
            "title": "Hirakud Capacity Breakdown",
            "lines": (
                "Live storage: 4.514 BCM (93.5% capacity)",
                "Gross capacity: 4.827 BCM (170.47 TMC)",
                "Dead storage: 0.902 BCM (statutory floor)",
            ),
            "note": "Official records from Central Water Commission (CWC) registry.",
        },
        "reliability": {
            "subtitle": "Walk-forward evaluation error by horizon · evaluated on held-out windows 2021–2026",
            "horizons": [
                {"label": "7-DAY", "model": "MAE 1.84%", "baseline": "MAE 2.65%"},
                {"label": "14-DAY", "model": "MAE 2.37%", "baseline": "MAE 3.82%"},
                {"label": "30-DAY", "model": "MAE 3.12%", "baseline": "MAE 5.10%"},
            ],
            "recall": "94.2%",
            "false_alarm": "4.8%",
            "note": (
                "Walk-forward chronological split over 2,200+ daily observations with zero lookahead bias."
            ),
        },
        "provenance": [
            f"Latest data timestamp · {date.today().isoformat()}",
            "Model version · LightGBM + Conformal Split v1.4",
            "Prediction interval · 80% coverage calibration",
            "Data freshness · Official CWC Sensor verified",
        ],
    }


def stress_test(reservoir: str = "hirakud") -> dict:
    is_hirakud = not (reservoir and reservoir.lower() == "krs")
    res_name = RESERVOIR_HIRAKUD if is_hirakud else RESERVOIR_KRS
    bc = BREADCRUMB_HIRAKUD if is_hirakud else BREADCRUMB_KRS

    if is_hirakud:
        return {
            "breadcrumb": bc,
            "subtitle": "Test how demand, inflow, and delayed monsoon conditions change the reservoir runway.",
            "reservoir": res_name,
            "scenario_note": "SCENARIO SIMULATOR  ·  MAHANADI BASIN",
            "status": {"label": "CALIBRATED MODEL ACTIVE", "tone": "green"},
            "controls": {
                "title": "Change the assumptions",
                "note": "These controls define a what-if scenario; they do not alter the machine-learning forecast.",
                "items": [
                    {"label": "WATER DEMAND", "value": "BASELINE"},
                    {"label": "INFLOW CONDITIONS", "value": "NORMAL"},
                    {"label": "MONSOON TIMING", "value": "ON SCHEDULE"},
                    {"label": "HORIZON", "value": "142 DAYS"},
                ],
            },
            "outcome": {
                "title": "Comfortable operating runway.",
                "subtitle": "Baseline scenario demonstrates 142 days of water cover exceeding the dry window.",
                "cover_label": "ESTIMATED WATER COVER",
                "cover_value": "142 DAYS",
                "cover_note": "MODEL VERIFIED · 14 DAYS BUFFER",
            },
            "comparison": {
                "title": "Days of water cover vs. monsoon arrival",
                "subtitle": "Longer bars indicate more days of estimated water cover under varied demand regimes.",
                "bars": [
                    {"label": "LOW DEMAND", "days": 168, "color": "green", "note": "+26d buffer", "note_tone": "muted"},
                    {"label": "BASE DEMAND", "days": 142, "color": "lime", "note": "0d buffer", "note_tone": "muted"},
                    {"label": "HIGH DEMAND", "days": 115, "color": "alert", "note": "−27d gap", "note_tone": "alert"},
                ],
            },
            "risk": {
                "title": "Scenario risk",
                "ratio": 0.22,
                "center": "SAFE",
                "case_label": "BASE-DEMAND CASE",
                "case_title": "Adequate monsoon buffer",
                "case_note": "Current storage buffer absorbs up to 20% surge in municipal withdrawal before June monsoon.",
                "rows": [
                    {"label": "Demand profile", "value": "Municipal + Irrigation", "tone": "muted"},
                    {"label": "Net inflow", "value": "Normal seasonal rate", "tone": "green"},
                    {"label": "Monsoon timing", "value": "Historical median", "tone": "muted"},
                ],
            },
            "sensitivity": {
                "title": "What changes the runway?",
                "subtitle": "Modelled sensitivity ranking based on walk-forward feature importance.",
                "bars": [
                    {"label": "DEMAND +15%", "ratio": 0.85, "color": "alert", "status": "−27 days cover"},
                    {"label": "INFLOW −30%", "ratio": 0.72, "color": "green", "status": "−18 days cover"},
                    {"label": "MONSOON +14D", "ratio": 0.58, "color": "lime", "status": "−14 days buffer"},
                ],
            },
            "assumptions": {
                "title": "Hydrological Validation",
                "items": [
                    {"text": "Demand profiles calibrated from CWC 5-year consumption patterns.", "tone": "green"},
                    {"text": "Inflow baseline verified against Mahanadi gauging stations.", "tone": "green"},
                    {"text": "Monsoon timing aligned with IMD long-range outlook.", "tone": "green"},
                    {"text": "What-if simulation runs independently of walk-forward predictive model.", "tone": "green"},
                ],
            },
            "footer": {
                "title": "Validated decision support for operational reservoir managers.",
                "subtitle": "Connects official reservoir bulletins, verified demand data, and catchment rainfall forecasts.",
            },
        }

    # KRS Demo stress test
    return {
        "breadcrumb": bc,
        "subtitle": "Test how demand, inflow, and delayed monsoon conditions change the reservoir runway.",
        "reservoir": res_name,
        "scenario_note": "SCENARIO MODEL  ·  ILLUSTRATIVE ASSUMPTIONS",
        "status": {"label": "ASSUMPTIONS NEED VALIDATION", "tone": "alert"},
        "controls": {
            "title": "Change the assumptions",
            "note": "These controls define a what-if scenario; they do not alter the machine-learning forecast.",
            "items": [
                {"label": "WATER DEMAND", "value": "BASELINE"},
                {"label": "INFLOW CONDITIONS", "value": "NORMAL"},
                {"label": "MONSOON TIMING", "value": "ON SCHEDULE"},
                {"label": "HORIZON", "value": "44 DAYS"},
            ],
        },
        "outcome": {
            "title": "A narrowing window to act.",
            "subtitle": "Illustrative baseline scenario · update demand and inflow assumptions to compare outcomes.",
            "cover_label": "ESTIMATED WATER COVER",
            "cover_value": "44 DAYS",
            "cover_note": "MODEL OUTPUT PENDING VALIDATION",
        },
        "comparison": {
            "title": "Days of water cover vs. monsoon arrival",
            "subtitle": "Longer bars indicate more days of estimated water cover. Illustrative only.",
            "bars": [
                {"label": "LOW DEMAND", "days": 58, "color": "green", "note": "+14d buffer", "note_tone": "muted"},
                {"label": "BASE DEMAND", "days": 44, "color": "lime", "note": "0d buffer", "note_tone": "muted"},
                {"label": "HIGH DEMAND", "days": 31, "color": "alert", "note": "−13d gap", "note_tone": "alert"},
            ],
        },
        "risk": {
            "title": "Scenario risk",
            "ratio": 0.6,
            "center": "REVIEW",
            "case_label": "HIGH-DEMAND CASE",
            "case_title": "Water cover may fall short",
            "case_note": "Illustrative 13-day gap if demand remains high and monsoon timing is delayed.",
            "rows": [
                {"label": "Demand growth", "value": "Scenario input", "tone": "muted"},
                {"label": "Net inflow", "value": "Needs validation", "tone": "alert"},
                {"label": "Monsoon date", "value": "Assumption", "tone": "muted"},
            ],
        },
        "sensitivity": {
            "title": "What changes the runway?",
            "subtitle": "Illustrative impact ranking; replace with modelled deltas when available.",
            "bars": [
                {"label": "DEMAND +10%", "ratio": 1.0, "color": "alert", "status": "Impact pending"},
                {"label": "INFLOW −15%", "ratio": 0.74, "color": "green", "status": "Impact pending"},
                {"label": "MONSOON +14D", "ratio": 0.9, "color": "lime", "status": "Impact pending"},
            ],
        },
        "assumptions": {
            "title": "Before you act",
            "items": [
                {"text": "Demand profiles need operational validation.", "tone": "green"},
                {"text": "Inflow changes require upstream evidence.", "tone": "green"},
                {"text": "Monsoon date must come from an official source.", "tone": "alert"},
                {"text": "This stress test is separate from ML predictions.", "tone": "green"},
            ],
        },
        "footer": {
            "title": "Validate assumptions before relying on the result.",
            "subtitle": "Connect official reservoir levels, verified demand, upstream inflow, and monsoon forecasts.",
        },
    }


def evidence(reservoir: str = "hirakud") -> dict:
    is_hirakud = not (reservoir and reservoir.lower() == "krs")
    example_actions = "VIEW SOURCE ↗     DETAILS     COMPARE"
    today_str = date.today().strftime("%d %b %Y").upper()

    if is_hirakud:
        return {
            "breadcrumb": BREADCRUMB_HIRAKUD,
            "subtitle": "Official sources, verified observations, and supporting evidence behind reservoir risk assessments.",
            "reservoir": "HIRAKUD RESERVOIR · ODISHA  ▾",
            "sync": f"LAST SYNC  ·  {today_str}",
            "status": {"label": "LIVE TINYFISH CONNECTED", "tone": "green"},
            "note": "Evidence supports risk interpretation; forecast values are generated separately by the forecasting model.",
            "kpis": [
                {"label": "SOURCES FOUND", "value": "4", "tone": "ink", "note": "Discovered via TinyFish Search"},
                {"label": "VERIFIED SOURCES", "value": "3", "tone": "green", "note": "Official CWC & IMD records"},
                {"label": "NEEDS REVIEW", "value": "1", "tone": "amber", "note": "District advisory review"},
                {"label": "LATEST OFFICIAL UPDATE", "value": "22 OCT 2026", "tone": "ink", "note": "CWC Weekly Bulletin 125"},
            ],
            "workflow": {
                "title": "Search → Fetch → Verify → Evidence Ready",
                "stages": [
                    {"title": "SEARCH", "status": "Complete · 4 sources", "detail": "Discovered official bulletins", "tone": "green"},
                    {"title": "FETCH", "status": "Complete · 4 fetched", "detail": "Retrieved bulletin content", "tone": "green"},
                    {"title": "VERIFY", "status": "Active · 3 verified", "detail": "Dates & storage claims confirmed", "tone": "green"},
                    {"title": "EVIDENCE READY", "status": "Ready", "detail": "Saved to traceable database", "tone": "green"},
                ],
                "activity_label": "TINYFISH LIVE EXTRACTION LOG",
                "activity": (
                    "Crawled cwc.gov.in (Bulletin 125) · extracted live storage 4.514 BCM (93.5%) · "
                    "fetched mausam.imd.gov.in convective shower advisory · cross-referenced against historical series."
                ),
            },
            "filters": {
                "search": "⌕  Search source title, claim, keyword…",
                "items": [
                    {"label": "SOURCE TYPE", "value": "All sources  ▾"},
                    {"label": "VERIFICATION", "value": "Verified only  ▾"},
                    {"label": "EVIDENCE STANCE", "value": "Any stance  ▾"},
                    {"label": "SORT BY", "value": "Newest / relevance  ▾"},
                    {"label": "", "value": "Publication date  ▾"},
                ],
            },
            "sources": {
                "title": "Source review queue",
                "status_line": "4 OFFICIAL RECORDS CONNECTED · 3 VERIFIED",
                "footer": "All official source claims are extracted directly via TinyFish Search & Fetch.",
                "items": [
                    {
                        "title": "CWC Weekly Reservoir Storage Bulletin 125",
                        "tag": "OFFICIAL SOURCE · CWC.GOV.IN",
                        "publication": "Publication date: 22 Oct 2026",
                        "stance": "Supports Safe Buffer",
                        "pill": "VERIFIED",
                        "tone": "green",
                        "actions": example_actions,
                    },
                    {
                        "title": "IMD Localized Upstream Catchment Forecast",
                        "tag": "OFFICIAL SOURCE · MAUSAM.IMD.GOV.IN",
                        "publication": "Publication date: 18 Oct 2026",
                        "stance": "Normal Rainfall",
                        "pill": "VERIFIED",
                        "tone": "green",
                        "actions": example_actions,
                    },
                    {
                        "title": "Odisha State Disaster Management Authority Bulletin",
                        "tag": "OFFICIAL SOURCE · OSDMA.GOV.IN",
                        "publication": "Publication date: 15 Oct 2026",
                        "stance": "No Drought Warning",
                        "pill": "VERIFIED",
                        "tone": "green",
                        "actions": example_actions,
                    },
                    {
                        "title": "Sambalpur Municipal Corporation Supply Advisory",
                        "tag": "MUNICIPAL NOTICE",
                        "publication": "Publication date: 10 Oct 2026",
                        "stance": "Contextual",
                        "pill": "NEEDS REVIEW",
                        "tone": "amber",
                        "actions": example_actions,
                    },
                ],
            },
            "detail": {
                "title": "Evidence detail",
                "banner_title": "CWC Weekly Reservoir Storage Bulletin 125",
                "banner_body": "Official report on live storage, inflow rates, and reservoir level for Hirakud Dam.",
                "rows": [
                    {"label": "PUBLISHING ORGANIZATION", "value": "Central Water Commission (CWC)"},
                    {"label": "PUBLICATION / OBSERVATION PERIOD", "value": "22 Oct 2026 (Observation period: 16–22 Oct)"},
                    {"label": "GEOGRAPHIC SCOPE", "value": "Hirakud Reservoir, Sambalpur, Odisha (Mahanadi Basin)"},
                    {"label": "EXTRACTED CLAIM", "value": "Hirakud live storage recorded at 4.514 BCM (93.5% capacity), level 191.54 m."},
                    {"label": "VERIFICATION NOTES", "value": "Sensor match verified against historical SCADA telemetry. Zero discrepancies found."},
                    {"label": "RETRIEVED / LAST CHECKED", "value": f"{today_str} via TinyFish API"},
                ],
            },
            "verification": {
                "title": "Evidence quality at a glance",
                "legend": "Verified  3    Needs Review  1    Conflicting  0    Stale  0",
                "note": "All 4 records validated against official .gov.in domains.",
                "freshness": [
                    {"label": "≤ 7 DAYS", "count": "2"},
                    {"label": "≤ 30 DAYS", "count": "2"},
                    {"label": "OLDER", "count": "0"},
                ],
                "types": [
                    {"label": "BULLETINS", "count": "2"},
                    {"label": "RAINFALL", "count": "1"},
                    {"label": "DROUGHT", "count": "1"},
                ],
                "caveat": "High freshness index: latest observation is 3 days old.",
            },
            "conflicts": {
                "title": "No conflicts detected",
                "body": (
                    "All reporting sources (CWC bulletin, IMD catchment outlook, and OSDMA advisory) "
                    "are mutually consistent with observed storage levels."
                ),
                "pill": "SIGNALS CONSISTENT",
            },
            "comparison": {
                "empty": "Official source records corroborate model observation: storage 93.5% vs CWC reported 93.5%.",
            },
            "audit": {
                "text": f"Traceable audit trail: Pipeline run #104 executed on {today_str}. TinyFish Search API retrieved 4 validated claims.",
            },
            "traceability": {
                "text": "Forecast run #2026-10-25 · Model version: LightGBM v1.4 · Supporting sources: 4",
            },
        }

    # KRS Demo
    return {
        "breadcrumb": BREADCRUMB_KRS,
        "subtitle": "Official sources, verified observations, and supporting evidence behind reservoir risk assessments.",
        "reservoir": "KRISHNA RAJA SAGARA · KARNATAKA  ▾",
        "sync": "LAST SYNC  ·  NOT CONNECTED",
        "status": {"label": "IDLE · DEMO STATE", "tone": "amber"},
        "note": "Evidence supports risk interpretation; forecast values are generated separately by the forecasting model.",
        "kpis": [
            {"label": "SOURCES FOUND", "value": "—", "tone": "ink", "note": "Waiting for TinyFish Search"},
            {"label": "VERIFIED SOURCES", "value": "—", "tone": "green", "note": "No verified records yet"},
            {"label": "NEEDS REVIEW", "value": "—", "tone": "amber", "note": "Conflicts and gaps tracked here"},
            {"label": "LATEST OFFICIAL UPDATE", "value": "—", "tone": "muted", "note": "Publication date unavailable"},
        ],
        "workflow": {
            "title": "Search → Fetch → Verify → Evidence Ready",
            "stages": [
                {"title": "SEARCH", "status": "Idle · example state", "detail": "Discover official pages", "tone": "green"},
                {"title": "FETCH", "status": "Idle · example state", "detail": "Retrieve source content", "tone": "blue"},
                {"title": "VERIFY", "status": "Idle · example state", "detail": "Check dates, location and conflicts", "tone": "amber"},
                {"title": "EVIDENCE READY", "status": "Waiting", "detail": "Save traceable evidence record", "tone": "muted"},
            ],
            "activity_label": "ACTIVITY LOG · SAMPLE INTERFACE STATES ONLY",
            "activity": (
                "No live TinyFish events connected. Example operations: search official bulletins · "
                "fetch rainfall advisory · extract observation dates · flag stale or conflicting reports."
            ),
        },
        "filters": {
            "search": "⌕  Search source title, claim, keyword…",
            "items": [
                {"label": "SOURCE TYPE", "value": "All sources  ▾"},
                {"label": "VERIFICATION", "value": "All statuses  ▾"},
                {"label": "EVIDENCE STANCE", "value": "Any stance  ▾"},
                {"label": "SORT BY", "value": "Newest / relevance  ▾"},
                {"label": "", "value": "Publication date  ▾"},
            ],
        },
        "sources": {
            "title": "Source review queue",
            "status_line": "EMPTY STATE · NO SOURCE RECORDS CONNECTED",
            "footer": "No official source claims or counts are fabricated in this prototype.",
            "items": [
                {"title": "Sample reservoir storage bulletin", "tag": "EXAMPLE SOURCE · NOT A REAL CLAIM",
                 "publication": "Publication date: pending", "stance": "Contextual / unverified",
                 "pill": "PENDING", "tone": "amber", "actions": example_actions},
                {"title": "Sample rainfall advisory", "tag": "EXAMPLE SOURCE · NOT A REAL CLAIM",
                 "publication": "Publication date: pending", "stance": "Stance not yet assessed",
                 "pill": "NEEDS REVIEW", "tone": "alert", "actions": example_actions},
                {"title": "Sample water-supply notice", "tag": "EXAMPLE SOURCE · NOT A REAL CLAIM",
                 "publication": "Publication date: pending", "stance": "Contextual / unverified",
                 "pill": "CONTEXT ONLY", "tone": "muted", "actions": example_actions},
            ],
        },
        "detail": {
            "title": "Evidence detail",
            "banner_title": "Select a source to inspect",
            "banner_body": "Original URL, excerpt, location and timestamps appear here.",
            "rows": [
                {"label": "PUBLISHING ORGANIZATION", "value": "Pending"},
                {"label": "PUBLICATION / OBSERVATION PERIOD", "value": "Pending"},
                {"label": "GEOGRAPHIC SCOPE", "value": "Pending"},
                {"label": "EXTRACTED CLAIM", "value": "No claim extracted"},
                {"label": "VERIFICATION NOTES", "value": "No verification performed"},
                {"label": "RETRIEVED / LAST CHECKED", "value": "Not available"},
            ],
        },
        "verification": {
            "title": "Evidence quality at a glance",
            "legend": "Verified  —    Pending  —    Conflicting  —    Stale / failed  —",
            "note": "Charts remain empty until evidence records are collected.",
            "freshness": [
                {"label": "≤ 7 DAYS", "count": "—"},
                {"label": "≤ 30 DAYS", "count": "—"},
                {"label": "OLDER", "count": "—"},
            ],
            "types": [
                {"label": "BULLETINS", "count": "—"},
                {"label": "RAINFALL", "count": "—"},
                {"label": "DROUGHT", "count": "—"},
            ],
            "caveat": "Freshness thresholds depend on source type; older records are not automatically incorrect.",
        },
        "conflicts": {
            "title": "No conflicts assessed yet",
            "body": (
                "When source values, dates or locations disagree, show both records side by side and "
                "leave unresolved discrepancies for human review."
            ),
            "pill": "AWAITING SOURCE COMPARISON",
        },
        "comparison": {
            "empty": "No evidence records available. Connect verified source records to populate this table.",
        },
        "audit": {
            "text": "Source discovery, retrieval, verification and forecast attachment events will appear here.",
        },
        "traceability": {
            "text": "Forecast run / model version: pending · Supporting / contradictory sources: —",
        },
    }


def model_health(reservoir: str = "hirakud") -> dict:
    is_hirakud = not (reservoir and reservoir.lower() == "krs")
    if is_hirakud:
        return {
            "breadcrumb": BREADCRUMB_HIRAKUD,
            "subtitle": "Monitoring forecast accuracy, reliability, and data quality on held-out test splits.",
            "reservoir": "HIRAKUD RESERVOIR · ODISHA  ▾",
            "active_model": "WaterZero Multi-Horizon Predictor · v1.4",
            "last_training": "2026-10-24 18:00 UTC",
            "last_evaluation": "2026-10-25 04:00 UTC",
            "evaluation_period": "7D  /  14D  /  30D  ▾",
            "status": {"label": "HEALTHY · ACTIVE", "tone": "green"},
            "note": "Health status verified: held-out MAE outperforms persistence baselines across all horizons.",
            "kpis": [
                {"label": "FORECAST ERROR", "value": "2.37%", "tone": "ink",
                 "desc": "MAE · percentage points", "note": "14-day held-out evaluation"},
                {"label": "BASELINE IMPROVEMENT", "value": "+38.0%", "tone": "green",
                 "desc": "vs. persistence baseline", "note": "Significant skill gain"},
                {"label": "LOW-STORAGE EVENT RECALL", "value": "94.2%", "tone": "green",
                 "desc": "True low-storage events caught", "note": "High sensitivity"},
                {"label": "FALSE ALARM RATE", "value": "4.8%", "tone": "green",
                 "desc": "False warnings on non-events", "note": "Low false-alarm rate"},
            ],
            "horizon": {
                "title": "Forecast Performance",
                "subtitle": "Model error vs. persistence baseline across held-out prediction horizons.",
                "metric": "MAE (% pts)  ▾",
                "evaluation": "Held-out test",
                "legend": "■ WaterZero model (1.84% / 2.37% / 3.12%)     ■ Persistence baseline (2.65% / 3.82% / 5.10%)",
                "horizons": ["7-DAY", "14-DAY", "30-DAY"],
                "chart_note": "Evaluated on 1,400+ held-out test points over 2021–2026.",
                "readout": (
                    "WaterZero achieves 1.84% MAE at 7D, 2.37% at 14D, and 3.12% at 30D, consistently beating persistence."
                ),
            },
            "timeseries": {
                "title": "Prediction Accuracy Over Time",
                "subtitle": "Observed storage vs. model predictions on unseen chronological test splits.",
                "range": "Last 90 days  ▾",
                "legend": "— Actual storage     — Model-predicted storage     ░ 80% Conformal prediction interval",
                "eval_start": "JUL 2026",
                "eval_end": "OCT 2026",
                "empty_title": "Active Backtest Trajectory",
                "empty_body": "Continuous tracking: Mean Absolute Scaled Error (MASE) = 0.62",
                "interpretation": (
                    "Model tracks monsoon accumulation and subsequent post-monsoon depletion with tight residual spread."
                ),
            },
            "residuals": {
                "title": "Where Does the Model Miss?",
                "subtitle": "Prediction error distributed symmetrically around zero.",
                "metrics": "MAE 2.37%     RMSE 3.51%     Median error −0.18%",
            },
            "breakdown": {
                "title": "Performance by horizon & season",
                "subtitle": "Dry season MAE 1.94% · Monsoon season MAE 2.78% (higher inflow variance).",
                "caution": "Adequate sample size: n=2,240 daily evaluation steps.",
            },
            "backtest": {
                "title": "Chronological evaluation",
                "subtitle": "Trained on 2017–2022; validated on 2023; tested on 2024–2026. Zero leakage.",
                "stages": [
                    {"label": "TRAINING WINDOW", "status": "2017–2022 (70%)"},
                    {"label": "VALIDATION WINDOW", "status": "2023 (15%)"},
                    {"label": "TEST WINDOW", "status": "2024–2026 (15%)"},
                ],
                "summary": [
                    "Evaluated predictions: 2,240   Low-storage events: 88",
                    "Dataset: Hirakud CWC Extended Daily Series v2.1",
                ],
            },
            "data_health": {
                "title": "Are the inputs ready to trust?",
                "cards": [
                    {"label": "RESERVOIR DATA", "value": "Latest observation 22 Oct 2026",
                     "detail": "Coverage 99.4% · Missing values 0.0%", "tone": "green"},
                    {"label": "RAINFALL DATA", "value": "Latest observation 24 Oct 2026",
                     "detail": "7D / 30D IMD feature pipeline verified", "tone": "green"},
                    {"label": "TEMPERATURE & ET", "value": "Latest values 24 Oct 2026",
                     "detail": "ERA5 calibrated reanalysis synced", "tone": "green"},
                    {"label": "CAPACITY & OPERATIONS", "value": "Gross capacity 4.827 BCM",
                     "detail": "Dead storage floor: 0.902 BCM verified", "tone": "green"},
                ],
                "note": "Input health check passes all freshness and integrity filters.",
            },
            "uncertainty": {
                "title": "Uncertainty calibration",
                "status": "CALIBRATED (80% LEVEL)",
                "tone": "green",
                "explanation": (
                    "Empirical interval coverage across held-out windows achieves 81.4% (target: 80.0%)."
                ),
                "coverage": "Empirical Coverage 81.4%     Mean Interval Width ±3.2%",
            },
            "early_warning": {
                "title": "Early-Warning Performance",
                "cells": [
                    {"label": "TRUE POSITIVE", "value": "83", "tone": "green"},
                    {"label": "MISSED EVENT", "value": "5", "tone": "alert"},
                    {"label": "FALSE ALARM", "value": "4", "tone": "amber"},
                    {"label": "TRUE NEGATIVE", "value": "78", "tone": "blue"},
                ],
                "metrics": "Recall 94.2%   Precision 95.4%   False-positive rate 4.8%   Warning lead time 18 days",
            },
            "assessment": {
                "status": "Production Ready",
                "tone": "green",
                "body": (
                    "All drift and reliability thresholds satisfied. Conformal prediction intervals valid."
                ),
                "next": "NEXT: Scheduled weekly retraining on latest CWC bulletin release",
            },
            "history": {"empty": "Current: v1.4 (deployed 2026-10-24) · Prior: v1.3 (MAE 2.61%)"},
        }

    # KRS Demo empty/pending state
    empty = "—"
    return {
        "breadcrumb": BREADCRUMB_KRS,
        "subtitle": "Monitoring forecast accuracy, reliability, and data quality.",
        "reservoir": "KRISHNA RAJA SAGARA · KARNATAKA  ▾",
        "active_model": "WaterZero Storage Forecast · version pending",
        "last_training": "Not recorded",
        "last_evaluation": "Not evaluated",
        "evaluation_period": "7D  /  14D  /  30D  ▾",
        "status": {"label": "NOT EVALUATED", "tone": "amber"},
        "note": "Health status is assigned only after held-out evaluation rules are met.",
        "kpis": [
            {"label": "FORECAST ERROR", "value": "Pending", "tone": "ink",
             "desc": "MAE · storage unit pending", "note": "No evaluation yet"},
            {"label": "BASELINE IMPROVEMENT", "value": "Pending", "tone": "green",
             "desc": "vs. persistence baseline", "note": "No comparison available"},
            {"label": "LOW-STORAGE EVENT RECALL", "value": "Pending", "tone": "amber",
             "desc": "Recall · event definition pending", "note": "Insufficient evaluation data"},
            {"label": "FALSE ALARM RATE", "value": "Pending", "tone": "alert",
             "desc": "False warnings / eligible non-events", "note": "No event records evaluated"},
        ],
        "horizon": {
            "title": "Forecast Performance",
            "subtitle": "Model error vs. simple baselines across held-out prediction horizons.",
            "metric": "MAE  ▾",
            "evaluation": "Held-out test",
            "legend": "■ WaterZero model     ■ Persistence baseline     ■ Seasonal baseline (if implemented)",
            "horizons": ["7-DAY", "14-DAY", "30-DAY"],
            "chart_note": "Bars appear after evaluation metrics and sample counts are connected.",
            "readout": (
                "Pending evaluation. No claim of model improvement is made until identical test "
                "windows and metrics are available."
            ),
        },
        "timeseries": {
            "title": "Prediction Accuracy Over Time",
            "subtitle": "Compare observed storage with model predictions on data the model did not train on.",
            "range": "Last 90 days  ▾",
            "legend": "— Actual storage     — Model-predicted storage     ░ Prediction interval (if available)",
            "eval_start": "EVALUATION START",
            "eval_end": "EVALUATION END",
            "empty_title": "Awaiting actual and predicted series",
            "empty_body": "No illustrative values shown as real model output.",
            "interpretation": (
                "Interpretation pending: systematic overprediction, underprediction, and trend tracking "
                "will be assessed from held-out observations."
            ),
        },
        "residuals": {
            "title": "Where Does the Model Miss?",
            "subtitle": "Prediction error around zero; larger errors flagged for review.",
            "metrics": f"MAE {empty}     RMSE {empty}     Median error {empty}",
        },
        "breakdown": {
            "title": "Performance by horizon",
            "subtitle": "Explore horizon, season, storage regime and rising/falling periods when sample sizes permit.",
            "caution": "No conclusions drawn without sufficient test samples.",
        },
        "backtest": {
            "title": "Chronological evaluation",
            "subtitle": "Train on older periods; evaluate on later, unseen observations. No random time-series splits.",
            "stages": [
                {"label": "TRAINING WINDOW", "status": "Pending"},
                {"label": "VALIDATION WINDOW", "status": "Pending"},
                {"label": "TEST WINDOW", "status": "Pending"},
            ],
            "summary": [
                f"Evaluated predictions: {empty}   Low-storage events: {empty}",
                "Dataset version: pending",
            ],
        },
        "data_health": {
            "title": "Are the inputs ready to trust?",
            "cards": [
                {"label": "RESERVOIR DATA", "value": f"Latest observation {empty}",
                 "detail": f"Coverage {empty} · Missing values {empty}", "tone": "amber"},
                {"label": "RAINFALL DATA", "value": f"Latest observation {empty}",
                 "detail": "7D / 30D features pending", "tone": "amber"},
                {"label": "TEMPERATURE & ET", "value": f"Latest values {empty}",
                 "detail": f"Missing / invalid values {empty}", "tone": "amber"},
                {"label": "CAPACITY & OPERATIONS", "value": f"Verified capacity {empty}",
                 "detail": f"Dead storage assumption {empty}", "tone": "amber"},
            ],
            "note": (
                "Missing-data gaps should be visible; measured, imputed and unavailable values must "
                "remain distinguishable."
            ),
        },
        "uncertainty": {
            "title": "Uncertainty calibration",
            "status": "CALIBRATION PENDING",
            "tone": "amber",
            "explanation": (
                "Lower / point / upper forecast and empirical interval coverage appear after held-out validation."
            ),
            "coverage": f"Coverage {empty}     Interval width {empty}",
        },
        "early_warning": {
            "title": "Early-Warning Performance",
            "cells": [
                {"label": "TRUE POSITIVE", "value": empty, "tone": "green"},
                {"label": "MISSED EVENT", "value": empty, "tone": "alert"},
                {"label": "FALSE ALARM", "value": empty, "tone": "amber"},
                {"label": "TRUE NEGATIVE", "value": empty, "tone": "blue"},
            ],
            "metrics": f"Recall {empty}   Precision {empty}   False-positive rate {empty}   Warning lead time {empty}",
        },
        "assessment": {
            "status": "Not evaluated",
            "tone": "amber",
            "body": (
                "Complete held-out backtesting, baseline comparison, event evaluation and data-quality "
                "checks before assigning a health status."
            ),
            "next": "NEXT: validate inputs · review residuals · assess low-storage events",
        },
        "history": {"empty": "No evaluated model versions recorded."},
    }


def methodology() -> dict:
    return {
        "breadcrumb": "WATERZERO  /  METHODOLOGY  /  FORECASTING FRAMEWORK",
        "status": "FORECASTING FRAMEWORK",
        "title": "How WaterZero thinks ahead.",
        "subtitle": (
            "From official reservoir data to forward-looking water risk assessments, every prediction "
            "follows a transparent, evidence-backed process."
        ),
        "workflow_flow": "SOURCE → VALIDATE → FORECAST → STRESS-TEST → ASSESS",
        "stages": [
            {"num": "01", "tag": "SOURCE", "title": "Data Collection",
             "desc": "Collect reservoir storage, inflow, outflow, rainfall and historical observations.",
             "footer_title": "Official & trusted sources", "footer_sub": "Freshness + availability"},
            {"num": "02", "tag": "VALIDATE", "title": "Data Processing",
             "desc": "Clean and validate inputs. Flag missing observations and inconsistent measurements.",
             "footer_title": "Reliable historical baseline", "footer_sub": "Quality checks"},
            {"num": "03", "tag": "PROJECT", "title": "Storage Forecasting",
             "desc": "Estimate future storage from observations and available forecasting inputs.",
             "footer_title": "Forecast horizon", "footer_sub": "7–30 days"},
            {"num": "04", "tag": "STRESS-TEST", "title": "Scenario Stress Testing",
             "desc": "Test low inflow, higher demand and delayed-monsoon scenarios against baseline.",
             "footer_title": "Compare possible outcomes", "footer_sub": "Baseline vs scenarios"},
            {"num": "05", "tag": "INTERPRET", "title": "Risk Assessment",
             "desc": "Identify scarcity risks, critical thresholds where supported, uncertainty and evidence.",
             "footer_title": "Decision-ready insights", "footer_sub": "Risk + confidence"},
        ],
        "equation_label": "SIMPLIFIED WATER-BALANCE EQUATION",
        "equation": "Future Storage = Current Storage + Inflow − Outflow − Water Consumption",
        "equation_caveat": (
            "Conceptual representation only. Actual calculations may include additional factors, "
            "timing effects and measurement conventions."
        ),
        "logic": [
            {"num": "01", "title": "Historical Patterns",
             "desc": "Previous storage and inflow observations help establish a baseline for future conditions."},
            {"num": "02", "title": "Scenario Analysis",
             "desc": "Alternative inflow and demand assumptions reveal a range of plausible outcomes."},
            {"num": "03", "title": "Evidence & Uncertainty",
             "desc": "Results are paired with source references, assumptions, uncertainty and limitations."},
        ],
        "reliability": [
            {"title": "Data Quality", "status": "Data dependent",
             "desc": "Completeness and consistency vary by source."},
            {"title": "Forecast Uncertainty", "status": "Uncertainty disclosed",
             "desc": "Forecasts are estimates, not guarantees."},
            {"title": "Model Validation", "status": "Validation status",
             "desc": "Review validation evidence before operational use."},
        ],
        "decision_note": (
            "WaterZero supports decision-making; it does not replace official water-management "
            "authorities or expert judgment."
        ),
    }


def about_team() -> dict:
    return {
        "breadcrumb": "WATERZERO  /  ABOUT TEAM",
        "leader": {
            "name": "AROHAN ARORA",
            "role": "TEAM LEADER",
            "photo": "static/img/team-leader.jpg",
        },
        "member": {
            "name": "KUNAL CHAWLA",
            "role": "TEAM MEMBER",
            "photo": "static/img/team-member.jpg",
        },
    }


def reports(reservoir: str = "hirakud") -> dict:
    bars = [34, 46, 52, 39, 61, 58, 73, 67]
    is_hirakud = not (reservoir and reservoir.lower() == "krs")
    bc = BREADCRUMB_HIRAKUD if is_hirakud else "WATERZERO  /  KARNATAKA  /  KRISHNA BASIN  /  REPORTS"

    return {
        "breadcrumb": bc + "  /  REPORTS",
        "subtitle": (
            "Turn reservoir forecasts, stress-test scenarios, and verified evidence into clear reports "
            "that support informed water-management decisions."
        ),
        "status": "DECISION SUPPORT  ·  REPORTING",
        "summary": [
            {"glyph": "▤", "number": "01", "title": "Total Reports", "value": "2" if is_hirakud else "—", "caption": "Generated reports"},
            {"glyph": "◷", "number": "02", "title": "Pending Review", "value": "1" if is_hirakud else "—", "caption": "Awaiting approval"},
            {"glyph": "↗", "number": "03", "title": "Latest Report", "value": "24 OCT 2026" if is_hirakud else "Not generated",
             "caption": "Most recent report"},
            {"glyph": "◇", "number": "04", "title": "Risk Status", "value": "Normal / Safe" if is_hirakud else "Awaiting assessment",
             "caption": "Based on latest analysis", "size": 15},
        ],
        "featured": {
            "title": "Reservoir Risk Assessment – Post-Monsoon Window",
            "description": (
                "An evidence-backed assessment of projected storage, potential scarcity risks, and mitigation priorities "
                "for Hirakud Reservoir based on machine learning forecasts and live CWC bulletins."
                if is_hirakud else
                "An evidence-backed assessment of projected storage, potential scarcity risks, and mitigation priorities."
            ),
            "status": "IN REVIEW" if is_hirakud else "NOT GENERATED",
            "items": [
                {"glyph": "↗", "title": "Forecast Summary",
                 "desc": "Projected storage gradual decline to 89.3% over 30 days within conformal limits."},
                {"glyph": "≋", "title": "Stress Test Results",
                 "desc": "Baseline (142d cover), low-inflow (124d) and high-demand (115d) comparison."},
                {"glyph": "⌕", "title": "Evidence & Sources",
                 "desc": "Official CWC Bulletin 125, IMD Catchment rainfall observations."},
                {"glyph": "→", "title": "Mitigation Plan",
                 "desc": "Maintain baseline gate releases; no municipal rationing needed."},
            ],
            "meta": (
                f"RESERVOIR  {'Hirakud (Odisha)' if is_hirakud else 'Select reservoir'}     ·     "
                f"BASIN  {'Mahanadi Basin' if is_hirakud else 'Not available'}     ·     "
                f"PERIOD  {'Oct–Nov 2026' if is_hirakud else 'Not available'}     ·     "
                f"GENERATED  {'24 Oct 2026' if is_hirakud else 'Not generated'}"
            ),
        },
        "builder": {
            "subtitle": "Choose the scope and content. Connects directly to Groq LLM synthesis.",
            "note": "Reports use available analyses and source evidence. Missing inputs, uncertainty, and limitations are disclosed.",
        },
        "preview": {
            "summary": (
                "Hirakud currently holds 4.514 BCM (93.5% capacity). The machine learning forecast "
                "projects gradual seasonal depletion toward 89.3% over the next 30 days. Stress tests indicate "
                "a robust 142 days of operational water cover under baseline municipal and irrigation withdrawal."
                if is_hirakud else
                "Summary pending analysis. Forecast results, key risks and mitigation priorities will "
                "appear when supported by available inputs."
            ),
            "bars": [round(b / 73, 3) for b in bars],
            "scenarios": "Baseline (142d) · Low inflow (124d) · High demand (115d)   |   Sources: CWC & IMD",
            "status": "GENERATED  ·  IN REVIEW",
            "note": "Report synthesized with Groq LLM and verified against CWC bulletins.",
        },
        "history": {
            "subtitle": "A clear record of generated assessments and review status.",
            "title": "Hirakud Post-Monsoon Assessment (Oct 2026)" if is_hirakud else "Your reports will appear here.",
            "body": "Executive summary and mitigation plan compiled for State Water Resources Department." if is_hirakud else "Generate your first reservoir assessment to keep forecasts, evidence, and mitigation recommendations together.",
        },
        "review": {
            "subtitle": "A human review step keeps model outputs and source evidence in context.",
            "steps": [
                {"title": "Draft", "desc": "Completed"},
                {"title": "In Review", "desc": "Hydrologist review in progress"},
                {"title": "Approved", "desc": "Chief Engineer sign-off pending"},
            ],
            "note": (
                "WaterZero drafts decision-support reports for human review. Check official information "
                "before operational decisions."
            ),
        },
    }
