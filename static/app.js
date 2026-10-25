/*
 * WaterZero dashboard.
 *
 * All numbers, series, and labels come from GET /api/dashboard. Layout and
 * static copy live in index.html. Set window.WATERZERO_API_BASE before this
 * script loads if the API is hosted on a different origin.
 */
(function () {
  "use strict";

  const API_BASE = (window.WATERZERO_API_BASE || "").replace(/\/$/, "");
  const SVG_NS = "http://www.w3.org/2000/svg";
  const INTER = "Inter, system-ui, sans-serif";

  const C = {
    grid: "#c7cfba",
    observed: "#4f7a2e",
    forecast: "#38789e",
    threshold: "#e04f2e",
    muted: "#4d6359",
    band: "#38789e",
  };

  const TONE = {
    risk: { fg: "#d43821" },
    validate: { fg: "#337aa3" },
    stale: { fg: "#57753b" },
  };

  // Evidence log row geometry, measured from the Figma frame.
  const LOG_LAYOUT = [
    {
      date: 115, title: 131.5, source: 151.1,
      pill: [362, 127, 235.94, 31, 20.67], pillText: [380.94, 135.61],
      dateSize: 12, titleSize: 15, sourceSize: 12, pillSize: 10.68,
    },
    {
      date: 178.8, title: 191.5, source: 211.1,
      pill: [431.44, 183.42, 158.04, 20.76, 13.84], pillText: [444.13, 189.19],
      dateSize: 8.31, titleSize: 12.11, sourceSize: 7.84, pillSize: 7.15,
    },
    {
      date: 238.8, title: 251.5, source: 271.1,
      pill: [431.44, 243.4, 158.04, 20.76, 13.84], pillText: [444.13, 249.17],
      dateSize: 8.31, titleSize: 12.11, sourceSize: 7.84, pillSize: 7.15,
    },
  ];
  const LOG_DIVIDERS = [175.34, 235.33];

  // ---------- helpers ----------

  const $ = (id) => document.getElementById(id);
  const fmt = (v, d = 1) => Number(v).toFixed(d);
  const signedMinus = (v, d = 1) => (v < 0 ? "−" : "") + Math.abs(v).toFixed(d);
  const clamp = (v, lo = 0, hi = 1) => Math.min(hi, Math.max(lo, v));

  function setText(id, value) {
    const node = $(id);
    if (node) node.textContent = value;
  }

  function svgEl(tag, attrs, parent) {
    const el = document.createElementNS(SVG_NS, tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (v != null) el.setAttribute(k, v);
    }
    if (parent) parent.appendChild(el);
    return el;
  }

  function abs(parent, x, y, w, h, css, text) {
    const n = document.createElement("div");
    n.className = "a";
    n.style.left = `${x}px`;
    n.style.top = `${y}px`;
    if (w != null) n.style.width = `${w}px`;
    if (h != null) n.style.height = `${h}px`;
    Object.assign(n.style, css || {});
    if (text != null) n.textContent = text;
    parent.appendChild(n);
    return n;
  }

  function svgText(parent, str, x, y, size, fill, weight = 400) {
    const t = svgEl(
      "text",
      {
        x, y,
        "font-family": INTER,
        "font-size": size,
        "font-weight": weight,
        fill,
        style: "white-space:pre",
      },
      parent
    );
    t.textContent = str;
    return t;
  }

  // Prepare an existing <svg> so its viewBox uses stage coordinates.
  function prepareSvg(id, x, y, w, h) {
    const s = $(id);
    if (!s) return null;
    s.setAttribute("viewBox", `${x} ${y} ${w} ${h}`);
    s.setAttribute("width", w);
    s.setAttribute("height", h);
    s.style.overflow = "hidden";
    s.replaceChildren();
    return s;
  }

  // Step path: horizontal run, then vertical rise/fall. Matches the Figma style.
  function steppedPath(points) {
    if (!points || !points.length) return "";
    let d = `M${points[0][0]},${points[0][1]}`;
    for (let i = 1; i < points.length; i++) {
      const [x, y] = points[i];
      d += ` H${x} V${y}`;
    }
    return d;
  }

  // Linear map from data values to pixel y, padded to include extra values.
  function yScale(values, top, bottom, extra = []) {
    const all = [...values, ...(Array.isArray(extra) ? extra : [extra[0], extra[1]])].filter((v) => v != null && !isNaN(v));
    const min = all.length ? Math.min(...all) : 0;
    const max = all.length ? Math.max(...all) : 100;
    const span = max - min || 1;
    return (v) => {
      const clamped = Math.max(min, Math.min(max, v));
      return top + ((max - clamped) / span) * (bottom - top);
    };
  }

  // ---------- sections ----------

  function renderStorage(d) {
    const s = d.storage;

    setText("breadcrumb", d.meta.breadcrumb);
    setText("liveLabel", d.meta.live_label);

    setText("storagePct", fmt(s.current_pct));
    const meter = $("storageMeterFill");
    if (meter) {
      meter.style.width = `${(clamp(s.current_pct, 0, 100) / 100) * 744}px`;
    }
    setText(
      "storageVolume",
      `${fmt(s.tmc_live, 2)} TMC  /  ${fmt(s.tmc_gross_capacity, 2)} TMC GROSS CAPACITY`
    );

    setText("storageSecondary", `${fmt(s.forecast_7d_pct)}%`);
    setText("outlook14", `${fmt(s.outlook_14d_pct)}%`);
    setText(
      "outlookDelta",
      `${signedMinus(s.change_14d_pts)} pts  /  range ${fmt(s.range_14d[0])}–${fmt(s.range_14d[1])}%`
    );
  }

  function renderOverviewCards(d) {
    const s = d.storage;

    // Card 01: reservoir overview
    setText("b1Value", `${fmt(s.current_pct)}%`);
    setText("b1Note", `${fmt(s.tmc_live, 2)} / ${fmt(s.tmc_gross_capacity, 2)} TMC`);
    renderMiniTrend(s.trend);

    // Card 02: forecast chart
    setText("b2Value", `${fmt(s.outlook_14d_pct)}%`);
    setText(
      "b2Note",
      `7D ${fmt(s.forecast_7d_pct)}%   ·   14D ${fmt(s.outlook_14d_pct)}%`
    );
    renderMiniForecast(s.forecast_trend, s.range_14d);

    // Card 03: stress test
    setText("b3Value", `${d.decision.cover_days} days`);
    setText("b3Note", d.decision.cover_vs_monsoon);
    renderStressBars(d.stress_bars);

    // Card 04: evidence panel
    setText(
      "b4Value",
      `${d.evidence.summary.verified} VERIFIED · ${d.evidence.summary.stale} STALE`
    );
    renderEvidencePanel(d.evidence.items);

    // Card 05: model reliability
    setText("b5Value", `${fmt(d.reliability.mae)} / ${fmt(d.reliability.rmse)} pts`);
    setText("b5Note", d.reliability.note);
    renderReliabilityBars(d.reliability.bars);
  }

  function renderMiniTrend(values) {
    if (!values || !values.length) return;
    const svg = prepareSvg("miniTrend", 46, 455, 230, 60);
    if (!svg) return;
    const y = yScale(values, 466, 502);
    const n = Math.max(values.length - 1, 1);
    const step = (220 - 52) / n;
    const pts = values.map((v, i) => [52 + i * step, y(v)]);
    svgEl(
      "path",
      { d: steppedPath(pts), fill: "none", stroke: "#457829", "stroke-width": 2.6, "stroke-linejoin": "round" },
      svg
    );
  }

  function renderMiniForecast(values, range) {
    if (!values || !values.length) return;
    const svg = prepareSvg("miniForecast", 326, 440, 226, 70);
    if (!svg) return;
    const y = yScale(values, 448, 496, range || []);

    if (range && (range[0] != null || range[1] != null)) {
      const r0 = range[0] ?? values[0];
      const r1 = range[1] ?? values[values.length - 1];
      const y0 = y(r0);
      const y1 = y(r1);
      const top = Math.min(y0, y1);
      const height = Math.abs(y1 - y0);
      svgEl(
        "rect",
        { x: 430, y: top, width: 75, height: Math.max(height, 4), rx: 3, fill: "#e3f0f2" },
        svg
      );
    }

    const n = Math.max(values.length - 1, 1);
    const step = (510 - 336) / n;
    const pts = values.map((v, i) => [336 + i * step, y(v)]);
    svgEl(
      "path",
      { d: steppedPath(pts), fill: "none", stroke: "#2b7aad", "stroke-width": 2.6, "stroke-linejoin": "round" },
      svg
    );
  }

  function renderStressBars(bars) {
    const box = $("stressBars");
    const labels = $("stressLabels");
    if (!box || !labels) return;
    const colors = { LOW: "#2b7aad", BASE: "#457829", HIGH: "#e84526" };
    box.replaceChildren();
    labels.replaceChildren();

    bars.forEach((b, i) => {
      const bar = document.createElement("div");
      bar.className = "bar";
      bar.style.width = "28px";
      bar.style.height = `${clamp(b.ratio) * 57}px`;
      bar.style.background = colors[b.label] || "#457829";
      box.appendChild(bar);

      abs(labels, 623 + i * 48, 515, 42, 10, {
        font: "700 7px/normal " + INTER,
        color: "#596b5c",
        textAlign: "center",
      }, b.label);
    });
  }

  function renderEvidencePanel(items) {
    const box = $("evidenceRows");
    if (!box) return;
    box.replaceChildren();

    items.slice(0, 3).forEach((it, i) => {
      const y = i * 15.67;
      abs(box, 0, y, 15.67, 12.31, {
        background: "#e8f0d9",
        border: "1.12px solid #457829",
        borderRadius: "1.12px",
      });
      abs(box, 54.83, y, 125.33, 3.36, { background: "#ccd1ba", borderRadius: "1.12px" });
      abs(box, 71.62, y + 6.71, 92.88, 3.36, { background: "#ccd1ba", borderRadius: "1.12px" });
      abs(box, 218.21, y, 8.95, 8.95, {
        background: it.tone === "stale" ? "#e84526" : "#457829",
        borderRadius: "50%",
      });
    });
  }

  function renderReliabilityBars(bars) {
    const box = $("relBars");
    if (!box) return;
    box.replaceChildren();
    bars.forEach((r, i) => {
      const bar = document.createElement("div");
      bar.className = "bar";
      bar.style.width = "15px";
      bar.style.height = `${clamp(r) * 38}px`;
      bar.style.background = i === bars.length - 1 ? "#c4f52e" : "#57855c";
      box.appendChild(bar);
    });
  }

  function renderTrajectory(t) {
    const X0 = 85;
    const X1 = 935;
    const X_SPLIT = 685;
    const Y_TOP = 1060;
    const Y_BOT = 1285;
    const yMin = t.y_min ?? 0;
    const yMax = t.y_max ?? 100;

    const py = (p) => {
      const clamped = Math.max(yMin, Math.min(yMax, p));
      return Y_TOP + ((yMax - clamped) / (yMax - yMin)) * (Y_BOT - Y_TOP);
    };

    const svg = prepareSvg("trajectory", 32, 1015, 948, 340);
    if (!svg) return;

    // Gridlines and y labels
    const step = (yMax - yMin > 50) ? 20 : 10;
    for (let p = yMax; p >= yMin; p -= step) {
      const y = py(p);
      svgEl("line", { x1: X0, x2: X1, y1: y, y2: y, stroke: C.grid, "stroke-width": 1 }, svg);
      svgText(svg, `${p}%`, 44, y + 3, 9, C.muted, 500);
    }

    // Step series math
    const obsN = Math.max(t.observed.length - 1, 1);
    const obsStep = (X_SPLIT - X0) / obsN;
    const obs = t.observed.map((v, i) => [X0 + i * obsStep, py(v)]);

    const fcN = Math.max(t.forecast.length, 1);
    const fcStep = (X1 - X_SPLIT) / fcN;
    const fc = t.forecast.map((p, j) => [X_SPLIT + (j + 1) * fcStep, py(p.pct)]);

    const lastObs = obs[obs.length - 1] || [X_SPLIT, py(yMin)];

    // Forecast uncertainty band (if provided)
    const hasBand = t.forecast.some((p) => p.low != null && p.high != null);
    if (hasBand) {
      const upper = t.forecast.map((p, j) => [X_SPLIT + (j + 1) * fcStep, py(p.high ?? p.pct)]);
      const lower = t.forecast.map((p, j) => [X_SPLIT + (j + 1) * fcStep, py(p.low ?? p.pct)]).reverse();
      const points = [lastObs, ...upper, ...lower].map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join(" ");
      svgEl("polygon", { points, fill: C.band, "fill-opacity": 0.14 }, svg);
    }

    // Critical threshold line with label plate
    const ty = py(t.threshold_pct);
    svgEl("line", { x1: X0, x2: X1, y1: ty, y2: ty, stroke: C.threshold, "stroke-width": 2, "stroke-dasharray": "6 4" }, svg);
    const plateY = Math.min(Math.max(ty - 12, Y_TOP - 10), Y_BOT - 15);
    svgEl("rect", { x: 670, y: plateY, width: 250, height: 24, rx: 12, fill: "#fcfbf2", stroke: C.threshold, "stroke-width": 1 }, svg);
    svgText(
      svg,
      `${fmt(t.threshold_pct)}%  /  CRITICAL PLANNING LINE`,
      685,
      plateY + 15,
      8.5,
      C.threshold,
      700
    );

    // Draw observed series
    svgEl(
      "path",
      { d: steppedPath(obs), fill: "none", stroke: C.observed, "stroke-width": 3.2 },
      svg
    );

    // Draw forecast series
    svgEl(
      "path",
      { d: steppedPath([lastObs, ...fc]), fill: "none", stroke: C.forecast, "stroke-width": 3.2 },
      svg
    );

    // X-axis labels
    const [a, b, c] = t.axis_labels || ["JUL", "TODAY", "NOV"];
    svgText(svg, a, X0, 1318, 9, C.muted, 500);
    svgText(svg, b, X_SPLIT - 20, 1318, 9, C.muted, 500);
    svgText(svg, c, X1 - 50, 1318, 9, C.muted, 500);

    // Legend
    const legend = [
      { x: X0, color: C.observed, label: "Observed", tx: X0 + 26 },
      { x: X0 + 130, color: C.forecast, label: "Forecast", tx: X0 + 156 },
      { x: X0 + 260, color: C.threshold, label: "Threshold", tx: X0 + 286 },
    ];
    legend.forEach((item) => {
      svgEl("rect", { x: item.x, y: 1332, width: 18, height: 4, rx: 1, fill: item.color }, svg);
      svgText(svg, item.label, item.tx, 1336, 9, C.muted, 400);
    });
  }

  function renderRisk(d) {
    const r = d.risk;
    setText("riskTitleLabel", `CRITICAL THRESHOLD · ${fmt(r.threshold_pct)}%`);
    setText("riskDays", `${r.days_min}–${r.days_max}`);
    setText("riskText", r.explanation);
    setText("depletion", `−${fmt(r.daily_depletion_pct)}% / DAY`);
  }

  function renderDecision(d) {
    const dec = d.decision;
    setText("demandLabel", dec.demand_label);
    setText("rainfallValue", dec.rainfall_value);
    setText("coverDays", `${dec.cover_days} DAYS`);
    setText("coverDelta", dec.cover_vs_monsoon);
    const fill = $("runwayFill");
    if (fill) fill.style.width = `${clamp(dec.runway_ratio) * 246}px`;
  }

  function renderEvidenceLog(items) {
    const box = $("evidenceLogRows");
    if (!box) return;
    box.replaceChildren();

    items.forEach((it, i) => {
      const L = LOG_LAYOUT[i];
      if (!L) return;

      if (i > 0) {
        abs(box, 13.84, LOG_DIVIDERS[i - 1], 583.71, 0.77, { background: "#cfd1bf" });
      }

      abs(box, 14, L.date, 380, 16, {
        font: `700 ${L.dateSize}px/normal ${INTER}`,
        color: "#5e6e5e",
        letterSpacing: "0.3px",
        whiteSpace: "pre",
      }, it.date);

      abs(box, 13.84, L.title, 392, 20, {
        font: `600 ${L.titleSize}px/normal ${INTER}`,
        color: "#132e2b",
        whiteSpace: "pre",
      }, it.title);

      abs(box, 13.84, L.source, 300, 14, {
        font: `500 ${L.sourceSize}px/normal ${INTER}`,
        color: "#5e6e5e",
        letterSpacing: "0.17px",
        whiteSpace: "pre",
      }, it.source);

      const [px, py, pw, ph, pr] = L.pill;
      const pill = abs(box, px, py, pw, ph, {
        background: "#e5e8db",
        borderRadius: `${pr}px`,
      });
      const tone = TONE[it.tone] || TONE.validate;
      abs(
        pill,
        L.pillText[0] - px,
        L.pillText[1] - py,
        null,
        null,
        {
          font: `700 ${L.pillSize}px/normal ${INTER}`,
          color: tone.fg,
          letterSpacing: "0.17px",
          whiteSpace: "pre",
        },
        it.status_label
      );
    });
  }

  function updateDynamicCopy(res) {
    const isHirakud = res === "hirakud";
    if (isHirakud) {
      setText("heroTitle", "WaterZero: Reservoir Intelligence.");
      setText("heroSubtitle", "Active machine learning forecasts and conformal uncertainty bounds for Hirakud Reservoir (Mahanadi Basin).");
      setText("trajectoryTitle", "Seasonal Storage Drawdown (Monsoon Window)");
      setText("trajectoryDesc", "Observed levels from official CWC sensor telemetry and 30-day forward ML predictions with 80% conformal confidence intervals.");
      setText("riskWatchTitle", "Safe Operational Buffer.");
    } else {
      setText("heroTitle", "Water,\nunder pressure.");
      setText("heroSubtitle", "An early-warning read on storage, inflow and the decisions\nthat may matter before the next monsoon window.");
      setText("trajectoryTitle", "The reserve is trending down.");
      setText("trajectoryDesc", "Observed levels and a 30-day model outlook. The dotted threshold is a planning marker, not a statutory limit.");
      setText("riskWatchTitle", "A narrowing\nwindow to act.");
    }
  }

  function syncLinksAndSwitcher(currentRes) {
    const sH = $("switchHirakud");
    const sK = $("switchKrs");
    if (sH && sK) {
      if (currentRes === "krs") {
        sK.classList.add("active");
        sH.classList.remove("active");
      } else {
        sH.classList.add("active");
        sK.classList.remove("active");
      }
    }

    // Preserve ?reservoir= in all navigation links
    const links = document.querySelectorAll("a.nav, a.pill, a.card-link");
    links.forEach((a) => {
      const href = a.getAttribute("href");
      if (!href || href.startsWith("http") || href.startsWith("#") || href.startsWith("?")) return;
      const path = href.split("?")[0];
      a.setAttribute("href", `${path}?reservoir=${currentRes}`);
    });
  }

  // ---------- boot ----------

  function render(d, currentRes) {
    updateDynamicCopy(currentRes);
    syncLinksAndSwitcher(currentRes);
    renderStorage(d);
    renderOverviewCards(d);
    renderTrajectory(d.trajectory);
    renderRisk(d);
    renderDecision(d);
    renderEvidenceLog(d.evidence.items);
  }

  function showError(message) {
    const toast = document.createElement("div");
    toast.className = "toast";
    toast.textContent = `Could not load dashboard data. ${message}`;
    document.body.appendChild(toast);
  }

  async function load() {
    const stage = $("stage");
    const params = new URLSearchParams(window.location.search);
    const currentRes = params.get("reservoir") || "hirakud";

    try {
      const res = await fetch(`${API_BASE}/api/dashboard?reservoir=${currentRes}`, {
        headers: { Accept: "application/json" },
      });
      if (!res.ok) throw new Error(`API responded ${res.status}.`);
      const data = await res.json();
      render(data, currentRes);
    } catch (err) {
      console.error(err);
      showError(err.message || "Unknown error.");
    } finally {
      if (stage) stage.classList.add("is-ready");
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", load);
  } else {
    load();
  }
})();
