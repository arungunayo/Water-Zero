(function () {
  "use strict";
  const { R, T, topNav } = window.WZ;

  const P = {
    bg: "#f6f3e7",
    stripe: "#c2db52",
    nav: "#0e2e25",
    ink: "#0e2e25",
    muted: "#526657",
    cream: "#fcfbf2",
    line: "#d1d1b8",
    lime: "#c2db52",
    chip: "#e8edd1",
    soft: "#f0f0de",
    page: "#fbfaf0",
    bar: "#6b916e",
  };

  // Top navigation (own palette) plus the Reports secondary nav.
  function secondaryNav(d) {
    const out = [];
    out.push(R(392, 265, 656, 48, { bg: P.cream, bd: P.line, rad: 24 }));
    out.push(R(878, 276, 66, 26, { bg: P.nav, rad: 14 }));
    const items = [
      { label: "Overview", cx: 448.5, w: 57, href: "/" },
      { label: "Forecasts", cx: 533, w: 62, href: "/forecasts" },
      { label: "Stress Test", cx: 635, w: 70, href: "/stress-test" },
      { label: "Evidence", cx: 731, w: 58, href: "/evidence" },
      { label: "Model Health", cx: 827, w: 78, href: "/model-health" },
      { label: "Reports", cx: 912, w: 52, href: "/reports", active: true },
    ];
    items.forEach((it) => {
      out.push(
        T(it.cx - it.w / 2, 282, it.w, 11, it.active ? 700 : 400, it.active ? P.cream : P.muted, it.label, {
          align: "center",
          href: it.href,
        })
      );
    });
    return out;
  }

  window.WZ_PAGES = window.WZ_PAGES || {};
  window.WZ_PAGES.reports = {
    w: 1440,
    h: 2216,
    bg: P.bg,
    title: "WaterZero — Reports",
    api: "/api/reports",

    build(d) {
      const els = [];
      els.push(...topNav("dashboard", { stripe: P.stripe, nav: P.nav, marker: P.lime || P.stripe }));

      // Header
      els.push(T(32, 108, 950, 11, 700, P.muted, d.breadcrumb));
      els.push(T(32, 139, 850, 40, 700, P.ink, "From insight to action."));
      els.push(T(32, 202, 960, 15, 400, P.muted, d.subtitle));

      // Status pill and generate button
      els.push(R(1044, 124, 364, 30, { bg: P.chip, rad: 15 }));
      els.push(T(1064, 133, 325, 10, 700, P.ink, d.status));
      els.push(R(1112, 190, 296, 46, { bg: P.nav, rad: 6 }));
      els.push(R(1130, 202, 15, 20, { bg: P.lime, rad: 2 }));
      els.push(R(1134, 208, 7, 1, { bg: P.nav }));
      els.push(R(1134, 212, 7, 1, { bg: P.nav }));
      els.push(T(1155, 205, 235, 13, 700, P.cream, "+  Generate Report"));

      els.push(...secondaryNav(d));
      els.push(R(32, 337, 1376, 1, { bg: P.line }));

      // Report overview cards
      els.push(T(32, 360, 500, 21, 700, P.ink, "Report overview"));
      [32, 380, 728, 1076].forEach((x, i) => {
        const c = d.summary[i];
        if (!c) return;
        els.push(R(x, 407, 328, 142, { bg: P.cream, bd: P.line, rad: 9 }));
        els.push(T(x + 22, 425, 34, 22, 700, P.ink, c.glyph));
        els.push(T(x + 306, 428, 34, 9, 700, P.muted, c.number, { align: "right" }));
        els.push(T(x + 22, 461, 280, 12, 700, P.muted, c.title));
        els.push(T(x + 22, 486, 284, c.size || 21, 700, P.ink, c.value));
        els.push(T(x + 22, 519, 280, 10, 400, P.muted, c.caption));
      });

      // Featured report
      els.push(T(32, 584, 600, 10, 700, P.muted, "FEATURED REPORT  /  TEMPLATE"));
      els.push(R(32, 610, 1376, 300, { bg: P.cream, bd: P.line, rad: 12 }));
      els.push(R(32, 610, 8, 300, { bg: P.lime, rad: 4 }));
      els.push(T(60, 634, 730, 26, 700, P.ink, d.featured.title));
      els.push(T(60, 674, 890, 13, 400, P.muted, d.featured.description));
      els.push(R(1118, 636, 250, 28, { bg: P.chip, rad: 14 }));
      els.push(T(1140, 644, 210, 10, 700, P.ink, d.featured.status));
      [
        [60, 725, 724],
        [490, 725, 724],
        [60, 795, 794],
        [490, 795, 794],
      ].forEach(([x, y, ty], i) => {
        const f = d.featured.items[i];
        if (!f) return;
        els.push(R(x, y, 25, 25, { bg: i === 0 ? P.lime : P.soft, rad: 6 }));
        els.push(T(x, y + 4, 25, 11, 700, P.ink, f.glyph, { align: "center" }));
        els.push(T(x + 37, ty, 360, 13, 700, P.ink, f.title));
        els.push(T(x + 37, ty + 22, 360, 10, 400, P.muted, f.desc));
      });
      els.push(R(1046, 837, 158, 40, { bg: P.nav, rad: 5 }));
      els.push(T(1046, 850, 158, 11, 700, P.cream, "Preview Report", { align: "center" }));
      els.push(R(1215, 837, 153, 40, { bg: P.chip, bd: P.line, rad: 5 }));
      els.push(T(1215, 850, 153, 11, 700, P.ink, "Generate PDF", { align: "center" }));
      els.push(T(60, 872, 960, 9, 400, P.muted, d.featured.meta));

      // Report builder (design mockup; controls are not yet wired)
      els.push(T(32, 946, 600, 22, 700, P.ink, "Build a new report"));
      els.push(T(32, 983, 1020, 12, 400, P.muted, d.builder.subtitle));
      els.push(R(32, 1018, 870, 600, { bg: P.cream, bd: P.line, rad: 10 }));
      els.push(T(56, 1041, 400, 10, 700, P.muted, "REPORT CONFIGURATION"));

      const fields = [
        { label: "RESERVOIR", x: 56, y: 1075, w: 390, value: "Select reservoir  ▾", by: 1095, ty: 1107 },
        { label: "STATE", x: 468, y: 1075, w: 185, value: "Select state  ▾", by: 1095, ty: 1107 },
        { label: "DISTRICT", x: 675, y: 1075, w: 201, value: "Select district  ▾", by: 1095, ty: 1107 },
        { label: "RIVER BASIN", x: 56, y: 1149, w: 390, value: "Select basin  ▾", by: 1169, ty: 1181 },
        { label: "REPORT TYPE", x: 468, y: 1149, w: 408, value: "Reservoir Risk Assessment  ▾", by: 1169, ty: 1181, ink: true },
      ];
      fields.forEach((f) => {
        els.push(T(f.x, f.y, f.w, 9, 700, P.muted, f.label));
        els.push(R(f.x, f.by, f.w, 38, { bg: P.cream, bd: P.line, rad: 5 }));
        els.push(T(f.x + 12, f.ty, f.w - 24, 11, 400, f.ink ? P.ink : P.muted, f.value));
      });

      els.push(T(56, 1224, 220, 9, 700, P.muted, "FORECAST HORIZON"));
      [
        { x: 56, label: "7 days", active: false },
        { x: 158, label: "14 days", active: true },
        { x: 270, label: "30 days", active: false },
      ].forEach((c) => {
        els.push(R(c.x, 1245, 90, 32, { bg: c.active ? P.nav : P.soft, bd: c.active ? null : P.line, rad: 16 }));
        els.push(T(c.x, 1254, 90, 10, 700, c.active ? P.cream : P.ink, c.label, { align: "center" }));
      });

      els.push(T(56, 1296, 250, 9, 700, P.muted, "INCLUDE IN REPORT"));
      [
        { x: 56, y: 1323, label: "Forecast charts", on: true, lx: 81, ly: 1322 },
        { x: 456, y: 1323, label: "Scenario comparisons", on: true, lx: 481, ly: 1322 },
        { x: 56, y: 1357, label: "Evidence citations", on: true, lx: 81, ly: 1356 },
        { x: 456, y: 1357, label: "Model health and uncertainty", on: false, lx: 481, ly: 1356 },
        { x: 56, y: 1391, label: "Mitigation recommendations", on: false, lx: 81, ly: 1390 },
      ].forEach((c) => {
        els.push(R(c.x, c.y, 15, 15, { bg: c.on ? P.lime : P.cream, bd: P.line, rad: 3 }));
        els.push(T(c.lx, c.ly, 365, 11, 400, P.ink, c.label));
      });

      els.push(T(56, 1441, 180, 9, 700, P.muted, "OUTPUT FORMAT"));
      els.push(R(56, 1462, 130, 32, { bg: P.soft, bd: P.line, rad: 5 }));
      els.push(T(70, 1471, 105, 11, 700, P.ink, "PDF Report"));
      els.push(R(56, 1532, 230, 44, { bg: P.nav, rad: 5 }));
      els.push(T(56, 1546, 230, 12, 700, P.cream, "Generate Report  →", { align: "center" }));
      els.push(T(56, 1587, 810, 10, 400, P.muted, d.builder.note));

      // Document preview
      els.push(R(926, 1018, 482, 600, { bg: P.cream, bd: P.line, rad: 10 }));
      els.push(T(950, 1041, 350, 10, 700, P.muted, "DOCUMENT PREVIEW"));
      els.push(R(958, 1074, 418, 432, { bg: P.page, bd: P.line, rad: 3 }));
      els.push(R(958, 1074, 418, 5, { bg: P.lime }));
      els.push(T(977, 1092, 370, 9, 700, P.ink, "WATERZERO  /  RESERVOIR FIELD ATLAS"));
      els.push(T(977, 1121, 370, 18, 700, P.ink, "Reservoir Risk Assessment"));
      els.push(T(977, 1152, 370, 9, 400, P.muted, "Karnataka  /  Krishna Basin  /  Select reservoir"));
      els.push(R(977, 1180, 380, 1, { bg: P.line }));
      els.push(T(977, 1195, 360, 9, 700, P.ink, "EXECUTIVE SUMMARY"));
      els.push(T(977, 1217, 368, 9, 400, P.muted, d.preview.summary));
      els.push(T(977, 1270, 370, 9, 700, P.ink, "STORAGE FORECAST  ·  ILLUSTRATIVE"));
      els.push(R(984, 1371, 356, 1, { bg: P.line }));
      const bars = d.preview.bars.slice(0, 8);
      bars.forEach((r, i) => {
        const h = Math.max(0, Math.min(r, 1)) * 73;
        els.push(R(991 + i * 44, 1371 - h, 19, h, { bg: i === 6 ? P.lime : P.bar, rad: 2 }));
      });
      els.push(T(977, 1380, 370, 8, 700, P.muted, "Illustrative data — not a live forecast"));
      els.push(T(977, 1411, 370, 9, 700, P.ink, "SCENARIOS  /  EVIDENCE  /  MITIGATION"));
      els.push(T(977, 1432, 370, 8, 400, P.muted, d.preview.scenarios));
      els.push(T(977, 1478, 370, 8, 700, P.muted, d.preview.status));
      els.push(T(950, 1525, 430, 10, 400, P.muted, d.preview.note));

      // Previous reports
      els.push(T(32, 1660, 600, 22, 700, P.ink, "Previous reports"));
      els.push(T(32, 1696, 800, 12, 400, P.muted, d.history.subtitle));
      els.push(R(32, 1731, 1376, 195, { bg: P.cream, bd: P.line, rad: 10 }));
      els.push(R(620, 1752, 48, 48, { bg: P.chip, rad: 10 }));
      els.push(T(620, 1763, 48, 22, 700, P.ink, "▤", { align: "center" }));
      els.push(T(430, 1812, 580, 18, 700, P.ink, d.history.title, { align: "center" }));
      els.push(T(260, 1844, 920, 12, 400, P.muted, d.history.body, { align: "center" }));
      els.push(R(612, 1881, 216, 32, { bg: P.nav, rad: 5 }));
      els.push(T(612, 1890, 216, 10, 700, P.cream, "Generate First Report", { align: "center" }));

      // Review workflow
      els.push(T(32, 1967, 650, 22, 700, P.ink, "Review before action"));
      els.push(T(32, 2002, 1000, 12, 400, P.muted, d.review.subtitle));
      els.push(R(32, 2037, 1376, 156, { bg: P.cream, bd: P.line, rad: 10 }));
      [68, 508, 948].forEach((x, i) => {
        const s = d.review.steps[i];
        if (!s) return;
        els.push(R(x, 2070, 32, 32, { bg: i === 0 ? P.lime : P.soft, rad: 16 }));
        els.push(T(x, 2079, 32, 10, 700, P.ink, `0${i + 1}`, { align: "center" }));
        els.push(T(x + 46, 2072, 260, 14, 700, P.ink, s.title));
        els.push(T(x + 46, 2096, 310, 10, 400, P.muted, s.desc));
      });
      els.push(R(398, 2085, 80, 1, { bg: P.line }));
      els.push(R(838, 2085, 80, 1, { bg: P.line }));
      els.push(T(68, 2141, 960, 11, 400, P.muted, d.review.note));
      els.push(R(1040, 2140, 158, 34, { bg: P.chip, bd: P.line, rad: 5 }));
      els.push(T(1040, 2150, 158, 10, 700, P.ink, "Mark for Review", { align: "center" }));
      els.push(R(1210, 2140, 158, 34, { bg: P.nav, rad: 5 }));
      els.push(T(1210, 2150, 158, 10, 700, P.cream, "Approve Report", { align: "center" }));

      return els;
    },
  };
})();
