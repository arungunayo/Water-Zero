(function () {
  "use strict";
  const { R, T, C, topNav } = window.WZ;

  const TONE = {
    ink: "#0e2924",
    green: "#598733",
    blue: "#3885ad",
    alert: "#ed4529",
    amber: "#c79133",
    muted: "#596b5e",
    light: "#ccd6c7",
    cream: "#fcfbf2",
    sand: "#f5f2e5",
    track: "#e5ebdb",
    line: "#d1d4c2",
    dark: "#09211d",
    lime: "#def0d1",
    base: "#adb5a8",
  };

  const pick = (tone) => TONE[tone] || TONE.muted;

  window.WZ_PAGES = window.WZ_PAGES || {};
  window.WZ_PAGES["model-health"] = {
    w: 1440,
    h: 2540,
    bg: "#f5f2e5",
    title: "WaterZero — Model Health",
    api: "/api/model-health",

    build(d) {
      const els = [];
      els.push(...topNav("dashboard"));

      // Header
      els.push(T(32, 108, 650, 10, 700, TONE.green, d.breadcrumb));
      els.push(T(32, 139, 600, 32, 700, TONE.ink, "Model Health"));
      els.push(T(32, 183, 900, 13, 400, TONE.muted, d.subtitle));

      // Section pill nav
      els.push(R(453, 296, 600, 42, { bg: TONE.cream, bd: "#ccd4c4", rad: 24 }));
      els.push(R(781, 304, 100, 26, { bg: TONE.lime, rad: 16 }));
      els.push(T(481, 312, 50, 9, 500, TONE.muted, "Overview", { href: "/" }));
      els.push(T(549, 312, 62, 9, 500, TONE.muted, "Forecasts", { href: "/forecasts" }));
      els.push(T(629, 312, 70, 9, 500, TONE.muted, "Stress Test", { href: "/stress-test" }));
      els.push(T(717, 312, 58, 9, 500, TONE.muted, "Evidence", { href: "/evidence" }));
      els.push(T(793, 312, 76, 9, 600, TONE.ink, "Model health", { href: "/model-health" }));
      els.push(T(887, 312, 52, 9, 500, TONE.muted, "Reports", { href: "/reports" }));

      // Model summary strip
      els.push(R(32, 474, 290, 25, { bg: TONE.track, rad: 13 }));
      els.push(T(42, 481, 270, 8, 600, TONE.green, d.reservoir));
      els.push(T(350, 477, 130, 8, 700, TONE.muted, "ACTIVE MODEL"));
      els.push(T(350, 491, 370, 10, 500, TONE.ink, d.active_model));
      els.push(T(740, 477, 130, 8, 700, TONE.muted, "LAST TRAINING"));
      els.push(T(740, 491, 180, 10, 500, TONE.ink, d.last_training));
      els.push(T(930, 477, 140, 8, 700, TONE.muted, "LAST EVALUATION"));
      els.push(T(930, 491, 170, 10, 500, TONE.ink, d.last_evaluation));
      els.push(R(1110, 474, 170, 25, { bg: TONE.cream, bd: TONE.line, rad: 13 }));
      els.push(T(1120, 481, 150, 8, 600, TONE.muted, d.evaluation_period));
      els.push(R(1290, 474, 118, 42, { bg: TONE.track, bd: TONE.line, rad: 5 }));
      els.push(T(1300, 481, 100, 8, 700, TONE.muted, "MODEL STATUS"));
      els.push(T(1300, 497, 105, 8, 700, pick(d.status.tone), d.status.label));
      els.push(T(32, 526, 1100, 9, 500, TONE.muted, d.note));

      // KPI cards
      [32, 382, 732, 1082].forEach((x, i) => {
        const k = d.kpis[i];
        if (!k) return;
        els.push(R(x, 550, 326, 102, { bg: TONE.cream, bd: TONE.line, rad: 6 }));
        els.push(T(x + 15, 566, 295, 9, 700, TONE.muted, k.label));
        els.push(T(x + 15, 588, 260, 22, 700, pick(k.tone), k.value));
        els.push(T(x + 15, 618, 300, 9, 500, TONE.ink, k.desc));
        els.push(T(x + 15, 635, 300, 8, 400, TONE.muted, k.note));
      });

      // 01 Horizon comparison
      els.push(R(32, 674, 1376, 330, { bg: TONE.cream, bd: TONE.line, rad: 6 }));
      els.push(T(56, 694, 400, 10, 700, TONE.green, "01  /  HORIZON COMPARISON"));
      els.push(T(56, 716, 500, 20, 700, TONE.ink, d.horizon.title));
      els.push(T(56, 744, 700, 10, 400, TONE.muted, d.horizon.subtitle));
      els.push(R(1140, 704, 92, 25, { bg: TONE.track, rad: 13 }));
      els.push(T(1150, 711, 72, 8, 600, TONE.green, d.horizon.metric));
      els.push(R(1244, 704, 130, 25, { bg: TONE.cream, bd: TONE.line, rad: 13 }));
      els.push(T(1254, 711, 110, 8, 600, TONE.muted, d.horizon.evaluation));
      els.push(T(56, 780, 780, 9, 500, TONE.muted, d.horizon.legend));
      [812, 849, 886, 923, 960].forEach((y) => els.push(R(90, y, 870, 1, { bg: TONE.line })));
      d.horizon.horizons.slice(0, 3).forEach((label, i) => {
        const x = [220, 490, 760][i];
        els.push(T(x, 968, 100, 9, 700, TONE.ink, label));
        els.push(R(x, 954, 42, 6, { bg: TONE.green, rad: 2 }));
        els.push(R(x + 48, 954, 42, 6, { bg: TONE.base, rad: 2 }));
      });
      els.push(T(1000, 824, 350, 11, 500, TONE.muted, d.horizon.chart_note));
      els.push(R(990, 864, 380, 95, { bg: TONE.sand, rad: 4 }));
      els.push(T(1006, 878, 140, 8, 700, TONE.green, "READOUT"));
      els.push(T(1006, 898, 345, 10, 400, TONE.ink, d.horizon.readout));

      // 02 Time-series evaluation
      els.push(R(32, 1024, 1376, 350, { bg: TONE.cream, bd: TONE.line, rad: 6 }));
      els.push(T(56, 1044, 450, 10, 700, TONE.green, "02  /  TIME-SERIES EVALUATION"));
      els.push(T(56, 1066, 580, 20, 700, TONE.ink, d.timeseries.title));
      els.push(T(56, 1094, 780, 10, 400, TONE.muted, d.timeseries.subtitle));
      els.push(R(1120, 1052, 170, 25, { bg: TONE.cream, bd: TONE.line, rad: 13 }));
      els.push(T(1130, 1059, 150, 8, 600, TONE.muted, d.timeseries.range));
      els.push(T(56, 1126, 800, 9, 500, TONE.muted, d.timeseries.legend));
      [1160, 1198.75, 1237.5, 1276.25, 1315].forEach((y) => els.push(R(90, y, 970, 1, { bg: TONE.line })));
      ["50%", "40%", "30%"].forEach((label, i) => els.push(T(56, [1155, 1193, 1232][i], 30, 8, 400, TONE.muted, label)));
      els.push(T(90, 1324, 130, 8, 400, TONE.muted, d.timeseries.eval_start));
      els.push(T(900, 1324, 130, 8, 400, TONE.muted, d.timeseries.eval_end));
      els.push(R(1090, 1160, 280, 155, { bg: TONE.sand, rad: 4 }));
      els.push(T(1106, 1190, 240, 11, 600, TONE.ink, d.timeseries.empty_title));
      els.push(T(1106, 1214, 240, 9, 400, TONE.muted, d.timeseries.empty_body));
      els.push(T(56, 1343, 1250, 9, 400, TONE.muted, d.timeseries.interpretation));

      // 03 Residual analysis
      els.push(R(32, 1394, 670, 270, { bg: TONE.cream, bd: TONE.line, rad: 6 }));
      els.push(T(52, 1413, 400, 10, 700, TONE.green, "03  /  RESIDUAL ANALYSIS"));
      els.push(T(52, 1434, 520, 18, 700, TONE.ink, d.residuals.title));
      els.push(T(52, 1460, 560, 9, 400, TONE.muted, d.residuals.subtitle));
      [1494, 1522, 1550, 1578, 1606].forEach((y) => els.push(R(72, y, 510, 1, { bg: TONE.line })));
      els.push(R(327, 1494, 2, 112, { bg: TONE.ink }));
      els.push(T(72, 1612, 170, 8, 700, TONE.blue, "UNDERPREDICTION"));
      els.push(T(427, 1612, 150, 8, 700, TONE.alert, "OVERPREDICTION"));
      els.push(T(52, 1637, 560, 10, 500, TONE.ink, d.residuals.metrics));

      // 04 Error breakdown by horizon
      els.push(R(722, 1394, 686, 270, { bg: TONE.cream, bd: TONE.line, rad: 6 }));
      els.push(T(742, 1413, 400, 10, 700, TONE.green, "04  /  ERROR BREAKDOWN"));
      els.push(T(742, 1434, 480, 18, 700, TONE.ink, d.breakdown.title));
      els.push(T(742, 1460, 630, 9, 400, TONE.muted, d.breakdown.subtitle));
      [1500, 1533.33, 1566.67, 1600].forEach((y) => els.push(R(765, y, 590, 1, { bg: TONE.line })));
      ["7D", "14D", "30D"].forEach((label, i) => {
        const x = [825, 1005, 1185][i];
        els.push(R(x, 1594, 35, 6, { bg: TONE.green, rad: 2 }));
        els.push(R(x + 42, 1594, 35, 6, { bg: TONE.base, rad: 2 }));
        els.push(T(x + 7, 1610, 60, 8, 700, TONE.ink, label));
      });
      els.push(T(742, 1637, 620, 9, 500, TONE.amber, d.breakdown.caution));

      // 05 Backtesting
      els.push(R(32, 1684, 1376, 230, { bg: TONE.cream, bd: TONE.line, rad: 6 }));
      els.push(T(56, 1704, 460, 10, 700, TONE.green, "05  /  HISTORICAL BACKTESTING"));
      els.push(T(56, 1726, 500, 19, 700, TONE.ink, d.backtest.title));
      els.push(T(56, 1752, 950, 10, 400, TONE.muted, d.backtest.subtitle));
      [
        { x: 56, color: TONE.green },
        { x: 356, color: TONE.blue },
        { x: 656, color: TONE.alert },
      ].forEach((b, i) => {
        const s = d.backtest.stages[i];
        if (!s) return;
        els.push(R(b.x, 1790, 270, 42, { bg: b.color, rad: 4 }));
        els.push(T(b.x + 10, 1798, 250, 9, 700, TONE.cream, s.label));
        els.push(T(b.x + 10, 1814, 250, 8, 400, TONE.cream, s.status));
      });
      els.push(R(980, 1785, 390, 78, { bg: TONE.sand, rad: 4 }));
      els.push(T(996, 1798, 300, 8, 700, TONE.green, "EVALUATION SUMMARY"));
      els.push(T(996, 1815, 350, 9, 400, TONE.ink, d.backtest.summary[0] || ""));
      els.push(T(996, 1830, 350, 9, 400, TONE.ink, d.backtest.summary[1] || ""));

      // 06 Input data health
      els.push(R(32, 1934, 1376, 200, { bg: TONE.cream, bd: TONE.line, rad: 6 }));
      els.push(T(56, 1954, 420, 10, 700, TONE.green, "06  /  INPUT DATA HEALTH"));
      els.push(T(56, 1976, 580, 19, 700, TONE.ink, d.data_health.title));
      [56, 386, 716, 1046].forEach((x, i) => {
        const c = d.data_health.cards[i];
        if (!c) return;
        els.push(R(x, 2010, 310, 88, { bg: TONE.sand, bd: TONE.line, rad: 4 }));
        els.push(R(x + 12, 2022, 7, 7, { bg: pick(c.tone), rad: 4 }));
        els.push(T(x + 26, 2020, 270, 8, 700, TONE.ink, c.label));
        els.push(T(x + 12, 2040, 285, 10, 400, TONE.muted, c.value));
        els.push(T(x + 12, 2061, 285, 8, 400, TONE.muted, c.detail));
      });
      els.push(T(56, 2108, 1200, 9, 400, TONE.muted, d.data_health.note));

      // 07 Uncertainty calibration
      els.push(R(32, 2154, 670, 185, { bg: TONE.cream, bd: TONE.line, rad: 6 }));
      els.push(T(52, 2173, 430, 9, 700, TONE.green, "07  /  FORECAST UNCERTAINTY"));
      els.push(T(52, 2194, 470, 17, 700, TONE.ink, d.uncertainty.title));
      els.push(R(52, 2224, 230, 23, { bg: TONE.track, rad: 12 }));
      els.push(T(64, 2231, 210, 8, 700, pick(d.uncertainty.tone), d.uncertainty.status));
      els.push(T(52, 2257, 600, 9, 400, TONE.muted, d.uncertainty.explanation));
      els.push(T(52, 2295, 500, 9, 500, TONE.ink, d.uncertainty.coverage));

      // 08 Early-warning performance
      els.push(R(722, 2154, 686, 185, { bg: TONE.cream, bd: TONE.line, rad: 6 }));
      els.push(T(742, 2173, 520, 9, 700, TONE.alert, "08  /  LOW-STORAGE EVENT DETECTION"));
      els.push(T(742, 2194, 480, 17, 700, TONE.ink, d.early_warning.title));
      [742, 900, 1058, 1216].forEach((x, i) => {
        const c = d.early_warning.cells[i];
        if (!c) return;
        els.push(R(x, 2225, 145, 42, { bg: TONE.sand, bd: TONE.line, rad: 4 }));
        els.push(T(x + 8, 2232, 130, 7, 700, TONE.muted, c.label));
        els.push(T(x + 8, 2247, 100, 11, 700, pick(c.tone), c.value));
      });
      els.push(T(742, 2287, 640, 9, 400, TONE.muted, d.early_warning.metrics));

      // 09 Assessment
      els.push(R(32, 2358, 670, 142, { bg: TONE.cream, bd: TONE.line, rad: 6 }));
      els.push(T(52, 2376, 450, 9, 700, TONE.green, "09  /  MODEL HEALTH ASSESSMENT"));
      els.push(T(52, 2397, 340, 18, 700, pick(d.assessment.tone), d.assessment.status));
      els.push(T(52, 2423, 610, 10, 400, TONE.ink, d.assessment.body));
      els.push(T(52, 2468, 620, 8, 500, TONE.muted, d.assessment.next));

      // 10 Model history
      els.push(R(722, 2358, 686, 142, { bg: TONE.cream, bd: TONE.line, rad: 6 }));
      els.push(T(742, 2376, 520, 9, 700, TONE.green, "10  /  MODEL VERSION & AUDIT TRAIL"));
      els.push(T(742, 2397, 320, 18, 700, TONE.ink, "Model history"));
      [
        [742, "VERSION"],
        [850, "DATASET"],
        [960, "EVALUATION"],
        [1080, "MAE / RMSE"],
        [1220, "STATUS"],
      ].forEach(([x, label]) => els.push(T(x, 2430, 105, 7, 700, TONE.muted, label)));
      els.push(R(742, 2446, 630, 1, { bg: TONE.line }));
      els.push(T(742, 2460, 600, 9, 400, TONE.muted, d.history.empty));

      return els;
    },
  };
})();
