/*
 * WaterZero page engine.
 *
 * Each secondary screen is described as a list of positioned elements
 * (rectangles, text, and custom chart blocks) in Figma stage coordinates.
 * The page definition (static/pages/<slug>.js) builds that list from the
 * JSON returned by its API endpoint, so every value on screen is data-driven.
 */
(function () {
  "use strict";

  const API_BASE = (window.WATERZERO_API_BASE || "").replace(/\/$/, "");
  const SVG_NS = "http://www.w3.org/2000/svg";
  const FONT = "Inter, system-ui, sans-serif";

  // ---------- element factories (used by page definitions) ----------

  // Rectangle. o: { bg, rad, bd (border color), bdw (border width) }
  const R = (x, y, w, h, o = {}) => ({ k: "r", x, y, w, h, o });

  // Text. size/wt in px/weight. o: { lh, ls, align, upper, href, w2 }
  const T = (x, y, w, size, wt, color, text, o = {}) => ({ k: "t", x, y, w, size, wt, color, text, o });

  // Custom block: fn(stage, helpers) draws directly into the stage.
  const C = (fn) => ({ k: "c", fn });

  // ---------- DOM helpers ----------

  function place(parent, x, y, w, h, css) {
    const d = document.createElement("div");
    d.style.position = "absolute";
    d.style.left = `${x}px`;
    d.style.top = `${y}px`;
    if (w != null) d.style.width = `${w}px`;
    if (h != null) d.style.height = `${h}px`;
    Object.assign(d.style, css || {});
    parent.appendChild(d);
    return d;
  }

  function renderRect(stage, e) {
    const o = e.o;
    const css = {};
    if (o.bg) css.background = o.bg;
    if (o.rad != null) css.borderRadius = `${o.rad}px`;
    if (o.bd) css.border = `${o.bdw || 1}px solid ${o.bd}`;
    place(stage, e.x, e.y, e.w, e.h, css);
  }

  function renderText(stage, e) {
    const o = e.o;
    const css = {
      font: `${e.wt} ${e.size}px/${o.lh || "normal"} ${FONT}`,
      color: e.color,
      whiteSpace: "pre-wrap",
      wordBreak: "break-word",
    };
    if (o.ls != null) css.letterSpacing = `${o.ls}px`;
    if (o.align) css.textAlign = o.align;
    if (o.upper) css.textTransform = "uppercase";
    if (o.href) css.textDecoration = "none";

    const node = place(
      stage,
      e.x,
      e.y,
      e.w,
      null,
      css
    );
    node.textContent = e.text == null ? "" : String(e.text);

    if (o.href) {
      const a = document.createElement("a");
      const params = new URLSearchParams(window.location.search);
      const res = params.get("reservoir");
      let href = o.href;
      if (res && !href.includes("?")) {
        href += `?reservoir=${res}`;
      }
      a.href = href;
      a.style.color = "inherit";
      a.style.textDecoration = "none";
      a.style.position = "absolute";
      a.style.left = `${e.x}px`;
      a.style.top = `${e.y}px`;
      a.style.width = `${e.w}px`;
      a.style.font = css.font;
      a.style.color = e.color;
      a.style.whiteSpace = "pre-wrap";
      a.style.cursor = "pointer";
      a.style.zIndex = "40";
      a.textContent = node.textContent;
      node.replaceWith(a);
    }
  }

  // ---------- SVG helpers (stage coordinates via viewBox) ----------

  function svgLayer(stage, x, y, w, h) {
    const s = document.createElementNS(SVG_NS, "svg");
    s.setAttribute("viewBox", `${x} ${y} ${w} ${h}`);
    s.setAttribute("width", w);
    s.setAttribute("height", h);
    s.style.position = "absolute";
    s.style.left = `${x}px`;
    s.style.top = `${y}px`;
    s.style.overflow = "hidden";
    stage.appendChild(s);
    return s;
  }

  function svgEl(name, attrs, parent) {
    const n = document.createElementNS(SVG_NS, name);
    for (const k in attrs) n.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(n);
    return n;
  }

  function svgText(parent, str, x, y, size, fill, weight = 400, anchor = "start") {
    const t = svgEl(
      "text",
      {
        x,
        y,
        "font-family": FONT,
        "font-size": size,
        "font-weight": weight,
        fill,
        "text-anchor": anchor,
        style: "white-space:pre",
      },
      parent
    );
    t.textContent = str;
    return t;
  }

  // Stepped path: horizontal run then vertical connector.
  function steppedPath(points) {
    if (!points.length) return "";
    let d = `M${points[0][0]},${points[0][1]}`;
    for (let i = 1; i < points.length; i++) {
      const [x, y] = points[i];
      d += ` H${x} V${y}`;
    }
    return d;
  }

  // Donut: track circle plus a value arc. Returns nothing; draws into svg.
  function donut(stage, x, y, size, ratio, color, track, stroke = 9) {
    const s = svgLayer(stage, x, y, size, size);
    const r = (size - stroke) / 2;
    const c = size / 2;
    const circ = 2 * Math.PI * r;
    svgEl("circle", { cx: c, cy: c, r, fill: "none", stroke: track, "stroke-width": stroke }, s);
    if (ratio != null && ratio > 0) {
      svgEl(
        "circle",
        {
          cx: c,
          cy: c,
          r,
          fill: "none",
          stroke: color,
          "stroke-width": stroke,
          "stroke-dasharray": `${Math.min(ratio, 1) * circ} ${circ}`,
          transform: `rotate(-90 ${c} ${c})`,
          "stroke-linecap": "butt",
        },
        s
      );
    }
    return s;
  }

  // Linear y-scale from values to pixel range. Includes extra values in the domain.
  function yScale(values, top, bottom, extra = []) {
    const all = [...values, ...extra].filter((v) => v != null);
    const min = Math.min(...all);
    const max = Math.max(...all);
    const span = max - min || 1;
    return (v) => top + ((max - v) / span) * (bottom - top);
  }

  // ---------- rendering ----------

  function renderElements(stage, elements) {
    const helpers = { svgLayer, svgEl, svgText, steppedPath, donut, yScale, place };
    for (const e of elements) {
      if (e.k === "r") renderRect(stage, e);
      else if (e.k === "t") renderText(stage, e);
      else if (e.k === "c") e.fn(stage, helpers);
    }
  }

  function showError(message) {
    const toast = document.createElement("div");
    toast.className = "toast";
    toast.textContent = `Could not load page data. ${message}`;
    document.body.appendChild(toast);
  }

  function loadScript(src) {
    return new Promise((resolve, reject) => {
      const s = document.createElement("script");
      s.src = src;
      s.onload = resolve;
      s.onerror = () => reject(new Error(`Failed to load ${src}`));
      document.head.appendChild(s);
    });
  }

  async function boot() {
    const slug = document.body.dataset.page;
    const stage = document.getElementById("stage");

    try {
      await loadScript(`static/pages/${slug}.js`);
      const def = window.WZ_PAGES[slug];
      if (!def) throw new Error(`No page definition for "${slug}".`);

      stage.style.width = `${def.w}px`;
      stage.style.height = `${def.h}px`;
      if (def.bg) stage.style.background = def.bg;
      document.title = def.title || document.title;

      const qs = window.location.search || "";
      const res = await fetch(`${API_BASE}${def.api}${qs}`, { headers: { Accept: "application/json" } });
      if (!res.ok) throw new Error(`API responded ${res.status}.`);
      const data = await res.json();

      renderElements(stage, def.build(data));
    } catch (err) {
      console.error(err);
      showError(err.message || "Unknown error.");
    } finally {
      stage.classList.add("is-ready");
    }
  }

  // Shared top bar: stripe, dark nav band, wordmark, three primary links.
  // active: "dashboard" | "methodology" | "about" | null
  // pal (optional): { stripe, nav, marker } to match a page's own palette.
  function topNav(active, pal = {}) {
    const markers = {
      dashboard: { x: 178, w: 88 },
      methodology: { x: 378, w: 108 },
      about: { x: 611, w: 88 },
    };
    const m = markers[active] || markers.dashboard;
    const params = new URLSearchParams(window.location.search);
    const curRes = params.get("reservoir") || "hirakud";
    const resQs = curRes ? `?reservoir=${curRes}` : "";

    const link = (key, label, x, w) => {
      const target = { dashboard: "/", methodology: "/methodology", about: "/about-team" }[key];
      return T(x, 23, w, 17.88, active === key && !pal.plain ? 600 : 400, "#fcfbf2", label, { href: target + resQs });
    };

    const isHirakud = curRes === "hirakud";
    return [
      R(0, 0, 1440, 6, { bg: pal.stripe || "#c7f052" }),
      R(0, 6, 1440, 82, { bg: pal.nav || "#0e2924" }),
      R(m.x, 62.88, m.w, 3, { bg: pal.marker || "#c4f52e" }),
      T(24, 23, 170, 20, 700, "#fcfbf2", "WATERZERO"),
      T(24, 51, 180, 9, 500, "#c7f052", "RESERVOIR FIELD ATLAS  /  06"),
      link("dashboard", "1. Dashboard", 198.63, 125),
      link("methodology", "2. Methodology", 398, 145),
      link("about", "3. About Team", 611.13, 145),

      // Reservoir Switcher in Top Navigation
      T(1050, 27, 80, 9, 700, "#c7f052", "RESERVOIR:"),
      R(1140, 22, 135, 26, { bg: isHirakud ? "#c7f052" : "rgba(255,255,255,0.12)", rad: 13, bd: "rgba(199,240,82,0.4)" }),
      T(1148, 28, 120, 8.5, 700, isHirakud ? "#0e2924" : "#fcfbf2", "HIRAKUD (ML ACTIVE)", { href: "?reservoir=hirakud" }),
      R(1285, 22, 120, 26, { bg: !isHirakud ? "#c7f052" : "rgba(255,255,255,0.12)", rad: 13, bd: "rgba(199,240,82,0.4)" }),
      T(1295, 28, 105, 8.5, 700, !isHirakud ? "#0e2924" : "#fcfbf2", "KRS (FIGMA DEMO)", { href: "?reservoir=krs" }),
    ];
  }

  window.WZ = { R, T, C, topNav, fmt: (v, d = 1) => Number(v).toFixed(d) };
  window.WZ_PAGES = window.WZ_PAGES || {};

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
