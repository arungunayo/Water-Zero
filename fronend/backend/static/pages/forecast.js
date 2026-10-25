(function () {
  "use strict";
  const { R, T, C, topNav } = window.WZ;

  const TONE = {
    ink: "#0e2924",
    green: "#598733",
    blue: "#3885ad",
    alert: "#ed4529",
    muted: "#596b5e",
  };

  // Chart geometry (stage coordinates, from the Figma frame)
  const GRID_X1 = 92;
  const GRID_X2 = 1347;
  const OBS_X0 = 97;
  const FC_X0 = 637;
  function chart(d) {
    const ch = d.chart;
    const allVals = [...ch.observed, ...ch.forecast.map((p) => p.pct), ch.threshold_pct];
    const maxVal = Math.max(...allVals, 50);
    const isHighScale = maxVal > 55;
    const yMin = isHighScale ? 0 : 10;
    const yMax = isHighScale ? 100 : 50;
    const ySpan = yMax - yMin;
    const y = (p) => {
      const clamped = Math.max(yMin, Math.min(yMax, p));
      return 669 + ((yMax - clamped) / ySpan) * 300;
    };

    const gridSteps = isHighScale ? [100, 80, 60, 40, 20, 0] : [50, 40, 30, 20, 10];

    // [x0, step] -> stepped run of horizontal segments with a vertical join
    const segments = (values, x0, step) =>
      values.flatMap((v, i) => [
        [x0 + i * step, y(v)],
        [x0 + (i + 1) * step, y(v)],
      ]);

    return C((stage, h) => {
      const svg = h.svgLayer(stage, 24, 640, 1376, 340);
      svg.style.overflow = "hidden";

      gridSteps.forEach((p) => {
        h.svgEl("line", { x1: GRID_X1, x2: GRID_X2, y1: y(p), y2: y(p), stroke: "#d1d4c2", "stroke-width": 1 }, svg);
        h.svgText(svg, `${p}%`, 49, y(p) + 3, 9, "#596b5e", 400);
      });

      // History / forecast boundary
      h.svgEl("rect", { x: 637, y: 649, width: 1, height: 320, fill: "#ed4529" }, svg);

      // Threshold
      h.svgEl("rect", { x: GRID_X1, y: y(ch.threshold_pct) - 1, width: GRID_X2 - GRID_X1, height: 2, fill: "#ed4529" }, svg);

      // Forecast uncertainty intervals
      ch.forecast.forEach((p, i) => {
        if (p.low == null || p.high == null) return;
        const x = 697 + SEG * i;
        h.svgEl("line", { x1: x, x2: x, y1: y(p.high), y2: y(p.low), stroke: "#7fa44c", "stroke-width": 1.5 }, svg);
        h.svgEl("line", { x1: x - 4, x2: x + 4, y1: y(p.high), y2: y(p.high), stroke: "#7fa44c", "stroke-width": 1.5 }, svg);
        h.svgEl("line", { x1: x - 4, x2: x + 4, y1: y(p.low), y2: y(p.low), stroke: "#7fa44c", "stroke-width": 1.5 }, svg);
      });

      // Observed (dark) and forecast (green) stepped series
      h.svgEl("path", { d: h.steppedPath(segments(ch.observed, OBS_X0, SEG)), fill: "none", stroke: "#0e2924", "stroke-width": 3 }, svg);
      h.svgEl("path", { d: h.steppedPath(segments(ch.forecast.map((p) => p.pct), FC_X0, SEG)), fill: "none", stroke: "#598733", "stroke-width": 5 }, svg);
    });
  }

  function kpiCards(d) {
    const xs = [24, 374, 724, 1074];
    const out = [];
    d.kpis.slice(0, 4).forEach((k, i) => {
      const x = xs[i];
      out.push(R(x, 401, 326, 104, { bg: "#fcfbf2", bd: "#d1d4c2", rad: 5 }));
      out.push(T(x + 16, 416, 260, 9, 700, TONE.muted, k.label));
      out.push(T(x + 16, 437, 230, 26, 700, TONE[k.tone] || TONE.ink, k.value));
      out.push(T(x + 16, 474, 290, 9, 400, TONE.muted, k.note));
      out.push(T(x + 230, 416, 80, 8, 700, TONE[k.tag_tone] || TONE.muted, k.tag));
    });
    return out;
  }

  function scenarioCards(d) {
    const xs = [48, 487, 926];
    const out = [];
    d.scenarios.slice(0, 3).forEach((s, i) => {
      const x = xs[i];
      out.push(R(x, 1209, 410, 104, { bg: "#f5f2e5", rad: 4 }));
      out.push(T(x + 14, 1222, 180, 9, 700, TONE.muted, s.label));
      out.push(T(x + 14, 1242, 160, 23, 700, TONE.ink, s.days));
      out.push(T(x + 14, 1274, 200, 10, 400, TONE.muted, s.gap));
      out.push(R(x + 270, 1221, 122, 21, { bg: "#e5ebdb", rad: 11 }));
      out.push(T(x + 279, 1227, 110, 8, 700, TONE[s.tone] || TONE.green, s.pill));
    });
    return out;
  }

  function reliabilityHorizons(d) {
    const xs = [167, 512, 857];
    const out = [];
    d.reliability.horizons.slice(0, 3).forEach((hz, i) => {
      const x = xs[i];
      out.push(T(x, 1749, 100, 10, 700, TONE.ink, hz.label));
      out.push(R(x, 1776, 80, 20, { bg: "#e5ebdb", rad: 2 }));
      out.push(R(x + 90, 1776, 80, 20, { bg: "#dbe3cf", rad: 2 }));
      out.push(T(x + 18, 1781, 70, 8, 500, TONE.muted, hz.model || "Pending"));
      out.push(T(x + 102, 1781, 70, 8, 500, TONE.muted, hz.baseline || "Pending"));
    });
    return out;
  }

  window.WZ_PAGES = window.WZ_PAGES || {};
  window.WZ_PAGES.forecast = {
    w: 1440,
    h: 2057,
    bg: "#f5f2e5",
    title: "WaterZero — Storage Forecast",
    api: "/api/forecast",

    build(d) {
      const els = [];

      // Top bar
      els.push(...topNav("dashboard"));

      // Page header
      els.push(T(32, 108, 650, 10, 700, TONE.green, d.breadcrumb));
      els.push(T(32, 139, 720, 34, 700, TONE.ink, "Storage Forecast"));
      els.push(T(32, 183, 850, 15, 400, TONE.muted, "Predicting reservoir storage, uncertainty, and water availability."));

      // Section pill nav
      els.push(R(465, 301, 558, 48, { bg: "#fcfbf2", bd: "#ccd4c4", rad: 24 }));
      els.push(R(549, 311, 76, 32, { bg: "#def0d1", rad: 12 }));
      els.push(T(495, 321, 54, 8.5, 500, TONE.muted, "Overview", { href: "/" }));
      els.push(T(555, 321, 64, 8.5, 600, TONE.ink, "Forecasts", { href: "/forecasts" }));
      els.push(T(633, 321, 72, 8.5, 500, TONE.muted, "Stress Test", { href: "/stress-test" }));
      els.push(T(719, 321, 60, 8.5, 500, TONE.muted, "Evidence", { href: "/evidence" }));
      els.push(T(793, 321, 82, 8.5, 500, TONE.muted, "Model health", { href: "/model-health" }));
      els.push(T(889, 321, 58, 8.5, 500, TONE.muted, "Reports", { href: "/reports" }));

      // Reservoir selector, update stamp, horizon toggles, status
      els.push(R(24, 349, 208, 27, { bg: "#def0d1", rad: 14 }));
      els.push(T(34, 356, 188, 9, 600, TONE.ink, d.reservoir));
      els.push(T(250, 357, 500, 10, 500, TONE.muted, d.updated));
      els.push(R(842, 349, 75, 27, { bg: "#def0d1", rad: 14 }));
      els.push(T(852, 356, 55, 9, 600, TONE.ink, "7 Days"));
      els.push(R(924, 349, 82, 27, { bg: "#fcfbf2", bd: "#d1d4c2", rad: 14 }));
      els.push(T(934, 356, 62, 9, 500, TONE.muted, "14 Days"));
      els.push(R(1011, 349, 82, 27, { bg: "#fcfbf2", bd: "#d1d4c2", rad: 14 }));
      els.push(T(1021, 356, 62, 9, 500, TONE.muted, "30 Days"));
      els.push(R(1112, 358, 7, 7, { bg: TONE.alert, rad: 4 }));
      els.push(T(1126, 355, 260, 10, 700, TONE[d.status.tone] || TONE.alert, d.status.label));

      // KPI cards
      els.push(...kpiCards(d));

      // Main trajectory panel
      els.push(R(24, 527, 1376, 550, { bg: "#fcfbf2", bd: "#d1d4c2", rad: 6 }));
      els.push(T(48, 549, 360, 10, 700, TONE.green, "01  /  STORAGE TRAJECTORY"));
      els.push(T(48, 572, 650, 24, 700, TONE.ink, "Reservoir Storage Prediction"));
      els.push(T(48, 604, 930, 12, 400, TONE.muted, "Historical observations and forecast interval · illustrative until model outputs are connected"));
      els.push(R(1152, 553, 48, 27, { bg: "#def0d1", rad: 14 }));
      els.push(T(1162, 560, 28, 9, 600, TONE.ink, "7D"));
      els.push(R(1205, 553, 55, 27, { bg: "#fcfbf2", bd: "#d1d4c2", rad: 14 }));
      els.push(T(1215, 560, 35, 9, 500, TONE.muted, "14D"));
      els.push(R(1265, 553, 55, 27, { bg: "#fcfbf2", bd: "#d1d4c2", rad: 14 }));
      els.push(T(1275, 560, 35, 9, 500, TONE.muted, "30D"));

      els.push(chart(d));

      els.push(T(537, 644, 80, 8, 700, TONE.muted, "HISTORY"));
      els.push(T(662, 644, 210, 8, 700, TONE.green, "FORECAST · ILLUSTRATIVE"));
      els.push(T(992, y(d.chart.threshold_pct) - 17, 320, 9, 700, TONE.alert, "SHORTAGE THRESHOLD · ILLUSTRATIVE"));
      d.chart.date_labels.forEach((label, i) => {
        const x = [92, 582, 1272][i];
        els.push(T(x, 987, 130, 9, 400, TONE.muted, label));
      });

      // Chart legend
      els.push(R(50, 1024, 22, 3, { bg: TONE.ink }));
      els.push(T(80, 1017, 150, 10, 400, TONE.muted, "Historical actual"));
      els.push(R(237, 1024, 22, 3, { bg: TONE.green }));
      els.push(T(267, 1017, 90, 10, 400, TONE.muted, "Forecast"));
      els.push(R(367, 1016, 18, 13, { bg: "#e0ebcc", rad: 2 }));
      els.push(T(393, 1017, 260, 10, 400, TONE.muted, "Prediction interval · pending calibration"));
      els.push(R(692, 1023, 24, 2, { bg: TONE.alert }));
      els.push(T(724, 1017, 140, 10, 400, TONE.muted, "Critical threshold"));

      els.push(T(48, 1045, 120, 8, 700, TONE.green, "INTERPRETATION"));
      els.push(T(167, 1042, 1180, 11, 500, TONE.ink, d.chart.interpretation));

      // Demand stress test panel
      els.push(R(24, 1101, 1376, 238, { bg: "#fcfbf2", bd: "#d1d4c2", rad: 6 }));
      els.push(T(48, 1121, 420, 10, 700, TONE.green, "02  /  DEMAND STRESS TEST"));
      els.push(T(48, 1143, 760, 22, 700, TONE.ink, "Will Water Last Until the Next Monsoon?"));
      els.push(T(48, 1174, 940, 11, 400, TONE.muted, d.scenario_note));
      els.push(...scenarioCards(d));
      els.push(T(48, 1319, 1000, 9, 400, TONE.muted, d.scenario_footer));

      // Threshold risk panel
      els.push(R(24, 1361, 665, 250, { bg: "#fcfbf2", bd: "#d1d4c2", rad: 6 }));
      els.push(T(48, 1381, 350, 10, 700, TONE.alert, "03A  /  THRESHOLD RISK"));
      els.push(T(48, 1404, 380, 22, 700, TONE.ink, d.risk.title));
      els.push(C((stage, h) => h.donut(stage, 70, 1452, 94, d.risk.ratio, TONE.alert, "#e5ebdb", 9)));
      els.push(T(70, 1491, 94, 16, 700, TONE.ink, d.risk.value, { align: "center" }));
      els.push(T(196, 1461, 360, 9, 700, TONE.muted, d.risk.horizon_label));
      els.push(T(196, 1484, 410, 14, 500, TONE.ink, d.risk.status));
      els.push(T(196, 1512, 420, 11, 400, TONE.muted, d.risk.explanation));
      els.push(T(48, 1576, 400, 9, 500, TONE.alert, d.risk.note));

      // Storage composition panel
      els.push(R(711, 1361, 689, 250, { bg: "#fcfbf2", bd: "#d1d4c2", rad: 6 }));
      els.push(T(735, 1381, 390, 10, 700, TONE.green, "03B  /  STORAGE COMPOSITION"));
      els.push(T(735, 1404, 450, 22, 700, TONE.ink, d.composition.title));
      els.push(C((stage, h) => h.donut(stage, 758, 1452, 94, null, TONE.green, "#e5ebdb", 9)));
      els.push(T(758, 1491, 94, 16, 700, TONE.ink, "—", { align: "center" }));
      els.push(T(882, 1453, 440, 11, 500, TONE.ink, d.composition.lines[0]));
      els.push(T(882, 1481, 440, 11, 500, TONE.muted, d.composition.lines[1]));
      els.push(T(882, 1509, 440, 11, 500, TONE.muted, d.composition.lines[2]));
      els.push(T(735, 1576, 610, 9, 400, TONE.muted, d.composition.note));

      // Model evaluation panel
      els.push(R(24, 1633, 1376, 245, { bg: "#fcfbf2", bd: "#d1d4c2", rad: 6 }));
      els.push(T(48, 1653, 400, 10, 700, TONE.blue, "04  /  MODEL EVALUATION"));
      els.push(T(48, 1676, 550, 22, 700, TONE.ink, "Forecast Reliability"));
      els.push(T(48, 1706, 850, 11, 400, TONE.muted, d.reliability.subtitle));
      els.push(...reliabilityHorizons(d));
      els.push(R(1042, 1756, 18, 3, { bg: TONE.green }));
      els.push(T(1067, 1749, 100, 9, 400, TONE.muted, "Model error"));
      els.push(R(1177, 1756, 18, 3, { bg: TONE.blue }));
      els.push(T(1202, 1749, 140, 9, 400, TONE.muted, "Baseline error"));
      els.push(R(1042, 1789, 150, 54, { bg: "#f5f2e5", rad: 4 }));
      els.push(T(1052, 1797, 130, 8, 700, TONE.muted, "EVENT RECALL"));
      els.push(T(1052, 1816, 120, 15, 700, TONE.ink, d.reliability.recall));
      els.push(R(1202, 1789, 160, 54, { bg: "#f5f2e5", rad: 4 }));
      els.push(T(1212, 1797, 145, 8, 700, TONE.muted, "FALSE ALARM RATE"));
      els.push(T(1212, 1816, 120, 15, 700, TONE.ink, d.reliability.false_alarm));
      els.push(T(48, 1839, 930, 10, 400, TONE.muted, d.reliability.note));

      // Provenance footer
      els.push(R(24, 1899, 1376, 102, { bg: "#09211d", rad: 6 }));
      els.push(T(48, 1915, 280, 9, 700, "#bff033", "DATA & PROVENANCE"));
      [48, 442, 712, 1052].forEach((x, i) => {
        els.push(T(x, 1937, 340, 10, 500, "#fcfbf2", d.provenance[i]));
      });
      els.push(R(48, 1964, 188, 25, { bg: "#def0d1", rad: 13 }));
      els.push(T(60, 1971, 170, 8, 700, TONE.ink, "VIEW OFFICIAL EVIDENCE ↗", { href: "/evidence" }));

      return els;
    },
  };
})();
