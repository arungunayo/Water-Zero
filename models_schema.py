from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal
from pydantic import BaseModel, Field


# -------------------------------------------------------------
# Reservoir & General Info
# -------------------------------------------------------------
class ReservoirInfo(BaseModel):
    id: str = "hirakud"
    name: str = "Hirakud Reservoir"
    state: str = "Odisha"
    district: str = "Sambalpur"
    river_basin: str = "Mahanadi Basin"
    lat: float = 21.53
    lon: float = 83.87
    gross_capacity_bcm: float = 4.827
    gross_capacity_tmc: float = 170.47
    dead_storage_bcm: float = 0.902
    warning_threshold_pct: float = 26.72
    is_active_model: bool = True


# -------------------------------------------------------------
# 01 Top Nav Insight Blocks
# -------------------------------------------------------------
class TopInsightsResponse(BaseModel):
    reservoir: str
    state: str
    basin: str
    current_storage_pct: float
    current_storage_bcm: float
    gross_capacity_bcm: float
    outlook_30d_pct: float
    outlook_30d_delta_pct: float
    outlook_30d_range: tuple[float, float]
    stress_test_cover_days: int
    stress_test_monsoon_gap_days: int
    evidence_verified_count: int
    evidence_stale_count: int
    evidence_pending_count: int
    model_mae_pts: float
    model_rmse_pts: float
    sparkline_history: list[dict[str, Any]]
    reliability_bars: list[dict[str, Any]]


# -------------------------------------------------------------
# 02 Overview Screen
# -------------------------------------------------------------
class OverviewResponse(BaseModel):
    reservoir: ReservoirInfo
    live_storage: dict[str, Any]
    storage_trajectory: dict[str, Any]
    threshold_watch: dict[str, Any]
    decision_lab_summary: dict[str, Any]
    evidence_signals_preview: list[dict[str, Any]]


# -------------------------------------------------------------
# 03 Storage Forecast Screen
# -------------------------------------------------------------
class ForecastHorizonCard(BaseModel):
    horizon_weeks: int
    horizon_days: int
    target_date: str
    pred_median_pct: float
    pred_low_pct: float
    pred_high_pct: float
    change_pct: float
    status: str = "PREDICTED"


class ForecastsResponse(BaseModel):
    reservoir: ReservoirInfo
    current_storage_pct: float
    as_of_date: str
    horizon_cards: list[ForecastHorizonCard]
    trajectory_chart: dict[str, Any]
    demand_stress_summary: list[dict[str, Any]]
    threshold_risk: dict[str, Any]
    storage_composition: dict[str, Any]
    forecast_reliability: dict[str, Any]
    provenance: dict[str, Any]


# -------------------------------------------------------------
# 04 Demand Stress Test Screen
# -------------------------------------------------------------
class StressTestRequest(BaseModel):
    water_demand: Literal["baseline", "low", "high", "contingency"] = "baseline"
    inflow_conditions: Literal["normal", "deficient_30", "severe_50", "surplus_30"] = "normal"
    monsoon_timing: Literal["on_schedule", "delayed_14d", "delayed_30d", "early_7d"] = "on_schedule"
    horizon_days: int = Field(default=44, ge=7, le=120)


class StressTestResponse(BaseModel):
    water_demand: str
    inflow_conditions: str
    monsoon_timing: str
    horizon_days: int
    estimated_water_cover_days: int
    monsoon_gap_days: int
    scenario_comparison: list[dict[str, Any]]
    scenario_risk: dict[str, Any]
    sensitivity_analysis: list[dict[str, Any]]
    assumptions_and_limitations: list[str]


# -------------------------------------------------------------
# 05 Evidence & Verification Screen
# -------------------------------------------------------------
class EvidenceItem(BaseModel):
    id: str
    title: str
    source_url: str
    organization: str
    publication_date: str
    observation_period: str
    query_type: str
    extracted_claim: str
    verification_status: Literal["verified", "pending", "needs_review", "stale", "context_only"]
    stance: Literal["supports_risk", "mitigates_risk", "neutral"]
    is_official_domain: bool
    freshness_days: int
    notes: str = ""


class EvidenceVerificationAction(BaseModel):
    source_id: str
    new_status: Literal["verified", "pending", "needs_review", "stale", "context_only"]
    new_stance: Literal["supports_risk", "mitigates_risk", "neutral"] | None = None
    notes: str = ""


class EvidenceDashboardResponse(BaseModel):
    reservoir: str
    last_sync: str
    workflow_state: dict[str, str]
    summary_counts: dict[str, int]
    sources_queue: list[EvidenceItem]
    quality_stats: dict[str, Any]
    conflicts: list[dict[str, Any]]
    official_comparison_table: list[dict[str, Any]]
    audit_trail: list[dict[str, Any]]


# -------------------------------------------------------------
# 06 Model Health Screen
# -------------------------------------------------------------
class ModelHealthResponse(BaseModel):
    active_model: dict[str, Any]
    kpi_cards: dict[str, Any]
    horizon_comparison: list[dict[str, Any]]
    prediction_accuracy_timeline: list[dict[str, Any]]
    residual_analysis: dict[str, Any]
    error_by_horizon_and_season: list[dict[str, Any]]
    historical_backtest_splits: dict[str, Any]
    input_data_health: dict[str, Any]
    uncertainty_calibration: dict[str, Any]
    early_warning_performance: dict[str, Any]
    health_assessment: dict[str, Any]
    model_version_history: list[dict[str, Any]]


# -------------------------------------------------------------
# 07 Reports Screen
# -------------------------------------------------------------
class ReportSectionFlags(BaseModel):
    forecast_charts: bool = True
    evidence_citations: bool = True
    mitigation_recommendations: bool = True
    scenario_comparisons: bool = True
    model_health_and_uncertainty: bool = True


class ReportGenerateRequest(BaseModel):
    reservoir: str = "Hirakud"
    state: str = "Odisha"
    district: str = "Sambalpur"
    river_basin: str = "Mahanadi Basin"
    report_type: str = "Reservoir Risk Assessment"
    forecast_horizon_days: int = 14
    include_sections: ReportSectionFlags = Field(default_factory=ReportSectionFlags)
    output_format: Literal["pdf", "json", "markdown"] = "pdf"


class ReportRecord(BaseModel):
    id: int
    title: str
    reservoir: str
    state: str
    basin: str
    report_type: str
    created_at: str
    updated_at: str
    status: Literal["draft", "in_review", "approved"]
    forecast_horizon_days: int
    executive_summary: str
    content_json: dict[str, Any]


class ReportStatusUpdate(BaseModel):
    status: Literal["draft", "in_review", "approved"]
    reviewed_by: str = "Chief Hydrologist"
    comments: str = ""


class ReportsDashboardResponse(BaseModel):
    overview: dict[str, Any]
    featured_template: dict[str, Any]
    previous_reports: list[ReportRecord]


# -------------------------------------------------------------
# 08 Methodology & Team
# -------------------------------------------------------------
class MethodologyResponse(BaseModel):
    framework_title: str
    tagline: str
    connected_stages: list[dict[str, Any]]
    water_balance_equation: str
    core_pillars: list[dict[str, Any]]
    decision_principles: list[dict[str, Any]]


class TeamMember(BaseModel):
    name: str
    role: str
    badge: str
    bio: str
    image_url: str


class TeamResponse(BaseModel):
    team_name: str
    project: str
    members: list[TeamMember]
