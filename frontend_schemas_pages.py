"""
API contracts for the secondary screens.

Each model is the response of one endpoint and maps directly to the fields
read by the matching layout in static/pages/<slug>.js.
"""

from pydantic import BaseModel, Field


# ---------- shared ----------

class Pill(BaseModel):
    """A label with a semantic tone. Tones: ink, green, lime, blue, alert, amber, muted, accent."""
    label: str
    tone: str = "muted"


# ---------- Forecast (/api/forecast) ----------

class ForecastKpi(BaseModel):
    label: str
    value: str
    tone: str = "ink"
    note: str
    tag: str
    tag_tone: str = "muted"


class ForecastPointModel(BaseModel):
    pct: float
    low: float | None = None
    high: float | None = None


class ForecastChart(BaseModel):
    observed: list[float] = Field(description="Observed storage %, 9 segments")
    forecast: list[ForecastPointModel] = Field(description="Forecast %, 11 segments, with interval")
    threshold_pct: float
    date_labels: tuple[str, str, str]
    interpretation: str


class Scenario(BaseModel):
    label: str
    days: str
    gap: str
    pill: str
    tone: str = "green"


class ForecastRisk(BaseModel):
    title: str
    ratio: float | None = Field(default=None, ge=0, le=1, description="Ring fill; null for empty")
    value: str
    horizon_label: str
    status: str
    explanation: str
    note: str


class ForecastComposition(BaseModel):
    title: str
    lines: tuple[str, str, str]
    note: str


class HorizonMetric(BaseModel):
    label: str
    model: str | None = None
    baseline: str | None = None


class ForecastReliability(BaseModel):
    subtitle: str
    horizons: list[HorizonMetric]
    recall: str
    false_alarm: str
    note: str


class ForecastResponse(BaseModel):
    breadcrumb: str
    reservoir: str
    updated: str
    status: Pill
    kpis: list[ForecastKpi]
    chart: ForecastChart
    scenario_note: str
    scenarios: list[Scenario]
    scenario_footer: str
    risk: ForecastRisk
    composition: ForecastComposition
    reliability: ForecastReliability
    provenance: list[str]


# ---------- Stress test (/api/stress-test) ----------

class Control(BaseModel):
    label: str
    value: str


class StressControls(BaseModel):
    title: str
    note: str
    items: list[Control]


class StressOutcome(BaseModel):
    title: str
    subtitle: str
    cover_label: str
    cover_value: str
    cover_note: str


class ComparisonBar(BaseModel):
    label: str
    days: int
    color: str = Field(description="green | lime | alert")
    note: str
    note_tone: str = "muted"


class StressComparison(BaseModel):
    title: str
    subtitle: str
    bars: list[ComparisonBar]


class RiskRow(BaseModel):
    label: str
    value: str
    tone: str = "muted"


class StressRisk(BaseModel):
    title: str
    ratio: float = Field(ge=0, le=1)
    center: str
    case_label: str
    case_title: str
    case_note: str
    rows: list[RiskRow]


class SensitivityBar(BaseModel):
    label: str
    ratio: float = Field(ge=0, le=1)
    color: str = "green"
    status: str


class StressSensitivity(BaseModel):
    title: str
    subtitle: str
    bars: list[SensitivityBar]


class Assumption(BaseModel):
    text: str
    tone: str = "green"


class StressAssumptions(BaseModel):
    title: str
    items: list[Assumption]


class StressFooter(BaseModel):
    title: str
    subtitle: str


class StressTestResponse(BaseModel):
    breadcrumb: str
    subtitle: str
    reservoir: str
    scenario_note: str
    status: Pill
    controls: StressControls
    outcome: StressOutcome
    comparison: StressComparison
    risk: StressRisk
    sensitivity: StressSensitivity
    assumptions: StressAssumptions
    footer: StressFooter


# ---------- Evidence (/api/evidence) ----------

class EvidenceKpi(BaseModel):
    label: str
    value: str
    tone: str = "ink"
    note: str


class WorkflowStage(BaseModel):
    title: str
    status: str
    detail: str
    tone: str = "muted"


class Workflow(BaseModel):
    title: str
    stages: list[WorkflowStage]
    activity_label: str
    activity: str


class FilterItem(BaseModel):
    label: str
    value: str


class Filters(BaseModel):
    search: str
    items: list[FilterItem]


class SourceItem(BaseModel):
    title: str
    tag: str
    publication: str
    stance: str
    pill: str
    tone: str = "muted"
    actions: str


class Sources(BaseModel):
    title: str
    status_line: str
    footer: str
    items: list[SourceItem]


class DetailRow(BaseModel):
    label: str
    value: str


class SelectedSource(BaseModel):
    title: str
    banner_title: str
    banner_body: str
    rows: list[DetailRow]


class CountRow(BaseModel):
    label: str
    count: str


class Verification(BaseModel):
    title: str
    legend: str
    note: str
    freshness: list[CountRow]
    types: list[CountRow]
    caveat: str


class Conflicts(BaseModel):
    title: str
    body: str
    pill: str


