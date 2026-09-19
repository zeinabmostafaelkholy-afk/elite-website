/* Elite — North Coast map page.
   The page is drawn at build time; when data/properties.js is available every compound's price,
   unit count and photo are refreshed from it, so admin edits show up on the next page load. */
(function () {
  "use strict";
  var D = window.SAHEL_MAP || [], L = window.SAHEL_L || {};
  var C = window.EliteCards;
  var dlg = document.querySelector(".smap-dialog");
  var base = L.base || "";

  function esc(s) { return C ? C.esc(s) : String(s == null ? "" : s); }
  function fmt(n) { return C ? C.money(n) : String(n); }
  function usable(u) { return !C.isAsk(u) || Number(u.area) > 0 || Number(u.beds) > 0; }

  function refresh() {
    var props = window.ELITE_PROPERTIES, comps = window.ELITE_COMPOUNDS;
    if (!C || !props || !comps) return;
    var by = {};
    props.forEach(function (p) { if (p.compound) (by[p.compound] = by[p.compound] || []).push(p); });
    var rows = document.querySelectorAll(".smap-row[data-slug]");
    rows.forEach(function (row) {
      var slug = row.dataset.slug, it = D[+row.querySelector(".smap-row__name").dataset.i];
      var comp = comps[slug]; if (!it || !comp) return;
      var units = (by[slug] || []).slice().sort(C.byCompound);
      var priced = units.filter(function (u) { return !C.isAsk(u); }).map(function (u) { return Number(u.price); });
      var listed = units.filter(usable).length;
      var photo = "";
      for (var i = 0; i < units.length && !photo; i++) {
        var imgs = [units[i].image].concat(units[i].gallery || []);
        for (var j = 0; j < imgs.length; j++) {
          if (imgs[j] && imgs[j].indexOf("assets/img/compounds/") === -1) { photo = imgs[j]; break; }
        }
      }
      photo = photo || comp.galleryPhoto || comp.cover || "";
      it.photo = photo ? C.imgSrc(base, photo) : "";
      var min = priced.length ? Math.min.apply(null, priced) : 0;
      it.price = min ? L.egp + " " + fmt(min) : "";
      it.units = listed ? listed + " " + (listed > 1 || L.ar ? L.units : L.unit1) : "";

      var sub = row.querySelector(".smap-row__price");
      if (sub) {
        sub.className = "smap-row__price" + (min ? "" : " is-ask");
        sub.textContent = min ? L.from + " " + it.price : L.ask;
      }
      var badge = row.querySelector(".smap-row__badge");
      if (badge && it.photo) {
        badge.innerHTML = '<img src="' + esc(it.photo) + '" alt="" loading="lazy" width="80" height="80" referrerpolicy="no-referrer" data-fallback="' + esc(C.imgSrc(base, comp.cover)) + '">';
      }
    });
    if (window.EliteImgFix) window.EliteImgFix.sweep();
  }

  function q(s) { return dlg.querySelector(s); }
  function open(i) {
    var c = D[i];
    q(".smap-dialog__media").innerHTML = c.photo
      ? '<img src="' + esc(c.photo) + '" alt="" referrerpolicy="no-referrer" data-fallback="' + esc(c.cover || "") + '">'
      : "<span>" + esc(c.alt.split(/\s+/).slice(0, 2).map(function (w) { return w.charAt(0); }).join("")) + "</span>";
    q(".smap-dialog__meta").textContent = L.km + " " + c.km + " · " + c.region;
    q(".smap-dialog__name").textContent = c.name;
    q(".smap-dialog__alt").textContent = c.alt;
    q(".smap-dialog__price").innerHTML = c.price ? "<small>" + esc(L.from) + "</small> " + esc(c.price) : esc(L.ask);
    q(".smap-dialog__units").textContent = c.units; q(".smap-dialog__units").hidden = !c.units;
    q(".smap-dialog__wa").href = c.wa;
    var l = q(".smap-dialog__link");
    if (c.link) { l.href = c.link; l.innerHTML = esc(c.linkLabel) + L.arrow; l.hidden = false; } else { l.hidden = true; }
    if (dlg.showModal) dlg.showModal(); else window.open(c.wa, "_blank");
    if (window.EliteImgFix) window.EliteImgFix.sweep();
  }

  refresh();
  if (dlg) {
    document.querySelectorAll(".smap-row__name").forEach(function (btn) {
      btn.addEventListener("click", function () { open(+btn.dataset.i); });
    });
    q(".smap-dialog__close").addEventListener("click", function () { dlg.close(); });
    dlg.addEventListener("click", function (e) { if (e.target === dlg) dlg.close(); });
  }
  var p = document.querySelector("[data-print]");
  if (p) p.addEventListener("click", function () { window.print(); });
})();
