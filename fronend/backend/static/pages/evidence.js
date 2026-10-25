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
    accent: "#bff033",
    cream: "#fcfbf2",
    sand: "#f5f2e5",
    track: "#e5ebdb",
    line: "#d1d4c2",
    dark: "#09211d",
    lime: "#def0d1",
  };

  const pick = (tone) => TONE[tone] || TONE.muted;

  window.WZ_PAGES = window.WZ_PAGES || {};
  window.WZ_PAGES.evidence = {
    w: 1440,
    h: 2180,
    bg: "#f5f2e5",
    title: "WaterZero — Evidence & Verification",
    api: "/api/evidence",

    build(d) {
      const els = [];
      els.push(...topNav("dashboard"));

      // Header
      els.push(T(32, 108, 650, 10, 700, TONE.green, d.breadcrumb));
      els.push(T(32, 139, 800, 32, 700, TONE.ink, "Evidence & Verification"));
      els.push(T(32, 183, 1040, 13, 400, TONE.muted, d.subtitle));

      // Section pill nav
      els.push(R(465, 301, 558, 48, { bg: TONE.cream, bd: "#ccd4c4", rad: 24 }));
      els.push(R(707, 314, 84, 26, { bg: TONE.lime, rad: 16 }));
      els.push(T(495, 322, 50, 9, 500, TONE.muted, "Overview", { href: "/" }));
      els.push(T(551, 322, 62, 9, 500, TONE.muted, "Forecasts", { href: "/forecasts" }));
      els.push(T(631, 322, 70, 9, 500, TONE.muted, "Stress Test", { href: "/stress-test" }));
      els.push(T(719, 322, 58, 9, 600, TONE.ink, "Evidence", { href: "/evidence" }));
      els.push(T(795, 322, 76, 9, 500, TONE.muted, "Model health", { href: "/model-health" }));
      els.push(T(889, 322, 52, 9, 500, TONE.muted, "Reports", { href: "/reports" }));

      // Source selector, sync, refresh, state
      els.push(R(32, 472, 275, 27, { bg: TONE.lime, rad: 14 }));
      els.push(T(42, 479, 255, 9, 600, TONE.ink, d.reservoir));
      els.push(T(330, 480, 280, 9, 500, TONE.muted, d.sync));
      els.push(R(1060, 470, 160, 34, { bg: TONE.dark, rad: 17 }));
      els.push(T(1077, 481, 140, 9, 700, TONE.cream, "↻  REFRESH EVIDENCE"));
      els.push(R(1240, 484, 7, 7, { bg: TONE.amber, rad: 4 }));
      els.push(T(1253, 480, 160, 9, 700, pick(d.status.tone), d.status.label));
      els.push(T(32, 516, 1100, 10, 500, TONE.muted, d.note));

      // KPI cards
      [32, 382, 732, 1082].forEach((x, i) => {
        const k = d.kpis[i];
        if (!k) return;
        els.push(R(x, 546, 326, 84, { bg: TONE.cream, bd: TONE.line, rad: 5 }));
        els.push(T(x + 14, 559, 285, 9, 700, TONE.muted, k.label));
        els.push(T(x + 14, 578, 285, 23, 700, pick(k.tone), k.value));
        els.push(T(x + 14, 608, 295, 8, 400, TONE.muted, k.note));
      });

      // Research workflow
      els.push(R(32, 648, 1376, 190, { bg: TONE.cream, bd: TONE.line, rad: 6 }));
      els.push(T(56, 668, 500, 10, 700, TONE.green, "01  /  LIVE RESEARCH WORKFLOW"));
      els.push(T(56, 690, 800, 20, 700, TONE.ink, d.workflow.title));
      [56, 386, 716, 1046].forEach((x, i) => {
        const s = d.workflow.stages[i];
        if (!s) return;
        els.push(R(x, 728, 300, 72, { bg: TONE.sand, rad: 4 }));
        els.push(R(x + 14, 742, 8, 8, { bg: pick(s.tone), rad: 4 }));
        els.push(T(x + 30, 738, 250, 10, 700, TONE.ink, s.title));
        els.push(T(x + 14, 757, 260, 9, 500, pick(s.tone), s.status));
        els.push(T(x + 14, 777, 270, 8, 400, TONE.muted, s.detail));
        if (i < 3) els.push(R(x + 302, 762, 28, 2, { bg: TONE.line }));
      });
      els.push(T(56, 811, 450, 8, 700, TONE.muted, d.workflow.activity_label));
      els.push(T(390, 807, 970, 10, 400, TONE.muted, d.workflow.activity));

      // Search and filter toolbar
      els.push(R(32, 856, 1376, 106, { bg: TONE.cream, bd: TONE.line, rad: 6 }));
      els.push(T(56, 874, 350, 9, 700, TONE.green, "02  /  SEARCH & FILTER"));
      els.push(R(56, 895, 340, 36, { bg: TONE.sand, bd: TONE.line, rad: 4 }));
      els.push(T(68, 907, 315, 10, 400, TONE.muted, d.filters.search));
      [
        { x: 414, w: 175 },
        { x: 601, w: 175 },
        { x: 788, w: 175 },
        { x: 975, w: 205 },
        { x: 1190, w: 190 },
      ].forEach((f, i) => {
        const item = d.filters.items[i];
        if (!item) return;
        els.push(T(f.x, 887, f.w, 8, 700, TONE.muted, item.label));
        els.push(R(f.x, 905, f.w, 27, { bg: TONE.sand, bd: TONE.line, rad: 4 }));
        els.push(T(f.x + 9, 914, f.w - 18, 9, 500, TONE.ink, item.value));
      });

      // Source review queue
      els.push(R(32, 980, 820, 510, { bg: TONE.cream, bd: TONE.line, rad: 6 }));
      els.push(T(56, 1000, 400, 10, 700, TONE.green, "03  /  EVIDENCE SOURCES"));
      els.push(T(56, 1022, 480, 20, 700, TONE.ink, d.sources.title));
      els.push(T(56, 1051, 600, 9, 700, TONE.muted, d.sources.status_line));
      [1080, 1205, 1330].forEach((y, i) => {
        const s = d.sources.items[i];
        if (!s) return;
        els.push(R(56, y, 772, 108, { bg: TONE.sand, bd: TONE.line, rad: 4 }));
        els.push(R(56, y, 4, 108, { bg: pick(s.tone) }));
        els.push(T(72, y + 12, 460, 13, 600, TONE.ink, s.title));
        els.push(T(72, y + 35, 480, 8, 700, TONE.muted, s.tag));
        els.push(T(72, y + 53, 280, 9, 400, TONE.muted, s.publication));
        els.push(T(72, y + 73, 310, 9, 500, pick(s.tone), s.stance));
        els.push(R(650, y + 12, 154, 20, { bg: TONE.track, rad: 10 }));
        els.push(T(660, y + 18, 140, 8, 700, pick(s.tone), s.pill));
        els.push(T(590, y + 78, 220, 8, 500, TONE.ink, s.actions));
      });
      els.push(R(56, 1450, 772, 24, { bg: TONE.track, rad: 3 }));
      els.push(T(68, 1457, 740, 9, 400, TONE.muted, d.sources.footer));

      // Selected source detail
      els.push(R(874, 980, 534, 510, { bg: TONE.cream, bd: TONE.line, rad: 6 }));
      els.push(T(898, 1000, 360, 10, 700, TONE.blue, "04  /  SELECTED SOURCE"));
      els.push(T(898, 1022, 400, 20, 700, TONE.ink, d.detail.title));
      els.push(R(898, 1060, 486, 55, { bg: TONE.sand, rad: 4 }));
      els.push(T(912, 1070, 450, 12, 600, TONE.ink, d.detail.banner_title));
      els.push(T(912, 1091, 455, 9, 400, TONE.muted, d.detail.banner_body));
      [1132, 1175, 1218, 1261, 1304, 1347].forEach((y, i) => {
        const row = d.detail.rows[i];
        if (!row) return;
        els.push(T(898, y, 240, 8, 700, TONE.muted, row.label));
        els.push(T(898, y + 15, 450, 10, 500, TONE.ink, row.value));
        if (i < 5) els.push(R(898, y + 37, 486, 1, { bg: TONE.line }));
      });
      els.push(R(898, 1402, 150, 32, { bg: TONE.sand, bd: TONE.line, rad: 16 }));
      els.push(T(914, 1413, 125, 9, 700, TONE.ink, "MARK FOR REVIEW"));
      els.push(R(1060, 1402, 152, 32, { bg: TONE.dark, rad: 16 }));
      els.push(T(1079, 1413, 120, 9, 700, TONE.cream, "OPEN SOURCE ↗"));

      // Verification summary
      els.push(R(32, 1510, 1376, 250, { bg: TONE.cream, bd: TONE.line, rad: 6 }));
      els.push(T(56, 1530, 500, 10, 700, TONE.green, "05  /  VERIFICATION & SOURCE QUALITY"));
      els.push(T(56, 1552, 540, 20, 700, TONE.ink, d.verification.title));
      els.push(C((stage, h) => h.donut(stage, 76, 1596, 108, null, TONE.green, TONE.track, 10)));
      els.push(T(76, 1643, 108, 17, 700, TONE.ink, "—", { align: "center" }));
      els.push(T(210, 1613, 460, 10, 400, TONE.muted, d.verification.legend));
      els.push(T(210, 1640, 420, 10, 400, TONE.muted, d.verification.note));
      els.push(T(710, 1594, 250, 9, 700, TONE.muted, "SOURCE FRESHNESS"));
      d.verification.freshness.slice(0, 3).forEach((f, i) => {
        const y = [1620, 1655, 1690][i];
        els.push(T(710, y, 100, 9, 500, TONE.ink, f.label));
        els.push(R(818, y, 300, 12, { bg: TONE.track, rad: 3 }));
        els.push(T(1130, y, 35, 9, 400, TONE.muted, f.count));
      });
      els.push(T(1190, 1594, 190, 9, 700, TONE.muted, "SOURCE TYPE DISTRIBUTION"));
      d.verification.types.slice(0, 3).forEach((t, i) => {
        const y = [1620, 1655, 1690][i];
        els.push(T(1190, y, 90, 8, 500, TONE.ink, t.label));
        els.push(R(1280, y, 90, 10, { bg: TONE.track, rad: 3 }));
        els.push(T(1375, y, 25, 8, 400, TONE.muted, t.count));
      });
      els.push(T(56, 1724, 800, 9, 400, TONE.muted, d.verification.caveat));

      // Conflicts
      els.push(R(32, 1780, 1376, 150, { bg: TONE.cream, bd: TONE.line, rad: 6 }));
      els.push(T(56, 1800, 560, 10, 700, TONE.alert, "06  /  CONFLICTING OR INCONSISTENT REPORTS"));
      els.push(T(56, 1822, 520, 18, 700, TONE.ink, d.conflicts.title));
      els.push(T(56, 1852, 900, 11, 400, TONE.muted, d.conflicts.body));
      els.push(R(1110, 1818, 250, 25, { bg: TONE.track, rad: 13 }));
      els.push(T(1124, 1826, 220, 8, 700, TONE.alert, d.conflicts.pill));

      // Official source comparison table (header + empty state)
      els.push(R(32, 1950, 1376, 112, { bg: TONE.cream, bd: TONE.line, rad: 6 }));
      els.push(T(56, 1968, 500, 10, 700, TONE.green, "07  /  OFFICIAL SOURCE COMPARISON"));
      [
        [56, "SOURCE"],
        [245, "ORGANIZATION"],
        [435, "PUBLICATION DATE"],
        [590, "OBSERVATION PERIOD"],
        [780, "REPORTED FINDING"],
        [1040, "STATUS / STANCE"],
        [1260, "ACTIONS"],
      ].forEach(([x, label]) => els.push(T(x, 1994, 180, 8, 700, TONE.muted, label)));
      els.push(R(56, 2012, 1328, 1, { bg: TONE.line }));
      els.push(T(56, 2025, 1100, 10, 400, TONE.muted, d.comparison.empty));

      // Audit trail and forecast traceability
      els.push(R(32, 2080, 680, 84, { bg: TONE.dark, rad: 5 }));
      els.push(T(50, 2095, 400, 9, 700, TONE.accent, "08  /  EVIDENCE AUDIT TRAIL"));
      els.push(T(50, 2117, 620, 10, 400, TONE.cream, d.audit.text));
      els.push(R(730, 2080, 678, 84, { bg: TONE.cream, bd: TONE.line, rad: 5 }));
      els.push(T(748, 2095, 610, 9, 700, TONE.green, "09  /  HOW EVIDENCE SUPPORTS THE FORECAST"));
      els.push(T(748, 2117, 620, 9, 500, TONE.ink, d.traceability.text));

      return els;
    },
  };
})();
