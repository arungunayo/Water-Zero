from typing import Literal

from pydantic import BaseModel, Field


class Meta(BaseModel):
    breadcrumb: str
    live_label: str
    as_of: str
    source: str = Field(description="'demo' or 'live'")


class Storage(BaseModel):
    current_pct: float
    tmc_live: float
    tmc_gross_capacity: float
    forecast_7d_pct: float
    outlook_14d_pct: float
    change_14d_pts: float
    range_14d: tuple[float, float]
    trend: list[float] = Field(description="Recent storage levels for the mini trend chart")
    forecast_trend: list[float] = Field(description="Forecast levels for the mini forecast chart")


class ForecastPoint(BaseModel):
    pct: float
    low: float | None = None
    high: float | None = None


class Trajectory(BaseModel):
    observed: list[float] = Field(description="Observed storage %, evenly spaced in time")
    forecast: list[ForecastPoint]
    threshold_pct: float
    y_min: float = 10
    y_max: float = 50
    axis_labels: tuple[str, str, str]


class Risk(BaseModel):
    threshold_pct: float
    days_min: int
    days_max: int
    explanation: str
    daily_depletion_pct: float


class Decision(BaseModel):
    demand_label: str
    rainfall_value: str
    cover_days: int
    cover_vs_monsoon: str
    runway_ratio: float = Field(ge=0, le=1)


class StressBar(BaseModel):
    label: str
    ratio: float = Field(ge=0, le=1, description="Bar height as a fraction of the tallest bar")


class EvidenceSummary(BaseModel):
    verified: int
    stale: int


class EvidenceItem(BaseModel):
    date: str
    title: str
    source: str
    status_label: str
    tone: Literal["risk", "validate", "stale"]


class Evidence(BaseModel):
    summary: EvidenceSummary
    items: list[EvidenceItem]


class Reliability(BaseModel):
    mae: float
    rmse: float
    note: str
    bars: list[float] = Field(description="Four bar heights as fractions of the tallest")


class DashboardResponse(BaseModel):
    meta: Meta
    storage: Storage
    trajectory: Trajectory
    risk: Risk
    decision: Decision
    stress_bars: list[StressBar]
    evidence: Evidence
    reliability: Reliability
