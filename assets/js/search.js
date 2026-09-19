/* ==========================================================================
   Elite Real Estate — properties search
   Reads window.ELITE_PROPERTIES (data/properties.js) and renders filtered cards.
   ========================================================================== */
(function () {
  "use strict";

  var root = document.getElementById("listing");
  if (!root) return;

  var html = document.documentElement;
  var lang = html.lang === "ar" ? "ar" : "en";
  var base = html.dataset.base || "";
  var T = JSON.parse(document.getElementById("i18n-data").textContent);
  var PAGE_SIZE = 9;

  var icons = {
    pin: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 21s7-5.6 7-11a7 7 0 1 0-14 0c0 5.4 7 11 7 11z"/><circle cx="12" cy="10" r="2.5"/></svg>',
    area: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 9V4h5M20 15v5h-5M20 9V4h-5M4 15v5h5"/></svg>',
    bed: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M3 18v-6h18v6M3 12V7m18 5V9a2 2 0 0 0-2-2h-5v5"/><circle cx="7.5" cy="9.5" r="1.8"/></svg>',
    bath: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 12h16v3a4 4 0 0 1-4 4H8a4 4 0 0 1-4-4v-3zM7 12V6a2 2 0 0 1 4 0"/></svg>',
    arrow: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M5 12h14m-6-6 6 6-6 6"/></svg>'
  };

  function t(key) { return T[key] || key; }

  function money(n) {
    return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  }

  var C = window.EliteCards;
  function cardHTML(p) { return C.card(p, { lang: lang, base: base }); }

  /* ---------- state ---------- */
  var all = (window.ELITE_PROPERTIES || []).slice();
  var COMPS = window.ELITE_COMPOUNDS || {};
  var shown = PAGE_SIZE;

  var els = {
    grid: document.getElementById("results-grid"),
    count: document.getElementById("results-count"),
    more: document.getElementById("load-more"),
    form: document.getElementById("filters-form"),
    sort: document.getElementById("sort"),
    keyword: document.getElementById("f-keyword")
  };

  function readState() {
    var f = els.form;
    return {
      purpose: f.querySelector(".chip.is-active[data-purpose]") ? f.querySelector(".chip.is-active[data-purpose]").dataset.purpose : "",
      beds: f.querySelector(".chip.is-active[data-beds]") ? f.querySelector(".chip.is-active[data-beds]").dataset.beds : "",
      type: f.elements.type.value,
      location: f.elements.location.value,
      project: f.elements.project ? f.elements.project.value : "",
      minPrice: f.elements.minPrice.value,
      maxPrice: f.elements.maxPrice.value,
      minArea: f.elements.minArea.value,
      maxArea: f.elements.maxArea.value,
      keyword: els.keyword ? els.keyword.value.trim().toLowerCase() : "",
      sort: els.sort.value
    };
  }

  function filter(s) {
    var out = all.filter(function (p) {
      if (s.purpose && p.purpose !== s.purpose) return false;
      if (s.type && p.type !== s.type) return false;
      if (s.location && p.city !== s.location) return false;
      if (s.project && p.project !== s.project) return false;
      if (s.beds) {
        var n = parseInt(s.beds, 10);
        if (s.beds === "4+" ? p.beds < 4 : p.beds !== n) return false;
      }
      if ((s.minPrice || s.maxPrice) && C.isAsk(p)) return false; /* "price on request" units have no price to compare */
      if (s.minPrice && p.price < Number(s.minPrice)) return false;
      if (s.maxPrice && p.price > Number(s.maxPrice)) return false;
      if (s.minArea && p.area < Number(s.minArea)) return false;
      if (s.maxArea && p.area > Number(s.maxArea)) return false;
      if (s.keyword) {
        var cp = COMPS[p.compound] || {};
        var hay = [p.title.ar, p.title.en, p.location.ar, p.location.en, p.id, p.project || "", p.compound || "",
          cp.name ? cp.name.ar + " " + cp.name.en : ""].join(" ").toLowerCase();
        if (hay.indexOf(s.keyword) === -1) return false;
      }
      return true;
    });

    /* "price on request" units always go to the end of the price sorts */
    if (s.sort === "priceAsc") out.sort(function (a, b) { return (C.isAsk(a) ? 1e15 : a.price) - (C.isAsk(b) ? 1e15 : b.price); });
    else if (s.sort === "priceDesc") out.sort(function (a, b) { return (C.isAsk(b) ? -1 : b.price) - (C.isAsk(a) ? -1 : a.price); });
    else if (s.sort === "areaDesc") out.sort(function (a, b) { return (b.area || 0) - (a.area || 0); });
    else out.sort(C.byDefault); /* featured first, then the admin's order, then newest */

    return out;
  }

  function syncURL(s) {
    var params = new URLSearchParams();
    Object.keys(s).forEach(function (k) {
      if (s[k] && !(k === "sort" && s[k] === "newest")) params.set(k, s[k]);
    });
    var q = params.toString();
    history.replaceState(null, "", q ? "?" + q : location.pathname);
  }

  function render(reset) {
    var s = readState();
    if (reset) shown = PAGE_SIZE;
    var results = filter(s);

    els.count.innerHTML = "<b>" + results.length + "</b> " + t("results.count");

    if (!results.length) {
      els.grid.innerHTML = '<div class="empty"><p>' + t("results.none") + "</p>" +
        '<button class="btn btn--brass" data-wa>' + t("cta.whatsapp") + "</button></div>";
      els.grid.querySelectorAll("[data-wa]").forEach(function (el) {
        el.addEventListener("click", function () { window.open(window.waLink(), "_blank", "noopener"); });
      });
    } else {
      els.grid.innerHTML = results.slice(0, shown).map(cardHTML).join("");
      if (window.EliteImgFix) window.EliteImgFix.sweep();
    }

    els.more.hidden = results.length <= shown;
    syncURL(s);
  }

  /* ---------- events ---------- */
  els.form.addEventListener("change", function () { render(true); });
  els.form.addEventListener("submit", function (e) { e.preventDefault(); render(true); });
  if (els.keyword) {
    var timer;
    els.keyword.addEventListener("input", function () {
      clearTimeout(timer);
      timer = setTimeout(function () { render(true); }, 250);
    });
  }
  els.sort.addEventListener("change", function () { render(true); });
  els.more.addEventListener("click", function () { shown += PAGE_SIZE; render(false); });

  els.form.querySelectorAll(".chip").forEach(function (chip) {
    chip.addEventListener("click", function () {
      var group = chip.dataset.purpose !== undefined ? "purpose" : "beds";
      var siblings = els.form.querySelectorAll('.chip[data-' + group + ']');
      var wasActive = chip.classList.contains("is-active");
      siblings.forEach(function (c) { c.classList.remove("is-active"); });
      if (!wasActive) chip.classList.add("is-active");
      render(true);
    });
  });

  var reset = document.getElementById("filters-reset");
  if (reset) {
    reset.addEventListener("click", function () {
      els.form.reset();
      els.form.querySelectorAll(".chip").forEach(function (c) { c.classList.remove("is-active"); });
      if (els.keyword) els.keyword.value = "";
      render(true);
    });
  }

  var fToggle = document.getElementById("filters-toggle");
  if (fToggle) {
    fToggle.addEventListener("click", function () {
      document.getElementById("filters").classList.toggle("is-open");
    });
  }

  /* ---------- hydrate from URL ---------- */
  (function hydrate() {
    var q = new URLSearchParams(location.search);
    var f = els.form;
    ["type", "location", "project", "minPrice", "maxPrice", "minArea", "maxArea"].forEach(function (k) {
      if (q.get(k) && f.elements[k]) f.elements[k].value = q.get(k);
    });
    if (q.get("keyword") && els.keyword) els.keyword.value = q.get("keyword");
    if (q.get("sort")) els.sort.value = q.get("sort");
    ["purpose", "beds"].forEach(function (k) {
      var v = q.get(k);
      if (!v) return;
      var chip = f.querySelector('.chip[data-' + k + '="' + v + '"]');
      if (chip) chip.classList.add("is-active");
    });
    /* price band coming from the hero search bar, e.g. price=5000000-10000000 */
    var band = q.get("price");
    if (band && band.indexOf("-") > -1) {
      var parts = band.split("-");
      if (parts[0]) f.elements.minPrice.value = parts[0];
      if (parts[1]) f.elements.maxPrice.value = parts[1];
    }
    var areaBand = q.get("areaBand");
    if (areaBand && areaBand.indexOf("-") > -1) {
      var ap = areaBand.split("-");
      if (ap[0]) f.elements.minArea.value = ap[0];
      if (ap[1]) f.elements.maxArea.value = ap[1];
    }
    render(true);
  })();
})();
