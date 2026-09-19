/* Elite — image safety net.
   If any picture fails to load (a dead external link, a deleted upload…) it is swapped for a
   fallback instead of showing an empty box: first the image's own data-fallback (e.g. the compound
   cover), then the branded fallback picture. Never loops. */
(function () {
  "use strict";
  var me = document.currentScript;
  var base = me && me.src ? me.src.replace(/assets\/js\/imgfix\.js.*$/, "") : "";
  var FALLBACK = base + "assets/img/brand/fallback.jpg";

  function swap(img) {
    if (!img || img.tagName !== "IMG") return;
    var step = Number(img.getAttribute("data-fb") || 0);
    if (step >= 2) { img.style.visibility = "hidden"; return; }
    var next = step === 0 && img.getAttribute("data-fallback") ? img.getAttribute("data-fallback") : FALLBACK;
    img.setAttribute("data-fb", next === FALLBACK ? "2" : "1");
    img.removeAttribute("srcset");
    img.src = next;
  }

  document.addEventListener("error", function (e) { swap(e.target); }, true);

  function sweep() {
    var list = document.images;
    for (var i = 0; i < list.length; i++) {
      var im = list[i];
      if (im.complete && im.naturalWidth === 0 && im.getAttribute("src") && !/\.svg(\?|$)/i.test(im.getAttribute("src"))) swap(im);
    }
  }
  document.addEventListener("DOMContentLoaded", sweep);
  window.addEventListener("load", sweep);
  window.EliteImgFix = { sweep: sweep };
})();
