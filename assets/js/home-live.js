/* Elite — home page: the "featured" and "recommended" rows are redrawn from data/properties.js,
   so marking a unit as featured in /admin changes the home page on the next load. */
(function () {
  "use strict";
  var C = window.EliteCards, all = window.ELITE_PROPERTIES;
  if (!C || !all) return;
  var lang = document.documentElement.lang === "ar" ? "ar" : "en";
  var base = document.documentElement.dataset.base || "";
  function fill(kind, list) {
    var box = document.querySelector('[data-live="' + kind + '"]');
    if (!box || !list.length) return;
    box.innerHTML = list.sort(C.byDefault).slice(0, 3).map(function (p) {
      return C.card(p, { lang: lang, base: base, source: kind === "recommended" });
    }).join("");
    box.querySelectorAll(".scroll-fade").forEach(function (el) { el.classList.add("is-in"); });
  }
  fill("featured", all.filter(function (p) { return p.featured; }));
  fill("recommended", all.filter(function (p) { return p.recommended; }));
  if (window.EliteImgFix) window.EliteImgFix.sweep();
})();
