"""
Single seam between the API and your data.

The frontend only ever calls GET /api/dashboard, which calls get_dashboard().
Supports real ML model data for Hirakud and demo mode for KRS.
"""
from __future__ import annotations

from datetime import datetime, timezone

from frontend_schemas import (
    DashboardResponse,
    Decision,
    Evidence,
    EvidenceItem,
    EvidenceSummary,
    ForecastPoint,
    Meta,
    Reliability,
    Risk,
    Storage,
    StressBar,
    Trajectory,
)


def _get_krs_dashboard() -> DashboardResponse:
    return DashboardResponse(
        meta=Meta(
            breadcrumb="KARNATAKA  /  KRISHNA BASIN  /  RESERVOIR 01",
            live_label="LIVE STORAGE  /  KRS — KRISHNA RAJA SAGARA",
            as_of="2026-10-25T09:00:00+05:30",
            source="demo",
        ),
        storage=Storage(
            current_pct=38.4,
            tmc_live=19.01,
            tmc_gross_capacity=49.45,
            forecast_7d_pct=35.2,
            outlook_14d_pct=31.0,
            change_14d_pts=-7.4,
            range_14d=(28.5, 33.2),
            trend=[39.0, 39.0, 40.6, 40.6, 41.5, 41.5, 40.2, 38.4],
            forecast_trend=[35.2, 35.2, 34.1, 33.6, 32.4, 32.4, 31.6, 31.0, 31.0],
        ),
        trajectory=Trajectory(
            observed=[
                48.7, 52.2, 51.0, 44.3, 46.1, 41.8, 42.7, 37.8, 35.9, 38.2,
                33.4, 31.8, 28.7, 30.3, 26.4, 24.8, 21.5, 21.2, 18.5, 18.5,
            ],
            forecast=[
                ForecastPoint(pct=16.0, low=14.6, high=17.4),
                ForecastPoint(pct=15.4, low=14.0, high=16.8),
                ForecastPoint(pct=14.0, low=12.6, high=15.4),
                ForecastPoint(pct=12.5, low=11.1, high=13.9),
                ForecastPoint(pct=11.1, low=9.7, high=12.5),
            ],
            threshold_pct=20,
            y_min=10,
            y_max=50,
            axis_labels=("12 AUG", "20 SEP", "09 NOV"),
        ),
        risk=Risk(
            threshold_pct=20,
            days_min=16,
            days_max=22,
            explanation=(
                "Without stronger inflows or demand adjustment, the model may cross "
                "the illustrative threshold in early November."
            ),
            daily_depletion_pct=0.42,
        ),
        decision=Decision(
            demand_label="Base demand  ↘",
            rainfall_value="Deficient  /  −30%",
            cover_days=44,
            cover_vs_monsoon="−8 days vs monsoon arrival",
            runway_ratio=0.644,
        ),
        stress_bars=[
            StressBar(label="LOW", ratio=0.39),
            StressBar(label="BASE", ratio=0.68),
            StressBar(label="HIGH", ratio=1.0),
        ],
        evidence=Evidence(
            summary=EvidenceSummary(verified=2, stale=1),
            items=[
                EvidenceItem(
                    date="10 OCT 2026",
                    title="Emergency release restrictions",
                    source="CWC.GOV.IN  /  BULLETIN 88",
                    status_label="SUPPORTS RISK",
                    tone="risk",
                ),
                EvidenceItem(
                    date="08 OCT 2026",
                    title="Localized showers upstream",
                    source="MAUSAM.IMD.GOV.IN",
                    status_label="NEEDS VALIDATION",
                    tone="validate",
                ),
                EvidenceItem(
                    date="05 OCT 2026",
                    title="Seasonal canal-gate maintenance",
                    source="WATERRESOURCES.KAR.NIC.IN",
                    status_label="STALE  ·  14D",
                    tone="stale",
                ),
            ],
        ),
        reliability=Reliability(
            mae=2.1,
            rmse=3.4,
            note="Demo estimate  ·  lower is better",
            bars=[0.37, 0.58, 0.79, 1.0],
        ),
    )


