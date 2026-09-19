/* ==========================================================================
   Elite Real Estate — single property page (rendered from ?id=)
   ========================================================================== */
(function () {
  "use strict";

  var root = document.getElementById("property-root");
  if (!root) return;

  var html = document.documentElement;
  var lang = html.lang === "ar" ? "ar" : "en";
  var base = html.dataset.base || "";
  var T = JSON.parse(document.getElementById("i18n-data").textContent);
  var C = window.EliteCards;
  var props = window.ELITE_PROPERTIES || [];
  var COMPS = window.ELITE_COMPOUNDS || {};
  var projects = window.ELITE_PROJECTS || [];

  function t(k) { return T[k] || k; }
  function money(n) { return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ","); }

  var IC = {
    pin: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 21s7-5.6 7-11a7 7 0 1 0-14 0c0 5.4 7 11 7 11z"/><circle cx="12" cy="10" r="2.5"/></svg>',
    check: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="m4 12 5 5L20 6"/></svg>',
    wa: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a10 10 0 0 0-8.6 15L2 22l5.2-1.4A10 10 0 1 0 12 2zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3.1.8.8-3-.2-.3A8.2 8.2 0 1 1 12 20.2z"/><path d="M17.5 14.4c-.3-.2-1.7-.8-2-.9-.3-.1-.5-.2-.7.2-.2.3-.7.9-.9 1.1-.2.2-.3.2-.6.1-1.7-.9-2.9-1.6-4-3.5-.3-.5.3-.5.8-1.5.1-.2 0-.4 0-.5 0-.2-.7-1.6-.9-2.2-.2-.6-.5-.5-.7-.5h-.6c-.2 0-.5.1-.8.4-.3.3-1 1-1 2.5s1.1 2.9 1.2 3.1c.2.2 2.2 3.3 5.3 4.6 2 .8 2.7.9 3.7.8.6-.1 1.7-.7 2-1.4.2-.7.2-1.2.2-1.4-.1-.1-.3-.2-.6-.4z"/></svg>',
    phone: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a1 1 0 0 1-1 1A16 16 0 0 1 4 5a1 1 0 0 1 1-1z"/></svg>',
    arrow: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M5 12h14m-6-6 6 6-6 6"/></svg>'
  };

  var id = new URLSearchParams(location.search).get("id");
  var p = props.filter(function (x) { return x.id === id; })[0];

  if (!p) {
    root.innerHTML = '<div class="wrap"><h1>' + t("results.none") + "</h1>" +
      '<p><a class="btn btn--outline" href="properties.html">' + t("featured.viewAll") + "</a></p></div>";
    return;
  }

  var project = projects.filter(function (x) { return x.slug === p.project; })[0];
  var ask = C.isAsk(p);
  var priceText = ask ? t("common.requestPrice") : t("common.egp") + " " + money(p.price) + (p.priceUnit === "monthly" ? " " + t("common.month") : "");
  var desc = (p.description && (p.description[lang] || p.description.en || p.description.ar)) || "";
  var comp = COMPS[p.compound];
  var badge = p.purpose === "rent" ? t("badge.rent") : t("badge.sale");

  /* SEO-ish head updates for shared links */
  document.title = p.title[lang] + " | " + t("brand");
  var md = document.querySelector('meta[name="description"]');
  if (md) md.setAttribute("content", desc.slice(0, 155));

  /* WhatsApp context for the floating widget and CTA buttons */
  document.body.dataset.waContext = (lang === "ar"
    ? "مهتم بالوحدة " + p.id + " - " + p.title.ar + " (" + priceText + ")"
    : "I'm interested in " + p.id + " - " + p.title.en + " (" + priceText + ")");

  var facts = [
    [t("common.ref"), p.id],
    [t("search.type"), t("type." + p.type)],
    [t("common.area"), Number(p.area) > 0 ? p.area + " " + t("common.sqm") : "—"],
    [t("filters.bedrooms"), p.beds || "—"],
    [t("common.baths"), p.baths || "—"],
    [t("common.finishing"), C.loc(p.finishing, lang) || "—"],
    [t("common.delivery"), C.loc(p.delivery, lang) || "—"],
    [t("common.floor"), p.floor || "—"]
  ];

  var factsHTML = facts.map(function (f) {
    return '<div class="fact"><span>' + C.esc(f[0]) + "</span><b>" + C.esc(f[1]) + "</b></div>";
  }).join("");

  var featuresHTML = (p.features || []).map(function (f) {
    return '<span class="pill">' + IC.check + C.esc(t("ft." + f)) + "</span>";
  }).join("");

  var similar = props.filter(function (x) {
    return x.id !== p.id && (x.city === p.city || x.type === p.type);
  }).slice(0, 3);

  function card(x) { return C.card(x, { lang: lang, base: base }); }

  var gallery = (p.gallery && p.gallery.length ? p.gallery : [p.image]);
  var fbAttr = comp ? ' data-fallback="' + C.esc(C.imgSrc(base, comp.cover)) + '"' : "";
  var galleryMain = C.imgSrc(base, gallery[0]);
  var ttl = C.esc(p.title[lang]);
  var gallerySide = gallery.slice(1, 3).map(function (src) { return '<img src="' + C.esc(C.imgSrc(base, src)) + '" alt="' + ttl + '" loading="lazy" width="1200" height="800" referrerpolicy="no-referrer"' + fbAttr + '>'; }).join("");
  if (!gallerySide) gallerySide = '<img src="' + C.esc(galleryMain) + '" alt="' + ttl + '" loading="lazy" width="1200" height="800" referrerpolicy="no-referrer"' + fbAttr + '>';
  var paymentHTML = p.paymentSummary ? '<div class="block"><h2>' + t("common.payment") + '</h2><p>' + C.esc(p.paymentSummary) + '</p></div>' : '';

  root.style.paddingTop = "0";
  root.innerHTML =
    '<section class="proj-hero" style="padding-top:84px">' +
      '<div class="proj-gallery"><div class="proj-gallery__main">' +
      '<img src="' + C.esc(galleryMain) + '" alt="' + ttl + '" width="1200" height="800" referrerpolicy="no-referrer"' + fbAttr + '></div>' +
      '<div class="proj-gallery__side">' + gallerySide +
      "</div></div></section>" +

    '<div class="wrap"><div class="proj-layout"><div>' +
      '<nav class="breadcrumbs" style="color:var(--muted);margin-top:26px">' +
        '<a href="index.html">' + t("breadcrumb.home") + "</a> <span>/</span> " +
        '<a href="properties.html">' + t("nav.properties") + "</a> <span>/</span> <span>" + ttl + "</span></nav>" +

      '<div class="proj-head"><div>' +
        '<span class="card__badge" style="position:static;display:inline-block;margin-bottom:12px">' + badge + "</span>" +
        "<h1>" + ttl + "</h1>" +
        '<p class="card__place">' + IC.pin + C.esc(C.loc(p.location, lang)) + "</p></div>" +
        '<div class="proj-price"><small>' + t("common.price") + "</small><strong>" + C.esc(priceText) + "</strong></div>" +
      "</div>" +

      '<div class="facts" style="grid-template-columns:repeat(4,1fr)">' + factsHTML + "</div>" +

      '<div class="block"><h2>' + t("common.about") + "</h2><p>" + C.esc(desc) + "</p>" +
      (comp ? '<p><a class="link-arrow" href="sahel/' + C.esc(comp.slug) + '.html">' +
        (lang === "ar" ? "كل وحدات " : "All units in ") + C.esc(C.loc(comp.name, lang)) + IC.arrow + "</a></p>" : "") +
      (project ? '<p><a class="link-arrow" href="projects/' + project.slug + '.html">' +
        (lang === "ar" ? "تفاصيل مشروع " : "About ") + project.name[lang] + IC.arrow + "</a></p>" : "") +
      "</div>" +

      (featuresHTML ? '<div class="block"><h2>' + t("common.amenities") + '</h2><div class="pill-list">' + featuresHTML + "</div></div>" : "") +
      paymentHTML +

      '<p class="disclaimer">' + t("disclaimer") + "</p>" +
    "</div>" +

    '<aside><div class="aside-card">' +
      "<h3>" + t("cta.requestPrice") + "</h3><p>" + t("contact.subtitle") + "</p>" +
      '<button class="btn btn--wa btn--block" data-wa>' + IC.wa + t("cta.whatsapp") + "</button>" +
      '<a class="btn btn--outline btn--block" href="tel:+' + window.ELITE_CONFIG.phoneIntl + '">' + IC.phone + t("cta.call") + "</a>" +
      '<a class="btn btn--solid btn--block" href="contact.html">' + t("cta.bookVisit") + "</a>" +
      '<p class="aside-note">' + t("common.ref") + ": " + p.id + "</p>" +
    "</div></aside></div></div>" +

    (similar.length
      ? '<section class="section section--cream"><div class="wrap"><h2 class="section__title" style="margin-bottom:32px">' +
        t("common.similar") + '</h2><div class="cards">' + similar.map(card).join("") + "</div></div></section>"
      : "");

  root.querySelectorAll("[data-wa]").forEach(function (el) {
    el.addEventListener("click", function () {
      window.open(window.waLink(document.body.dataset.waContext), "_blank", "noopener");
    });
  });

  /* structured data for the individual listing */
  var ld = document.createElement("script");
  ld.type = "application/ld+json";
  ld.textContent = JSON.stringify({
    "@context": "https://schema.org",
    "@type": "Product",
    name: p.title[lang],
    description: desc,
    image: [/^https?:/.test(p.image) ? p.image : window.ELITE_CONFIG.siteUrl + "/" + p.image],
    sku: p.id,
    offers: ask ? undefined : {
      "@type": "Offer",
      price: p.price,
      priceCurrency: "EGP",
      availability: "https://schema.org/InStock",
      url: location.href
    }
  });
  if (window.EliteImgFix) window.EliteImgFix.sweep();
  document.head.appendChild(ld);
})();
