(function () {
  "use strict";
  const { R, T, topNav } = window.WZ;

  const P = {
    bg: "#f6f3e7",
    lime: "#c2db52",
    nav: "#0e2e25",
    ink: "#0e2e25",
    muted: "#526657",
    cream: "#fcfbf2",
    line: "#d1d1b8",
    chip: "#e8edd1",
    panel: "#edf0db",
    accent: "#1a4d3b",
  };

  window.WZ_PAGES = window.WZ_PAGES || {};
  window.WZ_PAGES.methodology = {
    w: 1440,
    h: 1617,
    bg: P.bg,
    title: "WaterZero — Methodology",
    api: "/api/methodology",

    build(d) {
      const els = [];
      const pal = { stripe: P.lime, nav: P.nav, marker: P.lime, plain: true };
      els.push(...topNav("methodology", pal));

      // Header
      els.push(T(32, 116, 900, 11, 700, P.muted, d.breadcrumb));
      els.push(R(1128, 113, 280, 30, { bg: P.chip, rad: 15 }));
      els.push(T(1148, 122, 240, 10, 700, P.ink, d.status));
      els.push(T(32, 157, 1000, 48, 700, P.ink, d.title));
      els.push(T(34, 236, 1020, 17, 400, P.muted, d.subtitle));
      els.push(R(32, 424, 1376, 1, { bg: P.line }));

      // Workflow stages
      els.push(T(32, 326, 800, 11, 700, P.muted, "THE WORKFLOW  /  5 CONNECTED STAGES"));
      els.push(T(780, 326, 628, 10, 700, P.muted, d.workflow_flow, { align: "right" }));
      [32, 310, 588, 866, 1144].forEach((x, i) => {
        const s = d.stages[i];
        if (!s) return;
        els.push(R(x, 365, 264, 325, { bg: P.cream, bd: P.line, rad: 10 }));
        els.push(R(x, 365, 264, 5, { bg: i === 2 ? P.lime : P.accent, rad: 3 }));
        els.push(T(x + 18, 388, 54, 26, 700, P.ink, s.num));
        els.push(T(x + 143, 396, 100, 9, 700, P.muted, s.tag, { align: "right" }));
        els.push(T(x + 18, 442, 228, 18, 700, P.ink, s.title));
        els.push(R(x + 18, 502, 228, 1, { bg: P.line }));
        els.push(T(x + 18, 520, 228, 13, 400, P.muted, s.desc));
        els.push(R(x + 14, 620, 236, 55, { bg: P.panel, rad: 6 }));
        els.push(T(x + 24, 630, 216, 10, 700, P.ink, s.footer_title));
        els.push(T(x + 24, 648, 216, 10, 400, P.muted, s.footer_sub));
        if (i < 4) els.push(R(x + 264, 410, 14, 2, { bg: P.lime }));
      });

      // Forecasting logic
      els.push(T(32, 746, 600, 11, 700, P.muted, "02  /  FORECASTING LOGIC"));
      els.push(T(32, 779, 900, 30, 700, P.ink, "The logic behind every forecast"));
      els.push(R(32, 842, 1376, 112, { bg: P.nav, rad: 10 }));
      els.push(T(58, 862, 500, 10, 700, P.lime, d.equation_label));
      els.push(T(58, 889, 1300, 23, 700, P.cream, d.equation));
      els.push(T(34, 967, 1340, 12, 400, P.muted, d.equation_caveat));

      [32, 496, 960].forEach((x, i) => {
        const c = d.logic[i];
        if (!c) return;
        els.push(R(x, 1017, 448, 156, { bg: P.cream, bd: P.line, rad: 9 }));
        els.push(T(x + 20, 1037, 50, 16, 700, P.ink, c.num));
        els.push(T(x + 82, 1038, 330, 17, 700, P.ink, c.title));
        els.push(T(x + 22, 1082, 400, 13, 400, P.muted, c.desc));
      });

      // Model reliability
      els.push(R(32, 1217, 1376, 1, { bg: P.line }));
      els.push(T(32, 1244, 600, 11, 700, P.muted, "03  /  MODEL RELIABILITY"));
      els.push(T(32, 1276, 900, 30, 700, P.ink, "Built for transparent decisions"));
      [32, 496, 960].forEach((x, i) => {
        const c = d.reliability[i];
        if (!c) return;
        els.push(R(x, 1342, 448, 124, { bg: P.cream, bd: P.line, rad: 9 }));
        els.push(R(x + 20, 1362, 8, 8, { bg: P.lime, rad: 4 }));
        els.push(T(x + 40, 1358, 380, 16, 700, P.ink, c.title));
        els.push(T(x + 22, 1393, 400, 12, 700, P.ink, c.status));
        els.push(T(x + 22, 1420, 400, 11, 400, P.muted, c.desc));
      });

      // Decision note
      els.push(R(32, 1490, 1376, 64, { bg: P.chip, rad: 8 }));
      els.push(T(54, 1511, 1330, 13, 700, P.ink, d.decision_note));

      return els;
    },
  };
})();
