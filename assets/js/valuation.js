/* ==========================================================================
   Elite Real Estate — Property valuation
   Same fields and flow as the Aqarmap estimate tool:
   city → area, size, finishing, view, purpose → name, phone, email → price.
   The lead goes to api/lead.php (saved in /admin). The price is calculated
   here with exactly the same formula as api/lib/estimator.php, so the page
   still shows a result if the server is unreachable.
   ========================================================================== */
(function () {
  "use strict";

  var CFG = window.ELITE_VAL || {};
  var D = window.ELITE_VALUATION_DATA;
  var T = CFG.t || {};
  var LANG = CFG.lang === "en" ? "en" : "ar";
  var form = document.getElementById("vx-form");
  if (!D || !form) return;

  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }
  function find(list, id) { for (var i = 0; i < list.length; i++) if (list[i].id === id) return list[i]; return null; }
  function fmt(n) { return Math.round(n).toLocaleString("en-US"); }
  function tpl(s, o) { return String(s).replace(/\{(\w+)\}/g, function (_, k) { return o[k] != null ? o[k] : ""; }); }
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }

  var resultBox = $("#vx-result");
  var els = {
    region: $("#vx-region"), zone: $("#vx-zone"), zoneWrap: $("#vx-zone-wrap"),
    area: $("#vx-area"), finish: $("#vx-finish"), intent: $("#vx-intent"),
    name: $("#vx-name"), phone: $("#vx-phone"), email: $("#vx-email"),
    submit: form.querySelector(".vx-submit")
  };
  var views = [];            /* selected "view" feature ids */
  var dial = "20", iso = "eg";

  /* ---------- selects: grey placeholder look ---------- */
  function markEmpty(sel) { sel.classList.toggle("is-empty", !sel.value); }
  [els.region, els.zone, els.finish, els.intent].forEach(function (s) {
    markEmpty(s);
    s.addEventListener("change", function () { markEmpty(s); clearErr(s); });
  });

  /* ---------- city → area ---------- */
  els.region.addEventListener("change", function () {
    var r = find(D.regions, els.region.value);
    var first = els.zone.options[0].outerHTML;
    if (!r) { els.zoneWrap.hidden = true; els.zone.innerHTML = first; return; }
    var zones = r.zones.slice().sort(function (a, b) { return a[LANG].localeCompare(b[LANG], LANG); });
    els.zone.innerHTML = first + zones.map(function (z) {
      return '<option value="' + z.id + '">' + esc(z[LANG]) + "</option>";
    }).join("");
    els.zone.value = "";
    markEmpty(els.zone);
    clearErr(els.zone);
    els.zoneWrap.hidden = false;
  });

  /* ---------- dropdown helper (view multi-select + country picker) ---------- */
  var dropdownRoots = [];
  function closeAll(except) { dropdownRoots.forEach(function (r) { if (r !== except && r._close) r._close(); }); }
  document.addEventListener("click", function (e) {
    dropdownRoots.forEach(function (r) { if (!r.contains(e.target) && r._close) r._close(); });
  });

  function dropdown(root, btn, menu, onPick, multi) {
    dropdownRoots.push(root);
    function open() {
      closeAll(root);
      menu.hidden = false; btn.setAttribute("aria-expanded", "true");
      var cur = menu.querySelector('[aria-selected="true"]') || menu.querySelector("li");
      if (cur) cur.focus();
    }
    function close(focusBtn) {
      if (menu.hidden) return;
      menu.hidden = true; btn.setAttribute("aria-expanded", "false");
      if (focusBtn) btn.focus();
    }
    root._close = close;
    btn.addEventListener("click", function (e) {
      if (e.target.closest && e.target.closest("[data-remove]")) return;
      if (menu.hidden) open(); else close();
    });
    menu.addEventListener("click", function (e) {
      var li = e.target.closest("li"); if (!li) return;
      onPick(li);
      if (!multi) close(true);
    });
    menu.addEventListener("keydown", function (e) {
      var items = $$("li", menu), i = items.indexOf(document.activeElement);
      if (e.key === "ArrowDown") { e.preventDefault(); (items[i + 1] || items[0]).focus(); }
      else if (e.key === "ArrowUp") { e.preventDefault(); (items[i - 1] || items[items.length - 1]).focus(); }
      else if (e.key === "Enter" || e.key === " ") { e.preventDefault(); if (items[i]) { onPick(items[i]); if (!multi) close(true); } }
      else if (e.key === "Escape") { close(true); }
      else if (e.key === "Tab") { close(false); }
    });
    btn.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown") { e.preventDefault(); open(); }
    });
  }

  /* view (الإطلالة) */
  var viewRoot = $("#vx-view");
  var viewBtn = $(".vx-multi__btn", viewRoot);
  var viewMenu = $(".vx-menu", viewRoot);
  var viewChips = $(".vx-multi__chips", viewRoot);
  var viewPh = viewChips.innerHTML;

  function viewLabel(id) {
    var li = viewMenu.querySelector('[data-value="' + id + '"]');
    return li ? li.textContent : "";
  }
  function renderViews() {
    $$("li", viewMenu).forEach(function (li) {
      li.setAttribute("aria-selected", views.indexOf(li.getAttribute("data-value")) > -1 ? "true" : "false");
    });
    if (!views.length) { viewChips.innerHTML = viewPh; return; }
    viewChips.innerHTML = views.map(function (id) {
      return '<span class="vx-chip">' + esc(viewLabel(id)) + '<b data-remove="' + id + '" aria-hidden="true">&times;</b></span>';
    }).join("");
  }
  dropdown(viewRoot, viewBtn, viewMenu, function (li) {
    var id = li.getAttribute("data-value"), at = views.indexOf(id);
    if (at > -1) views.splice(at, 1); else views.push(id);
    renderViews();
  }, true);
  viewChips.addEventListener("click", function (e) {
    var b = e.target.closest("[data-remove]"); if (!b) return;
    e.stopPropagation();
    var id = b.getAttribute("data-remove");
    views = views.filter(function (v) { return v !== id; });
    renderViews();
  });

  /* phone country picker */
  var telRoot = $("#vx-tel");
  var telBtn = $(".vx-tel__btn", telRoot);
  var telMenu = $(".vx-menu", telRoot);
  /* if the flag image can't load, show the dial code instead */
  function flagFallback(img, code) {
    if (img.complete && img.src && !img.naturalWidth) { setTimeout(function () { img.onerror(); }, 0); }
    img.onerror = function () {
      var s = document.createElement("span");
      s.className = "vx-flagtxt"; s.dir = "ltr"; s.textContent = "+" + code;
      img.replaceWith(s);
    };
  }
  flagFallback(telBtn.querySelector("img"), "20");
  $$("li img", telMenu).forEach(function (im) { im.onerror = function () { im.style.visibility = "hidden"; }; });
  dropdown(telRoot, telBtn, telMenu, function (li) {
    $$("li", telMenu).forEach(function (x) { x.setAttribute("aria-selected", "false"); });
    li.setAttribute("aria-selected", "true");
    dial = li.getAttribute("data-dial"); iso = li.getAttribute("data-iso");
    var old = telBtn.querySelector("img, .vx-flagtxt");
    var im = document.createElement("img");
    im.alt = ""; im.width = 24; im.height = 18;
    flagFallback(im, dial);
    im.src = "https://flagcdn.com/24x18/" + iso + ".png";
    old.replaceWith(im);
    telBtn.setAttribute("title", "+" + dial);
    clearErr(els.phone);
  }, false);

  /* ---------- validation ---------- */
  function fieldOf(el) { return el.closest(".vx-f"); }
  function setErr(el, msg) {
    var f = fieldOf(el); f.classList.add("is-invalid");
    var p = f.querySelector(".vx-err"); if (p) p.textContent = msg;
  }
  function clearErr(el) {
    var f = fieldOf(el); if (!f) return;
    f.classList.remove("is-invalid");
    var p = f.querySelector(".vx-err"); if (p) p.textContent = "";
  }
  [els.area, els.name, els.phone, els.email].forEach(function (el) {
    el.addEventListener("input", function () { clearErr(el); });
  });

  /* digits the visitor typed, without a repeated country code */
  function phoneDigits() {
    var p = els.phone.value.replace(/[^0-9]/g, "");
    if (p.indexOf("00" + dial) === 0) p = p.slice(2 + dial.length);
    else if (p.indexOf(dial) === 0 && p.length > (dial === "20" ? 11 : 9)) p = p.slice(dial.length);
    return p;
  }
  function phoneValid() {
    var p = phoneDigits();
    if (dial === "20") return /^0?1[0125][0-9]{8}$/.test(p);
    return /^0?[0-9]{6,14}$/.test(p);
  }

  function validate() {
    var bad = [];
    if (!els.region.value) { setErr(els.region, T.errRegion); bad.push(els.region); }
    else if (!els.zone.value) { setErr(els.zone, T.errZone); bad.push(els.zone); }
    var a = parseFloat(els.area.value);
    if (!(a >= 25 && a <= 2000)) { setErr(els.area, T.errArea); bad.push(els.area); }
    if (!els.finish.value) { setErr(els.finish, T.errFinish); bad.push(els.finish); }
    if (!els.intent.value) { setErr(els.intent, T.errIntent); bad.push(els.intent); }
    if (els.name.value.trim().length < 2) { setErr(els.name, T.errName); bad.push(els.name); }
    if (!phoneValid()) { setErr(els.phone, T.errPhone); bad.push(els.phone); }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(els.email.value.trim())) { setErr(els.email, T.errEmail); bad.push(els.email); }
    if (bad.length) bad[0].focus();
    return !bad.length;
  }

  /* ---------- estimator (mirror of api/lib/estimator.php) ---------- */
  function areaFactor(area) {
    for (var i = 0; i < D.areaBands.length; i++) if (area <= D.areaBands[i].max) return D.areaBands[i].f;
    return 1;
  }
  function estimate(inp) {
    var region = find(D.regions, inp.region);
    var zone = region ? find(region.zones, inp.zone) : null;
    if (!region || !zone) return null;
    var area = +inp.area;
    if (!(area >= 25 && area <= 2000)) return null;

    var type = find(D.types, inp.type) || D.types[0];
    var finish = find(D.finishes, inp.finish) || find(D.finishes, "super-lux");
    var age = find(D.ages, "0-5");
    var legal = find(D.legal, "contract");
    var pay = find(D.payment, "cash");
    var flat = ["apartment", "studio", "duplex", "penthouse"].indexOf(type.id) > -1;
    var floor = flat ? find(D.floors, "low") : null;

    var feats = inp.features || [];
    var featSum = 0;
    feats.forEach(function (id) { var f = find(D.features, id); if (f) featSum += f.p; });
    featSum = Math.max(-0.15, Math.min(D.featureCap, featSum));

    var perSqm = zone.sqm * type.f * finish.f * age.f * legal.f * pay.f * areaFactor(area) * (1 + featSum);
    if (floor) perSqm *= floor.f;
    var value = perSqm * area;

    /* PHP counts filled beds / baths / legal / age / finish — this form sends finish only */
    var filled = inp.finish ? 1 : 0;
    var spread = D.spread + (filled >= 5 ? 0 : 0.03) + (feats.length ? 0 : 0.01);

    return {
      perSqm: Math.round(perSqm), marketPerSqm: zone.sqm, value: Math.round(value),
      low: Math.round(value * (1 - spread)), high: Math.round(value * (1 + spread)),
      rentMonthly: Math.round(value * region.yield / 12),
      rentSeason: region.seasonal ? Math.round(value * 0.045) : 0,
      seasonal: !!region.seasonal, area: area
    };
  }

  /* ---------- submit ---------- */
  function collect() {
    return {
      source: "valuation-form",
      lang: LANG,
      region: els.region.value,
      zone: els.zone.value,
      type: "apartment",
      area: parseFloat(els.area.value),
      finish: els.finish.value,
      features: views.slice(),
      intent: els.intent.value,
      name: els.name.value.trim(),
      phone: phoneDigits(),
      dial: dial,
      country: iso,
      email: els.email.value.trim()
    };
  }

  function sendLead(payload) {
    if (!CFG.apiBase || location.protocol === "file:") return Promise.resolve(null);
    return fetch(CFG.apiBase + "lead.php", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      keepalive: true
    }).then(function (r) { return r.json(); }).catch(function () { return null; });
  }

  var btnLabel = els.submit.innerHTML;
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    closeAll();
    if (!validate()) return;

    var payload = collect();
    var local = estimate(payload);
    if (!local) { setErr(els.zone, T.errZone); return; }
    payload.estimatedValue = local.value;
    payload.perSqm = local.perSqm;

    els.submit.disabled = true;
    els.submit.innerHTML = '<span class="vx-spin" aria-hidden="true"></span><span>' + esc(T.calculating) + "</span>";

    var wait = new Promise(function (res) { setTimeout(res, 900); });
    var timeout = new Promise(function (res) { setTimeout(function () { res(null); }, 6000); });

    Promise.all([Promise.race([sendLead(payload), timeout]), wait]).then(function (out) {
      var res = out[0];
      var r = (res && res.ok && res.result && res.result.value) ? res.result : local;
      els.submit.disabled = false;
      els.submit.innerHTML = btnLabel;
      showResult(payload, r, !!(res && res.ok));
    });
  });

  /* ---------- result ---------- */
  function scrollToTool() {
    var top = document.getElementById("vx").getBoundingClientRect().top + window.scrollY - 90;
    window.scrollTo({ top: Math.max(0, top), behavior: "smooth" });
  }

  function showResult(inp, r, saved) {
    var region = find(D.regions, inp.region);
    var zone = find(region.zones, inp.zone);
    var fin = find(D.finishes, inp.finish);
    var cur = T.currency;
    var sep = LANG === "ar" ? "، " : ", ";
    var zoneLabel = zone[LANG] + sep + region[LANG];

    var meta = [T.apartment + " " + fmt(inp.area) + " " + T.sqm, zoneLabel, fin[LANG]]
      .concat(inp.features.map(viewLabel).filter(Boolean))
      .map(esc).join(sep);

    /* comparison: up to 9 areas around the chosen one, ranked by price per m² */
    var zones = region.zones.slice().sort(function (a, b) { return b.sqm - a.sqm; });
    var idx = zones.indexOf(zone);
    var from = Math.max(0, Math.min(idx - 4, zones.length - 9));
    var max = zones[0].sqm;
    var cmp = zones.slice(from, from + 9).map(function (z) {
      return '<li class="' + (z === zone ? "is-you" : "") + '"><span>' + esc(z[LANG]) + "</span>" +
        '<span class="vxr-cmp__track"><span class="vxr-cmp__fill" style="width:' + Math.max(4, z.sqm / max * 100).toFixed(1) + '%"></span></span>' +
        '<span class="vxr-cmp__v">' + fmt(z.sqm) + "</span></li>";
    }).join("");

    var rentLabel = r.seasonal ? T.rentSeason : T.rent;
    var rentVal = r.seasonal ? r.rentSeason : r.rentMonthly;

    var wa = "https://wa.me/" + CFG.waNumber + "?text=" + encodeURIComponent(tpl(T.waMsg, {
      area: fmt(inp.area), zone: zoneLabel, value: fmt(r.value)
    }));

    resultBox.innerHTML =
      '<div class="vxr-head">' +
        "<h2>" + esc(T.resultTitle) + "</h2>" +
        '<p class="vxr-meta">' + meta + "</p>" +
        '<p class="vxr-value">' + fmt(r.value) + "<small>" + esc(cur) + "</small></p>" +
      "</div>" +
      '<div class="vxr-range">' +
        '<div class="vxr-bar"><span class="vxr-pin"><span>' + esc(T.mid) + "</span></span></div>" +
        '<div class="vxr-ends">' +
          "<div>" + esc(T.low) + "<strong>" + fmt(r.low) + " " + esc(cur) + "</strong></div>" +
          "<div>" + esc(T.high) + "<strong>" + fmt(r.high) + " " + esc(cur) + "</strong></div>" +
        "</div>" +
      "</div>" +
      '<div class="vxr-stats">' +
        '<div class="vxr-stat"><span>' + esc(T.perSqm) + "</span><strong>" + fmt(r.perSqm) + "</strong><small>" + esc(T.perSqmUnit) + "</small></div>" +
        '<div class="vxr-stat"><span>' + esc(T.zoneSqm) + "</span><strong>" + fmt(r.marketPerSqm) + "</strong><small>" + esc(T.perSqmUnit) + "</small></div>" +
        '<div class="vxr-stat"><span>' + esc(rentLabel) + "</span><strong>" + fmt(rentVal) + "</strong><small>" + esc(cur) + "</small></div>" +
      "</div>" +
      '<div class="vxr-block"><h3>' + esc(tpl(T.compareTitle, { region: region[LANG] })) + '</h3><ul class="vxr-cmp">' + cmp + "</ul></div>" +
      '<div class="vxr-block" id="vxr-similar" hidden></div>' +
      (saved ? '<p class="vxr-ok">' + esc(T.sentOk) + "</p>" : "") +
      '<div class="vxr-actions">' +
        '<button type="button" class="btn btn--outline" data-again>' + esc(T.again) + "</button>" +
        '<a class="btn btn--wa" href="' + wa + '" target="_blank" rel="noopener">' + esc(T.talk) + "</a>" +
      "</div>" +
      '<p class="vxr-note">' + esc(T.disclaimer) + "<br>" + esc(tpl(T.updated, { date: D.updated })) + "</p>";

    form.hidden = true;
    resultBox.hidden = false;
    scrollToTool();
    resultBox.focus({ preventScroll: true });

    $("[data-again]", resultBox).addEventListener("click", function () {
      resultBox.hidden = true; resultBox.innerHTML = "";
      form.hidden = false;
      scrollToTool();
      els.area.focus({ preventScroll: true });
    });

    loadSimilar(inp, zone);
  }

  /* Elite listings in the same city, closest in size — loaded only when needed */
  function loadSimilar(inp, zone) {
    var box = $("#vxr-similar"); if (!box) return;
    var ready = window.ELITE_PROPERTIES ? Promise.resolve() : new Promise(function (res) {
      var s = document.createElement("script");
      s.src = CFG.propertiesSrc; s.onload = res; s.onerror = res;
      document.body.appendChild(s);
    });
    ready.then(function () {
      var list = window.ELITE_PROPERTIES || [];
      var resid = ["apartment", "duplex", "penthouse", "studio", "chalet"];
      var names = [zone.ar, zone.en.toLowerCase()];
      var picks = list.filter(function (p) {
        return p.city === inp.region && p.purpose === "sale" && p.priceUnit === "total" &&
          resid.indexOf(p.type) > -1 && p.area && p.price;
      }).map(function (p) {
        var loc = p.location ? (p.location.ar + " " + p.location.en).toLowerCase() : "";
        var same = names.some(function (n) { return loc.indexOf(n) > -1; });
        return { p: p, score: (same ? 0 : 100000) + Math.abs(p.area - inp.area) };
      }).sort(function (a, b) { return a.score - b.score; }).slice(0, 3).map(function (x) { return x.p; });

      if (!picks.length || !document.body.contains(box)) return;
      box.innerHTML = "<h3>" + esc(T.similarTitle) + '</h3><div class="vxr-similar">' + picks.map(function (p) {
        return '<a class="vxr-card" href="property.html?id=' + encodeURIComponent(p.id) + '">' +
          '<img src="' + CFG.base + esc(p.image) + '" alt="" loading="lazy" width="400" height="300">' +
          "<div><h4>" + esc(p.title[LANG]) + "</h4><p>" + esc(p.location[LANG]) + sep() + fmt(p.area) + " " + esc(T.sqm) + "</p>" +
          "<strong>" + fmt(p.price) + " " + esc(T.currency) + "</strong></div></a>";
      }).join("") + '</div><a class="vxr-more" href="properties.html?location=' + encodeURIComponent(inp.region) + '">' + esc(T.similarAll) + "</a>";
      box.hidden = false;
    });
  }
  function sep() { return LANG === "ar" ? "، " : ", "; }
})();