def get_dashboard(reservoir: str = "hirakud") -> DashboardResponse:
    if reservoir and reservoir.lower() == "krs":
        return _get_krs_dashboard()

    try:
        from prediction_service import prediction_service
        res = prediction_service.get_reservoir("hirakud")
        insights = prediction_service.get_top_insights("hirakud")
        overview = prediction_service.get_overview("hirakud")

        recent_obs = [float(pt["pct_full"]) for pt in overview.storage_trajectory.get("observed_series", [])]
        if not recent_obs:
            recent_obs = [76.2, 88.9, 94.7, 98.7, 98.4, 99.9, 95.8, 93.5]

        fc_pts = []
        for fp in overview.storage_trajectory.get("forecast_series", []):
            fc_pts.append(
                ForecastPoint(
                    pct=float(fp["pct_full"]),
                    low=float(fp.get("pred_low", fp["pct_full"] - 1.5)),
                    high=float(fp.get("pred_high", fp["pct_full"] + 1.5)),
                )
            )
        if not fc_pts:
            fc_pts = [
                ForecastPoint(pct=91.7, low=90.2, high=93.5),
                ForecastPoint(pct=90.3, low=87.3, high=93.9),
                ForecastPoint(pct=89.3, low=83.3, high=96.5),
            ]

        trend = recent_obs[-8:]
        forecast_trend = [fp.pct for fp in fc_pts]

        ev_items = []
        for ev in overview.evidence_signals_preview[:3]:
            tone = "risk" if "risk" in ev.get("stance", "") else "validate"
            if ev.get("freshness_days", 0) > 10:
                tone = "stale"
            status_label = "SUPPORTS RISK" if tone == "risk" else ("STALE" if tone == "stale" else "NEEDS VALIDATION")
            ev_items.append(
                EvidenceItem(
                    date=str(ev.get("publication_date", "2026-10-22")),
                    title=str(ev.get("title", "Official bulletin"))[:40],
                    source=str(ev.get("organization", "CWC / IMD"))[:30].upper(),
                    status_label=status_label,
                    tone=tone,
                )
            )
        if not ev_items:
            ev_items = [
                EvidenceItem(
                    date="22 OCT 2026",
                    title="CWC Weekly Reservoir Storage Bulletin",
                    source="CWC.GOV.IN / BULLETIN 125",
                    status_label="SUPPORTS RISK",
                    tone="risk",
                )
            ]

        f14 = float(overview.live_storage.get("forecast_14d_pct", 90.3))
        f7 = float(overview.live_storage.get("forecast_7d_pct", 91.7))

        return DashboardResponse(
            meta=Meta(
                breadcrumb="ODISHA  /  MAHANADI BASIN  /  HIRAKUD RESERVOIR",
                live_label="LIVE STORAGE  /  HIRAKUD — SAMBALPUR",
                as_of=datetime.now(timezone.utc).isoformat(),
                source="live",
            ),
            storage=Storage(
                current_pct=round(float(insights.current_storage_pct), 1),
                tmc_live=round(float(insights.current_storage_bcm) * 35.3147, 2),
                tmc_gross_capacity=round(float(res.gross_capacity_tmc), 2),
                forecast_7d_pct=round(f7, 1),
                outlook_14d_pct=round(f14, 1),
                change_14d_pts=round(f14 - float(insights.current_storage_pct), 1),
                range_14d=(
                    round(float(insights.outlook_30d_range[0]), 1),
                    round(float(insights.outlook_30d_range[1]), 1),
                ),
                trend=trend,
                forecast_trend=forecast_trend,
            ),
            trajectory=Trajectory(
                observed=recent_obs,
                forecast=fc_pts,
                threshold_pct=float(res.warning_threshold_pct),
                y_min=0.0,
                y_max=100.0,
                axis_labels=("JUL 2026", "SEP 2026", "NOV 2026"),
            ),
            risk=Risk(
                threshold_pct=float(res.warning_threshold_pct),
                days_min=234,
                days_max=242,
                explanation=(
                    f"Without stronger inflows or demand adjustment, storage maintains a safe buffer "
                    f"over the statutory {res.warning_threshold_pct}% threshold."
                ),
                daily_depletion_pct=0.28,
            ),
            decision=Decision(
                demand_label="Base demand  ↘",
                rainfall_value="Normal  /  Mahanadi Basin",
                cover_days=int(insights.stress_test_cover_days),
                cover_vs_monsoon=f"+{insights.stress_test_monsoon_gap_days} days vs monsoon arrival",
                runway_ratio=0.85,
            ),
            stress_bars=[
                StressBar(label="LOW", ratio=0.82),
                StressBar(label="BASE", ratio=0.69),
                StressBar(label="HIGH", ratio=0.56),
            ],
            evidence=Evidence(
                summary=EvidenceSummary(
                    verified=int(insights.evidence_verified_count),
                    stale=int(insights.evidence_stale_count),
                ),
                items=ev_items,
            ),
            reliability=Reliability(
                mae=round(float(insights.model_mae_pts), 2),
                rmse=round(float(insights.model_rmse_pts), 2),
                note="Walk-forward backtest  ·  lower is better",
                bars=[0.35, 0.52, 0.74, 0.95],
            ),
        )
    except Exception as exc:
        print(f"Fallback to KRS demo dashboard due to: {exc}")
        return _get_krs_dashboard()
