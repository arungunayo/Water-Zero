(function () {
  "use strict";
  const { R, T, C, topNav } = window.WZ;

  const P = {
    bg: "#f5f2e3",
    stripe: "#c4db59",
    nav: "#122e26",
    marker: "#c4f52e",
    card: "#fffff5",
    backdrop: "#e8ebd4",
    badgeText: "#c4db59",
    ink: "#122e26",
    muted: "#596b5e",
  };

  // Portrait image with a soft backdrop fallback if the photo is missing.
  function portrait(src, x, y, w, h, alt) {
    return C((stage, helpers) => {
      const box = helpers.place(stage, x, y, w, h, { overflow: "hidden", borderRadius: "12px", background: P.backdrop });
      if (!src) return;
      const img = document.createElement("img");
      img.src = src;
      img.alt = alt;
      img.style.width = "100%";
      img.style.height = "100%";
      img.style.objectFit = "cover";
      img.style.display = "block";
      img.onerror = () => img.remove();
      box.appendChild(img);
    });
  }

  window.WZ_PAGES = window.WZ_PAGES || {};
  window.WZ_PAGES["about-team"] = {
    w: 1440,
    h: 821,
    bg: P.bg,
    title: "WaterZero — About Team",
    api: "/api/about-team",

    build(d) {
      const els = [];
      els.push(...topNav("about", { stripe: P.stripe, nav: P.nav, marker: P.marker, plain: true }));

      els.push(T(32, 118, 650, 10, 500, P.muted, d.breadcrumb));

      // Team leader card
      els.push(R(47, 201, 500, 520, { bg: P.card, rad: 16 }));
      els.push(R(71, 225, 452, 290, { bg: P.backdrop, rad: 12 }));
      els.push(portrait(d.leader.photo, 75, 225, 448, 283, d.leader.role));
      els.push(R(71, 532, 292, 61, { bg: P.nav, rad: 30.5 }));
      els.push(T(99, 547, 330, 23, 700, P.badgeText, d.leader.role));
      els.push(T(89, 617, 440, 24, 700, P.ink, d.leader.name));

      // Team member card
      els.push(R(647, 201, 500, 520, { bg: P.card, rad: 16 }));
      els.push(portrait(d.member.photo, 671, 229, 444, 286, d.member.role));
      els.push(R(675, 532, 285, 61, { bg: P.nav, rad: 30.5 }));
      els.push(T(703, 547, 330, 23, 700, P.badgeText, d.member.role));
      els.push(T(682, 614, 440, 29, 700, P.ink, d.member.name));

      return els;
    },
  };
})();