class EvidenceResponse(BaseModel):
    breadcrumb: str
    subtitle: str
    reservoir: str
    sync: str
    status: Pill
    note: str
    kpis: list[EvidenceKpi]
    workflow: Workflow
    filters: Filters
    sources: Sources
    detail: SelectedSource
    verification: Verification
    conflicts: Conflicts
    comparison: dict[str, str]
    audit: dict[str, str]
    traceability: dict[str, str]


# ---------- Model health (/api/model-health) ----------

class ModelKpi(BaseModel):
    label: str
    value: str
    tone: str = "ink"
    desc: str
    note: str


class HorizonBlock(BaseModel):
    title: str
    subtitle: str
    metric: str
    evaluation: str
    legend: str
    horizons: tuple[str, str, str]
    chart_note: str
    readout: str


class TimeseriesBlock(BaseModel):
    title: str
    subtitle: str
    range: str
    legend: str
    eval_start: str
    eval_end: str
    empty_title: str
    empty_body: str
    interpretation: str


class ResidualBlock(BaseModel):
    title: str
    subtitle: str
    metrics: str


class BreakdownBlock(BaseModel):
    title: str
    subtitle: str
    caution: str


class BacktestStage(BaseModel):
    label: str
    status: str


class BacktestBlock(BaseModel):
    title: str
    subtitle: str
    stages: tuple[BacktestStage, BacktestStage, BacktestStage]
    summary: tuple[str, str]


class HealthCard(BaseModel):
    label: str
    value: str
    detail: str
    tone: str = "amber"


class DataHealthBlock(BaseModel):
    title: str
    cards: list[HealthCard]
    note: str


class UncertaintyBlock(BaseModel):
    title: str
    status: str
    tone: str = "amber"
    explanation: str
    coverage: str


class ConfusionCell(BaseModel):
    label: str
    value: str
    tone: str = "ink"


class EarlyWarningBlock(BaseModel):
    title: str
    cells: list[ConfusionCell]
    metrics: str


class AssessmentBlock(BaseModel):
    status: str
    tone: str = "amber"
    # Named 'body' rather than 'copy' because BaseModel already has a .copy() method.
    body: str
    next: str


class HistoryBlock(BaseModel):
    empty: str


class ModelHealthResponse(BaseModel):
    breadcrumb: str
    subtitle: str
    reservoir: str
    active_model: str
    last_training: str
    last_evaluation: str
    evaluation_period: str
    status: Pill
    note: str
    kpis: list[ModelKpi]
    horizon: HorizonBlock
    timeseries: TimeseriesBlock
    residuals: ResidualBlock
    breakdown: BreakdownBlock
    backtest: BacktestBlock
    data_health: DataHealthBlock
    uncertainty: UncertaintyBlock
    early_warning: EarlyWarningBlock
    assessment: AssessmentBlock
    history: HistoryBlock


# ---------- Methodology (/api/methodology) ----------

class MethodStage(BaseModel):
    num: str
    tag: str
    title: str
    desc: str
    footer_title: str
    footer_sub: str


class LogicCard(BaseModel):
    num: str
    title: str
    desc: str


class ReliabilityCard(BaseModel):
    title: str
    status: str
    desc: str


class MethodologyResponse(BaseModel):
    breadcrumb: str
    status: str
    title: str
    subtitle: str
    workflow_flow: str
    stages: list[MethodStage]
    equation_label: str
    equation: str
    equation_caveat: str
    logic: list[LogicCard]
    reliability: list[ReliabilityCard]
    decision_note: str


# ---------- About team (/api/about-team) ----------

class TeamMember(BaseModel):
    name: str
    role: str
    photo: str = Field(description="Path under /static, e.g. static/img/team-leader.jpg")


class AboutTeamResponse(BaseModel):
    breadcrumb: str
    leader: TeamMember
    member: TeamMember


# ---------- Reports (/api/reports) ----------

class SummaryCard(BaseModel):
    glyph: str
    number: str
    title: str
    value: str
    caption: str
    size: float | None = None


class FeaturedItem(BaseModel):
    glyph: str
    title: str
    desc: str


class FeaturedReport(BaseModel):
    title: str
    description: str
    status: str
    items: list[FeaturedItem]
    meta: str


class BuilderBlock(BaseModel):
    subtitle: str
    note: str


class PreviewBlock(BaseModel):
    summary: str
    bars: list[float] = Field(description="Eight bar heights as fractions of the tallest")
    scenarios: str
    status: str
    note: str


class ReportHistory(BaseModel):
    subtitle: str
    title: str
    body: str


class ReviewStep(BaseModel):
    title: str
    desc: str


class ReviewBlock(BaseModel):
    subtitle: str
    steps: list[ReviewStep]
    note: str


class ReportsResponse(BaseModel):
    breadcrumb: str
    subtitle: str
    status: str
    summary: list[SummaryCard]
    featured: FeaturedReport
    builder: BuilderBlock
    preview: PreviewBlock
    history: ReportHistory
    review: ReviewBlock
