/* Elite — Sahel compound pages.
   The page ships with the units already drawn (good for search engines). When data/properties.js
   is available the units are redrawn from it, so anything saved in the admin dashboard shows up
   here on the next page load — no rebuild. Also: tabs, filters, sort, favourites and the unit sheet. */
(function () {
  "use strict";
  var C = window.EliteCards, CTX = window.NX_CTX || {}, L = window.NX_L || {};
  var grid = document.querySelector(".nx-grid");
  if (!grid) return;
  var U = window.NX_UNITS || [];
  var countEl = document.querySelector("[data-count]");
  var emptyEl = document.querySelector(".nx-empty");
  var state = { tab: "", type: "", beds: "", sort: "" };
  var esc = C ? C.esc : function (s) { return String(s == null ? "" : s); };
  function fmt(n) { return C ? C.money(n) : String(n); }

  /* ---------- live data ---------- */
  function money(n) { return '<b>' + fmt(n) + '</b> <small>' + esc(L.egp) + '</small>'; }
  function goLive() {
    var comps = window.ELITE_COMPOUNDS, props = window.ELITE_PROPERTIES;
    if (!C || !comps || !props || !CTX.slug || !comps[CTX.slug]) return;
    var comp = comps[CTX.slug];
    var list = props.filter(function (p) { return p.compound === CTX.slug; }).sort(C.byCompound);
    var cx = { lang: CTX.lang, base: CTX.base, comp: comp };
    U = list.map(function (p) { return C.sahelUnit(p, cx); });
    window.NX_UNITS = U;
    grid.innerHTML = U.map(function (u, i) {
      return C.nxCard(u, { lang: CTX.lang, base: CTX.base, i: i, fallback: comp.cover, devInitials: CTX.devInitials });
    }).join("");

    var dev = [], re = [];
    U.forEach(function (u) { if (!u.ask && u.p) { if (u.sale === "developer") dev.push(u.p); else if (u.sale === "resale") re.push(u.p); } });
    var dv = document.querySelector("[data-dev-start]"), rv = document.querySelector("[data-re-start]");
    if (dv) dv.innerHTML = dev.length ? money(Math.min.apply(null, dev)) : "<b>-</b>";
    if (rv) rv.innerHTML = re.length ? money(Math.min.apply(null, re)) : "<b>-</b>";

    var nDev = U.filter(function (u) { return u.sale === "developer"; }).length;
    var nRe = U.filter(function (u) { return u.sale === "resale"; }).length;
    var tabs = document.querySelectorAll("[data-tab]");
    var counts = { "": U.length, developer: nDev, resale: nRe };
    tabs.forEach(function (b) {
      var s = b.querySelector("small"); if (s) s.textContent = "(" + counts[b.dataset.tab] + ")";
    });
    var ts = document.querySelector("[data-f-type]");
    if (ts) {
      var keep = ts.value, seen = {}, opts = '<option value="">' + esc(ts.options[0] ? ts.options[0].textContent : "") + "</option>";
      U.forEach(function (u) { if (!seen[u.type]) { seen[u.type] = 1; opts += '<option value="' + esc(u.type) + '">' + esc(u.ty) + "</option>"; } });
      ts.innerHTML = opts; ts.value = keep; if (ts.value !== keep) { state.type = ""; }
    }
    document.querySelectorAll(".nx-empty-cta").forEach(function (e) { e.hidden = U.length > 0; });
    if (emptyEl) { emptyEl.hidden = U.length > 0; emptyEl.textContent = (U.length ? CTX.noMatchText : CTX.emptyText) || emptyEl.textContent; }
    var ld = document.querySelector("[data-nx-jsonld]"); if (ld) ld.remove();
  }

  /* ---------- filters / tabs / sort ---------- */
  function cards() { return Array.prototype.slice.call(grid.querySelectorAll(".nx-card")); }
  function apply() {
    var cs = cards(), shown = 0;
    cs.forEach(function (c) {
      var ok = (!state.tab || c.dataset.sale === state.tab) &&
        (!state.type || c.dataset.type === state.type) &&
        (!state.beds || (state.beds === "5" ? +c.dataset.beds >= 5 : c.dataset.beds === state.beds));
      c.hidden = !ok; if (ok) shown++;
    });
    var sorted = cs.slice();
    function ask(c) { return c.dataset.ask === "1"; }
    if (state.sort === "low") sorted.sort(function (a, b) { return (ask(a) ? 1e15 : +a.dataset.price) - (ask(b) ? 1e15 : +b.dataset.price); });
    else if (state.sort === "high") sorted.sort(function (a, b) { return (ask(b) ? -1 : +b.dataset.price) - (ask(a) ? -1 : +a.dataset.price); });
    else if (state.sort === "area") sorted.sort(function (a, b) { return b.dataset.area - a.dataset.area; });
    else sorted.sort(function (a, b) { return a.dataset.i - b.dataset.i; });
    sorted.forEach(function (c) { grid.appendChild(c); });
    if (countEl) countEl.textContent = shown;
    if (emptyEl && cs.length) { emptyEl.hidden = shown > 0; if (shown === 0) emptyEl.textContent = CTX.noMatchText || emptyEl.textContent; }
  }

  document.querySelectorAll("[data-tab]").forEach(function (b) {
    b.addEventListener("click", function () {
      document.querySelectorAll("[data-tab]").forEach(function (x) { x.setAttribute("aria-selected", x === b ? "true" : "false"); });
      state.tab = b.dataset.tab; apply();
    });
  });
  var ft = document.querySelector("[data-filter-toggle]"), fp = document.querySelector(".nx-filters");
  if (ft && fp) ft.addEventListener("click", function () { fp.hidden = !fp.hidden; ft.setAttribute("aria-expanded", String(!fp.hidden)); });
  var st = document.querySelector("[data-f-type]"), sb = document.querySelector("[data-f-beds]"), ss = document.querySelector("[data-sort]");
  if (st) st.addEventListener("change", function () { state.type = st.value; apply(); });
  if (sb) sb.addEventListener("change", function () { state.beds = sb.value; apply(); });
  if (ss) ss.addEventListener("change", function () { state.sort = ss.value; apply(); });
  var rs = document.querySelector("[data-f-reset]");
  if (rs) rs.addEventListener("click", function () { state.type = state.beds = ""; if (st) st.value = ""; if (sb) sb.value = ""; apply(); });

  /* ---------- favourites (kept in this browser only) ---------- */
  var FKEY = "elite-sahel-favs", favs = [];
  try { favs = JSON.parse(localStorage.getItem(FKEY) || "[]"); } catch (e) { favs = []; }
  function paintFavs() {
    grid.querySelectorAll("[data-fav]").forEach(function (b) { b.setAttribute("aria-pressed", favs.indexOf(b.dataset.fav) > -1 ? "true" : "false"); });
  }

  /* ---------- unit sheet ---------- */
  var dlg = document.querySelector(".nx-unit");
  function q(s) { return dlg.querySelector(s); }
  var cur = null, idx = 0;
  function show(k) {
    if (!cur || !cur.img.length) { q(".nx-unit__gal").hidden = true; return; }
    q(".nx-unit__gal").hidden = false;
    idx = (k + cur.img.length) % cur.img.length;
    var im = q(".nx-unit__img");
    im.removeAttribute("data-fb");
    im.src = cur.img[idx]; im.alt = cur.t;
    q(".nx-unit__counter").textContent = (idx + 1) + " / " + cur.img.length;
    var multi = cur.img.length > 1;
    q(".nx-unit__nav--prev").hidden = q(".nx-unit__nav--next").hidden = !multi;
    q(".nx-unit__thumbs").querySelectorAll("button").forEach(function (b, j) { b.setAttribute("aria-current", j === idx ? "true" : "false"); });
  }
  function open(i) {
    cur = U[i]; if (!cur || !dlg) return;
    q(".nx-unit__thumbs").innerHTML = cur.img.length > 1 ? cur.img.map(function (s, j) {
      return '<button type="button" data-j="' + j + '"><img src="' + esc(s) + '" alt="" loading="lazy" referrerpolicy="no-referrer"></button>';
    }).join("") : "";
    q(".nx-unit__thumbs").querySelectorAll("button").forEach(function (b) { b.addEventListener("click", function () { show(+b.dataset.j); }); });
    show(0);
    q(".nx-unit__title").textContent = cur.t;
    q(".nx-unit__loc").textContent = cur.loc;
    q(".nx-unit__price").innerHTML = cur.ask
      ? '<b class="is-ask">' + esc(L.ask) + "</b>"
      : cur.mx
        ? esc(L.from) + "<b>" + fmt(cur.p) + " " + esc(L.egp) + "</b>" + esc(L.max) + ": " + fmt(cur.mx) + " " + esc(L.egp)
        : esc(L.price) + "<b>" + fmt(cur.p) + " " + esc(L.egp) + "</b>";
    q(".nx-unit__wa").href = cur.wa;
    var facts = [[cur.ty, cur.a ? cur.a + " m²" : "-"], [L.ref, cur.ref], [L.beds, cur.bd || "-"], [L.baths, cur.bt || "-"],
      [L.dl, cur.dl || "-"], [L.cmp, cur.cmp], [L.sale, cur.sale === "developer" ? L.dev : cur.sale === "resale" ? L.resale : "-"], [L.fin, cur.fin || "-"]];
    q(".nx-unit__facts").innerHTML = facts.map(function (f) { return "<div><dt>" + esc(f[0]) + '</dt><dd dir="auto">' + esc(f[1]) + "</dd></div>"; }).join("");
    q(".nx-unit__am").innerHTML = cur.am.length ? "<h3>" + esc(L.am) + "</h3><ul>" + cur.am.map(function (a) { return "<li>" + esc(a) + "</li>"; }).join("") + "</ul>" : "";
    var plans = cur.plans.map(function (p, j) {
      return '<div class="nx-plan-card"><p>' + esc(L.plan) + " " + (j + 1) + "</p><b>" + fmt(p.i) + " " + esc(L.egp) + "</b> <span>" + esc(p.f) + "</span>" +
        (p.y ? "<p>" + esc(p.y) + " " + esc(L.years) + "</p>" : "") + (p.d ? "<p>" + fmt(p.d) + " " + esc(L.egp) + " " + esc(L.down) + "</p>" : "") + "</div>";
    }).join("");
    if (!plans && cur.cash) plans = '<div class="nx-plan-card"><b>' + esc(L.cash) + "</b></div>";
    q(".nx-unit__plans").innerHTML = plans ? "<h3>" + esc(L.plans) + "</h3><div>" + plans + "</div>" : "";
    q(".nx-unit__about").innerHTML = cur.desc ? "<h3>" + esc(L.about) + "</h3><p>" + esc(cur.desc) + "</p>" : "";
    if (dlg.showModal) { dlg.showModal(); dlg.scrollTop = 0; } else window.open(cur.wa, "_blank");
    if (history.replaceState) history.replaceState(null, "", "#u-" + encodeURIComponent(cur.ref));
  }
  if (dlg) {
    q(".nx-unit__close").addEventListener("click", function () { dlg.close(); });
    dlg.addEventListener("click", function (e) { if (e.target === dlg) dlg.close(); });
    dlg.addEventListener("close", function () { if (history.replaceState) history.replaceState(null, "", location.pathname + location.search); });
    var rtl = document.documentElement.dir === "rtl";
    q(".nx-unit__nav--prev").addEventListener("click", function () { show(idx + (rtl ? 1 : -1)); });
    q(".nx-unit__nav--next").addEventListener("click", function () { show(idx + (rtl ? -1 : 1)); });
    dlg.addEventListener("keydown", function (e) {
      if (e.key === "ArrowLeft") show(idx - 1);
      if (e.key === "ArrowRight") show(idx + 1);
    });
  }

  /* one listener for every card, so redrawing the list never loses the buttons */
  grid.addEventListener("click", function (e) {
    var o = e.target.closest("[data-open]");
    if (o) { open(+o.dataset.open); return; }
    var s = e.target.closest("[data-share]");
    if (s) {
      var u = U[+s.dataset.share]; if (!u) return;
      var link = location.origin + location.pathname + "#u-" + encodeURIComponent(u.ref);
      if (navigator.share) { navigator.share({ title: u.t, url: link }).catch(function () {}); return; }
      if (navigator.clipboard) navigator.clipboard.writeText(link).then(function () { s.title = L.copied; });
      return;
    }
    var f = e.target.closest("[data-fav]");
    if (f) {
      var i = favs.indexOf(f.dataset.fav);
      if (i > -1) favs.splice(i, 1); else favs.push(f.dataset.fav);
      f.setAttribute("aria-pressed", i > -1 ? "false" : "true");
      try { localStorage.setItem(FKEY, JSON.stringify(favs)); } catch (er) {}
    }
  });

  goLive();
  paintFavs();
  apply();
  var m = location.hash.match(/^#u-(.+)$/);
  if (m) { var ref = decodeURIComponent(m[1]); for (var i = 0; i < U.length; i++) if (U[i].ref === ref) { open(i); break; } }
  if (window.EliteImgFix) window.EliteImgFix.sweep();
})();
