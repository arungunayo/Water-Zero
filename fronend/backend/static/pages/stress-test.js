(function () {
  "use strict";
  const { R, T, C, topNav } = window.WZ;

  const TONE = {
    ink: "#0e2924",
    green: "#598733",
    lime: "#abc447",
    blue: "#2b7aad",
    alert: "#ed4529",
    muted: "#596b5e",
    light: "#ccd6c7",
    accent: "#bff033",
    cream: "#fcfbf2",
    sand: "#f5f2e5",
    track: "#e5ebdb",
    line: "#d1d4c2",
    dark: "#09211d",
  };

  const BAR_COLOR = { green: TONE.green, lime: TONE.lime, alert: TONE.alert, muted: TONE.muted, blue: TONE.blue };

  window.WZ_PAGES = window.WZ_PAGES || {};
  window.WZ_PAGES["stress-test"] = {
    w: 1440,
    h: 2057,
    bg: "#f5f2e5",
    title: "WaterZero — Demand Stress Test",
    api: "/api/stress-test",

    build(d) {
      const els = [];
      els.push(...topNav("dashboard"));

      // Header
      els.push(T(32, 108, 650, 10, 700, TONE.green, d.breadcrumb));
      els.push(T(32, 139, 720, 34, 700, TONE.ink, "Demand Stress Test"));
      els.push(T(32, 183, 1020, 14, 400, TONE.muted, d.subtitle));

      // Section pill nav
      els.push(R(465, 301, 558, 48, { bg: TONE.cream, bd: "#ccd4c4", rad: 24 }));
      els.push(T(495, 322, 50, 9, 500, TONE.muted, "Overview", { href: "/" }));
      els.push(T(549, 322, 62, 9, 500, TONE.muted, "Forecasts", { href: "/forecasts" }));
      els.push(R(615, 316, 84, 26, { bg: "#def0d1", rad: 14 }));
      els.push(T(629, 322, 70, 9, 600, TONE.ink, "Stress Test", { href: "/stress-test" }));
      els.push(T(717, 322, 58, 9, 500, TONE.muted, "Evidence", { href: "/evidence" }));
      els.push(T(793, 322, 76, 9, 500, TONE.muted, "Model health", { href: "/model-health" }));
      els.push(T(887, 322, 52, 9, 500, TONE.muted, "Reports", { href: "/reports" }));

      // Reservoir + status line
      els.push(R(32, 371, 208, 27, { bg: "#def0d1", rad: 14 }));
      els.push(T(42, 378, 188, 9, 600, TONE.ink, d.reservoir));
      els.push(T(258, 379, 410, 10, 500, TONE.muted, d.scenario_note));
      els.push(R(1110, 380, 7, 7, { bg: TONE.alert, rad: 4 }));
      els.push(T(1124, 376, 290, 10, 700, TONE[d.status.tone] || TONE.alert, d.status.label));

      // Scenario controls
      els.push(R(32, 418, 1376, 180, { bg: TONE.cream, bd: TONE.line, rad: 6 }));
      els.push(T(56, 438, 400, 10, 700, TONE.green, "01  /  SCENARIO CONTROLS"));
      els.push(T(56, 461, 460, 22, 700, TONE.ink, d.controls.title));
      els.push(T(56, 492, 900, 11, 400, TONE.muted, d.controls.note));
      [56, 388, 720, 1052].forEach((x, i) => {
        const c = d.controls.items[i];
        if (!c) return;
        els.push(T(x, 519, 260, 9, 700, TONE.muted, c.label));
        els.push(R(x, 539, 300, 38, { bg: TONE.sand, bd: TONE.line, rad: 4 }));
        els.push(T(x + 12, 551, 240, 11, 600, TONE.ink, c.value));
        els.push(T(x + 274, 551, 18, 11, 700, TONE.green, "▾"));
      });

      // Outcome banner
      els.push(R(32, 618, 1376, 126, { bg: TONE.dark, rad: 6 }));
      els.push(T(56, 638, 400, 10, 700, TONE.accent, "02  /  STRESS TEST OUTCOME"));
      els.push(T(56, 661, 650, 26, 700, TONE.cream, d.outcome.title));
      els.push(T(56, 698, 850, 11, 400, TONE.light, d.outcome.subtitle));
      els.push(T(1030, 639, 310, 9, 700, TONE.light, d.outcome.cover_label));
      els.push(T(1030, 659, 280, 30, 700, TONE.accent, d.outcome.cover_value));
      els.push(T(1030, 702, 320, 9, 500, TONE.cream, d.outcome.cover_note));

      // Scenario comparison (bars)
      els.push(R(32, 766, 880, 430, { bg: TONE.cream, bd: TONE.line, rad: 6 }));
      els.push(T(56, 786, 440, 10, 700, TONE.green, "03  /  SCENARIO COMPARISON"));
      els.push(T(56, 809, 740, 21, 700, TONE.ink, d.comparison.title));
      els.push(T(56, 839, 720, 11, 400, TONE.muted, d.comparison.subtitle));
      const maxDays = Math.max(...d.comparison.bars.map((b) => b.days), 1);
      d.comparison.bars.slice(0, 3).forEach((b, i) => {
        const y0 = [888, 968, 1048][i];
        const w = (b.days / maxDays) * 620;
        els.push(T(58, y0 + 1, 150, 10, 700, TONE.ink, b.label));
        els.push(R(200, y0, 630, 22, { bg: TONE.track, rad: 3 }));
        els.push(R(200, y0, w, 22, { bg: BAR_COLOR[b.color] || TONE.green, rad: 3 }));
        els.push(T(200 + w + 12, y0 + 4, 95, 10, 700, TONE.ink, `${b.days} days`));
        els.push(T(58, y0 + 25, 200, 9, 500, TONE[b.note_tone] || TONE.muted, b.note));
      });

      // Risk interpretation
      els.push(R(934, 766, 474, 430, { bg: TONE.cream, bd: TONE.line, rad: 6 }));
      els.push(T(958, 786, 390, 10, 700, TONE.alert, "04  /  RISK INTERPRETATION"));
      els.push(T(958, 809, 370, 21, 700, TONE.ink, d.risk.title));
      els.push(C((stage, h) => h.donut(stage, 987, 862, 114, d.risk.ratio, TONE.alert, TONE.track, 11)));
      els.push(T(987, 912, 114, 11, 700, TONE.ink, d.risk.center, { align: "center" }));
      els.push(T(1120, 874, 230, 9, 700, TONE.muted, d.risk.case_label));
      els.push(T(1120, 895, 245, 15, 600, TONE.ink, d.risk.case_title));
      els.push(T(1120, 923, 240, 12, 400, TONE.muted, d.risk.case_note));
      els.push(R(958, 1004, 420, 1, { bg: TONE.line }));
      [1023, 1051, 1079].forEach((y, i) => {
        const row = d.risk.rows[i];
        if (!row) return;
        els.push(T(958, y, 150, 10, 500, TONE.ink, row.label));
        els.push(T(1240, y, 130, 10, 400, TONE[row.tone] || TONE.muted, row.value));
      });

      // Sensitivity analysis
      els.push(R(32, 1218, 880, 260, { bg: TONE.cream, bd: TONE.line, rad: 6 }));
      els.push(T(56, 1238, 400, 10, 700, TONE.green, "05  /  SENSITIVITY ANALYSIS"));
      els.push(T(56, 1261, 520, 21, 700, TONE.ink, d.sensitivity.title));
      els.push(T(56, 1290, 740, 11, 400, TONE.muted, d.sensitivity.subtitle));
      d.sensitivity.bars.slice(0, 3).forEach((b, i) => {
        const y = [1328, 1370, 1412][i];
        const w = Math.min(Math.max(b.ratio, 0), 1) * 580;
        els.push(T(58, y, 160, 10, 700, TONE.ink, b.label));
        els.push(R(220, y, 580, 15, { bg: TONE.track, rad: 3 }));
        els.push(R(220, y, w, 15, { bg: BAR_COLOR[b.color] || TONE.green, rad: 3 }));
        els.push(T(810, y + 2, 90, 8, 400, TONE.muted, b.status));
      });

      // Assumptions and limitations
      els.push(R(934, 1218, 474, 260, { bg: TONE.sand, bd: TONE.line, rad: 6 }));
      els.push(T(958, 1238, 390, 10, 700, TONE.green, "ASSUMPTIONS & LIMITATIONS"));
      els.push(T(958, 1261, 360, 21, 700, TONE.ink, d.assumptions.title));
      [1301, 1336, 1371, 1406].forEach((y, i) => {
        const a = d.assumptions.items[i];
        if (!a) return;
        els.push(R(960, y, 7, 7, { bg: TONE[a.tone] || TONE.green, rad: 4 }));
        els.push(T(978, y - 3, 400, 10, 400, TONE.ink, a.text));
      });

      // Footer
      els.push(R(32, 1500, 1376, 130, { bg: TONE.dark, rad: 6 }));
      els.push(T(56, 1520, 430, 10, 700, TONE.accent, "06  /  EVIDENCE & NEXT STEPS"));
      els.push(T(56, 1543, 750, 19, 700, TONE.cream, d.footer.title));
      els.push(T(56, 1575, 810, 11, 400, TONE.light, d.footer.subtitle));
      els.push(R(1090, 1544, 270, 36, { bg: "#def0d1", rad: 18 }));
      els.push(T(1113, 1555, 235, 10, 700, TONE.ink, "VIEW OFFICIAL EVIDENCE  ↗", { href: "/evidence" }));

      return els;
    },
  };
})();
