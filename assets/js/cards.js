/* ==========================================================================
   Elite Real Estate — shared card renderer
   One place that draws a unit, so the site and the admin preview always match.
   Used by: properties page, home, property page, Sahel compound pages, /admin preview.

   Unit fields it understands (data/properties.json):
     id, title{ar,en}, location{ar,en}, type, purpose, city, compound, price, priceOnRequest,
     maxPrice, area, areaMax, beds, baths, finishing{ar,en}, delivery{ar,en}, image, gallery[],
     description{ar,en}, features[], featured, order, createdAt, saleType, plans[], paymentPlan{}
   ========================================================================== */
(function (root) {
  "use strict";

  var TXT = {
    ar: {
      egp: "ج.م", egpLong: "جنيه", month: "شهريًا", sqm: "م²", beds: "غرف", baths: "حمام", sale: "للبيع", rent: "للإيجار",
      details: "تفاصيل الوحدة", ask: "السعر عند الطلب", source: "مصدر خارجي", featured: "مميزة",
      ready: "استلام فوري", delivery: "الاستلام", years: "سنين", cash: "كاش", call: "اتصل بنا", wa: "واتساب",
      coast: "الساحل الشمالي", from: "يبدأ من", devSale: "بيع من المطور", resale: "إعادة بيع"
    },
    en: {
      egp: "EGP", egpLong: "EGP", month: "/ month", sqm: "sqm", beds: "Beds", baths: "Baths", sale: "For sale", rent: "For rent",
      details: "View details", ask: "Price on request", source: "External source", featured: "Featured",
      ready: "Ready to move", delivery: "Delivery In", years: "Years", cash: "Cash Payment", call: "Call Us", wa: "Whatsapp",
      coast: "North Coast", from: "Starting from", devSale: "Developer Sale", resale: "Resale"
    }
  };

  var TYPES = {
    ar: { apartment: "شقة", villa: "فيلا", chalet: "شاليه", townhouse: "تاون هاوس", twinhouse: "توين هاوس", duplex: "دوبلكس",
      penthouse: "بنتهاوس", office: "مكتب إداري", retail: "تجاري", medical: "القطاع الطبي", studio: "ستوديو",
      cabin: "كابينة", administrative: "إداري", pharmacy: "صيدلية", loft: "لوفت", unit: "وحدة" },
    en: { apartment: "Apartment", villa: "Villa", chalet: "Chalet", townhouse: "Townhouse", twinhouse: "Twin house", duplex: "Duplex",
      penthouse: "Penthouse", office: "Office", retail: "Commercial", medical: "Medical", studio: "Studio",
      cabin: "Cabin", administrative: "Administrative", pharmacy: "Pharmacy", loft: "Loft", unit: "Unit" }
  };

  var AMENITIES = {
    garden: ["حديقة", "Garden"], roof: ["روف", "Has roof"], driver: ["غرفة سواق", "Driver room"],
    nanny: ["غرفة مربية", "Nanny room"], kitchen: ["مطبخ مجهز", "Kitchen cabinets"], ac: ["تكييفات", "A/C"],
    row5: ["الصف الخامس", "5th row"], commercial: ["منطقة تجارية", "Commercial strip"],
    clubhouse: ["كلوب هاوس", "Clubhouse"], spa: ["سبا", "Shared spa"], gym: ["جيم", "Shared gym"],
    kids: ["منطقة ألعاب أطفال", "Children's play area"], parking: ["جراج تحت الأرض", "Underground parking"],
    seaView: ["إطلالة بحر", "Sea view"], pool: ["حمام سباحة", "Pool"], security: ["أمن 24 ساعة", "24/7 security"],
    balcony: ["بلكونة", "Balcony"], elevator: ["أسانسير", "Elevator"]
  };
  var FREQ = {
    quarterly: ["ربع سنوي", "Quarterly"], monthly: ["شهري", "Monthly"],
    "semi-annually": ["نصف سنوي", "Semi-annually"], annually: ["سنوي", "Annually"]
  };

  var IC = {
    pin: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 21s7-5.6 7-11a7 7 0 1 0-14 0c0 5.4 7 11 7 11z"/><circle cx="12" cy="10" r="2.5"/></svg>',
    area: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 9V4h5M20 15v5h-5M20 9V4h-5M4 15v5h5"/></svg>',
    bed: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M3 18v-6h18v6M3 12V7m18 5V9a2 2 0 0 0-2-2h-5v5"/><circle cx="7.5" cy="9.5" r="1.8"/></svg>',
    bath: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 12h16v3a4 4 0 0 1-4 4H8a4 4 0 0 1-4-4v-3zM7 12V6a2 2 0 0 1 4 0"/></svg>',
    arrow: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M5 12h14m-6-6 6 6-6 6"/></svg>',
    phone: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a1 1 0 0 1-1 1A16 16 0 0 1 4 5a1 1 0 0 1 1-1z"/></svg>',
    wa: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M17.5 14.4c-.3-.2-1.7-.8-2-.9-.3-.1-.5-.2-.7.2-.2.3-.7.9-.9 1.1-.2.2-.3.2-.6.1-1.7-.9-2.9-1.6-4-3.5-.3-.5.3-.5.8-1.5.1-.2 0-.4 0-.5 0-.2-.7-1.6-.9-2.2-.2-.6-.5-.5-.7-.5h-.6c-.2 0-.5.1-.8.4-.3.3-1 1-1 2.5s1.1 2.9 1.2 3.1c.2.2 2.2 3.3 5.3 4.6 2 .8 2.7.9 3.7.8.6-.1 1.7-.7 2-1.4.2-.7.2-1.2.2-1.4-.1-.1-.3-.2-.6-.4z"/><path d="M12 2a10 10 0 0 0-8.6 15L2 22l5.2-1.4A10 10 0 1 0 12 2zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3.1.8.8-3-.2-.3A8.2 8.2 0 1 1 12 20.2z"/></svg>',
    nxBed: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M3 18v-6.5A1.5 1.5 0 0 1 4.5 10h15a1.5 1.5 0 0 1 1.5 1.5V18M3 15h18M5 10V7a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v3M3 18v1.5M21 18v1.5"/></svg>',
    nxBath: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M6 12V6.5a3 3 0 0 1 6 0M4 12h16v1.5a5.5 5.5 0 0 1-5.5 5.5h-5A5.5 5.5 0 0 1 4 13.5zM8 21l.5-2M16 21l-.5-2M10 17.5v.01M12 16v.01M14 17.5v.01"/></svg>',
    nxArea: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="3.5" y="3.5" width="17" height="17" rx="1.5"/><path d="M8 16V8h8"/></svg>',
    share: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M14 4h6v6M20 4l-9 9M18 14v4a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4"/></svg>',
    heart: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20s-7-4.4-9.2-9A5 5 0 0 1 12 6.3 5 5 0 0 1 21.2 11C19 15.6 12 20 12 20z"/></svg>'
  };

  /* ---------- helpers ---------- */
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function money(n) { return String(Math.round(Number(n) || 0)).replace(/\B(?=(\d{3})+(?!\d))/g, ","); }
  function L(lang) { return lang === "ar" ? "ar" : "en"; }
  function loc(v, lang) { return v && typeof v === "object" ? (v[lang] || v.en || v.ar || "") : (v || ""); }
  function isAsk(p) { return !!p.priceOnRequest || !(Number(p.price) > 0); }
  function isRemote(s) { return /^(https?:)?\/\//i.test(s) || /^data:/i.test(s); }
  function imgSrc(base, path) {
    if (!path) return "";
    return isRemote(path) ? path : (base || "") + path.replace(/^\/+/, "");
  }
  function typeLabel(ty, lang) { return (TYPES[lang] || TYPES.en)[ty] || (ty ? String(ty).charAt(0).toUpperCase() + String(ty).slice(1) : ""); }
  function initials(s) {
    var w = String(s || "").split(/[\s\-()]+/).filter(Boolean).slice(0, 2);
    return (w.map(function (x) { return x.charAt(0); }).join("") || "E").toUpperCase();
  }
  function phoneIntl() { return (root.ELITE_CONFIG && root.ELITE_CONFIG.phoneIntl) || "201111788812"; }
  function waHref(msg) { return "https://wa.me/" + phoneIntl() + "?text=" + encodeURIComponent(msg); }

  /* Default order everywhere: featured first, then the admin's "order" number, then the rest. */
  function orderKey(p) { return (p.order === null || p.order === undefined || p.order === "") ? 1e9 : Number(p.order); }
  function byDefault(a, b) {
    if (!!a.featured !== !!b.featured) return a.featured ? -1 : 1;
    var oa = orderKey(a), ob = orderKey(b);
    if (oa !== ob) return oa - ob;
    var ca = a.createdAt || "", cb = b.createdAt || "";
    if (ca !== cb) return ca < cb ? 1 : -1;
    return String(a.id) < String(b.id) ? -1 : 1;
  }
  /* Inside a compound: featured, order, then cheapest first with "price on request" last. */
  function byCompound(a, b) {
    if (!!a.featured !== !!b.featured) return a.featured ? -1 : 1;
    var oa = orderKey(a), ob = orderKey(b);
    if (oa !== ob) return oa - ob;
    var pa = isAsk(a) ? 1e15 : Number(a.price), pb = isAsk(b) ? 1e15 : Number(b.price);
    if (pa !== pb) return pa - pb;
    return String(a.id) < String(b.id) ? -1 : 1;
  }

  /* ---------- the site's standard card (properties page, home, similar units) ---------- */
  function priceHtml(p, lang) {
    var t = TXT[L(lang)];
    if (isAsk(p)) return '<span class="is-ask">' + esc(t.ask) + "</span>";
    var s = esc(t.egp) + " " + money(p.price);
    if (p.priceUnit === "monthly") s += " <small>" + esc(t.month) + "</small>";
    return s;
  }

  /* o: { lang, base, source (show "external source" badge), lazy } */
  function card(p, o) {
    o = o || {};
    var lang = L(o.lang), base = o.base || "", t = TXT[lang];
    var url = base + lang + "/property.html?id=" + encodeURIComponent(p.id);
    var title = loc(p.title, lang), place = loc(p.location, lang);
    var badge = p.purpose === "rent" ? t.rent : t.sale;
    var meta = "";
    if (Number(p.area) > 0) meta += "<span>" + IC.area + esc(p.area) + " " + esc(t.sqm) + "</span>";
    if (p.beds) meta += "<span>" + IC.bed + esc(p.beds) + " " + esc(lang === "ar" ? "غرف" : "beds") + "</span>";
    if (p.baths) meta += "<span>" + IC.bath + esc(p.baths) + " " + esc(lang === "ar" ? "حمامات" : "baths") + "</span>";
    var fb = o.fallback ? ' data-fallback="' + esc(imgSrc(base, o.fallback)) + '"' : "";
    return '<article class="card' + (o.reveal ? " scroll-fade" : "") + '" data-id="' + esc(p.id) + '">' +
      '<a class="card__media" href="' + url + '">' +
      '<img src="' + esc(imgSrc(base, p.image)) + '" alt="' + esc(title) + '" loading="lazy" width="900" height="675" referrerpolicy="no-referrer"' + fb + ">" +
      '<span class="card__badge">' + esc(badge) + "</span>" +
      (p.featured ? '<span class="card__flag">' + esc(t.featured) + "</span>" : "") +
      (o.source && p.sourceUrl ? '<span class="card__source">' + esc(t.source) + "</span>" : "") +
      "</a>" +
      '<div class="card__body">' +
      '<h3 class="card__title"><a href="' + url + '">' + esc(title) + "</a></h3>" +
      '<p class="card__place">' + IC.pin + esc(place) + "</p>" +
      '<div class="card__meta">' + meta + "</div>" +
      '<p class="card__price' + (isAsk(p) ? " is-ask" : "") + '">' + priceHtml(p, lang) + "</p>" +
      "</div>" +
      '<a class="card__foot" href="' + url + '">' + esc(t.details) + IC.arrow + "</a>" +
      "</article>";
  }

  /* ---------- Sahel compound pages ---------- */
  function plansOf(p) {
    var out = [];
    if (Array.isArray(p.plans) && p.plans.length) {
      p.plans.forEach(function (x) {
        if (x && x.installment) out.push({ i: x.installment, f: x.frequency || "monthly", y: x.years || null, d: x.down || null });
      });
      return out;
    }
    var pp = p.paymentPlan || {};
    if (pp.minInstallment && !pp.isCash) {
      out.push({ i: pp.minInstallment, f: pp.frequency || "monthly", y: pp.years || pp.numberOfInstallmentYears || null, d: pp.minDownPayment || null });
    }
    return out;
  }

  /* p = unit record, ctx = { lang, base, comp:{slug,km,name,area,region} } -> normalised object for cards + the unit sheet */
  function sahelUnit(p, ctx) {
    var lang = L(ctx.lang), t = TXT[lang], ar = lang === "ar", base = ctx.base || "";
    var comp = ctx.comp || {};
    var name = loc(comp.name, lang), nameEn = loc(comp.name, "en");
    var areaName = loc(comp.area || comp.region, lang);
    var sep = ar ? "، " : ", ";
    var title = loc(p.title, lang) || (typeLabel(p.type, lang) + (ar ? " في " : " in ") + name);
    var dl = String(loc(p.delivery, lang) || "");
    var ready = /ready|delivered|فوري/i.test(dl) || (/^\d{4}$/.test(dl) && Number(dl) <= 2025);
    var dlTxt = ready ? t.ready : dl;
    var plans = plansOf(p).map(function (x) {
      return { i: x.i, f: (FREQ[x.f] || ["", ""])[ar ? 0 : 1], y: x.y, d: x.d };
    });
    var cash = !plans.length && !!(p.paymentPlan && p.paymentPlan.isCash);
    var imgs = [];
    [p.image].concat(p.gallery || []).forEach(function (s) {
      if (s && imgs.indexOf(s) === -1) imgs.push(s);
    });
    var ask = isAsk(p);
    var areaTxt = Number(p.area) > 0 ? String(p.area) + (Number(p.areaMax) > 0 ? " ~ " + p.areaMax : "") : "";
    var sub = p.phase || name;
    var bits = [title];
    if (p.beds) bits.push(p.beds + (ar ? " غرف" : " beds"));
    if (areaTxt) bits.push(areaTxt + " " + (ar ? "م²" : "m²"));
    bits.push(ask ? t.ask : (ar ? "السعر " + money(p.price) + " جنيه" : "EGP " + money(p.price)));
    var msg = ar
      ? "السلام عليكم، مهتم بالوحدة: " + bits.join(" - ") + " في " + name + " (" + nameEn + ") - كود " + p.id + ". (من موقع إيليت)"
      : "Hello, I'm interested in: " + bits.join(" - ") + " in " + nameEn + " - ref " + p.id + ". (From Elite's website)";
    var fin = loc(p.finishing, lang);
    var am = [];
    (p.features || []).forEach(function (f) { if (AMENITIES[f]) am.push(AMENITIES[f][ar ? 0 : 1]); });
    return {
      id: p.id, ref: p.id, t: title, ct: title, ty: typeLabel(p.type, lang), type: p.type,
      loc: sub + sep + areaName + sep + t.coast, cardLoc: areaName + sep + t.coast,
      img: imgs.map(function (s) { return imgSrc(base, s); }), p: Number(p.price) || 0, mx: p.maxPrice || null, ask: ask,
      a: areaTxt, area: Number(p.area) || 0, bd: Number(p.beds) || 0, bt: Number(p.baths) || 0, dl: dlTxt, cmp: sub,
      sale: p.saleType === "developer" || p.saleType === "resale" ? p.saleType : "", fin: fin, am: am, plans: plans, cash: cash,
      desc: loc(p.description, lang), wa: waHref(msg), feat: !!p.featured, name: name
    };
  }

  function planLine(u, lang) {
    var t = TXT[L(lang)], pl = u.plans[0];
    if (pl && pl.i) {
      var yrs = pl.y ? (Number(pl.y) % 1 === 0 ? String(Number(pl.y)) : String(pl.y)) : "";
      return money(pl.i) + " " + pl.f + (yrs ? " /" + yrs + " " + t.years : "");
    }
    return u.cash ? t.cash : "";
  }

  /* o: { lang, base, i (index used by the sheet), compFallback } */
  function nxCard(u, o) {
    var lang = L(o.lang), t = TXT[lang], base = o.base || "";
    var i = o.i;
    var media = u.img.length
      ? '<img src="' + esc(u.img[0]) + '" alt="' + esc(u.t) + '" loading="lazy" referrerpolicy="no-referrer"' +
        (o.fallback ? ' data-fallback="' + esc(imgSrc(base, o.fallback)) + '"' : "") + ">"
      : '<span class="nx-card__ph">' + esc(initials(u.name)) + "</span>";
    var specs = "";
    if (u.bd) specs += "<li>" + IC.nxBed + "<b>" + u.bd + "</b><small>" + esc(t.beds) + "</small></li>";
    if (u.bt) specs += "<li>" + IC.nxBath + "<b>" + u.bt + "</b><small>" + esc(t.baths) + "</small></li>";
    if (u.a) specs += "<li>" + IC.nxArea + '<b dir="ltr">' + esc(u.a) + "</b><small>m²</small></li>";
    var inst = planLine(u, lang);
    return '<article class="nx-card" data-i="' + i + '" data-sale="' + esc(u.sale) + '" data-type="' + esc(u.type) + '" data-beds="' + u.bd +
      '" data-price="' + (u.ask ? 0 : u.p) + '" data-ask="' + (u.ask ? 1 : 0) + '" data-area="' + u.area + '">' +
      '<button type="button" class="nx-card__media" data-open="' + i + '" aria-label="' + esc(u.t) + '">' + media +
      (u.dl ? '<span class="nx-card__dl"><small>' + esc(t.delivery) + "</small><b>" + esc(u.dl) + "</b></span>" : "") +
      (u.feat ? '<span class="nx-card__flag">' + esc(t.featured) + "</span>" : "") +
      "</button>" +
      '<div class="nx-card__icons">' +
      '<button type="button" class="nx-ic" data-share="' + i + '" aria-label="Share">' + IC.share + "</button>" +
      '<button type="button" class="nx-ic" data-fav="' + esc(u.ref) + '" aria-label="Favourite" aria-pressed="false">' + IC.heart + "</button>" +
      "</div>" +
      '<div class="nx-card__body"><div class="nx-card__head">' +
      '<span class="nx-logo nx-logo--sm" aria-hidden="true">' + esc(initials(o.devInitials || u.name)) + "</span><div>" +
      '<p class="nx-card__loc">' + esc(u.cardLoc) + "</p>" +
      '<h3 class="nx-card__title"><button type="button" data-open="' + i + '">' + esc(u.t) + "</button></h3>" +
      "</div></div>" +
      (specs ? '<ul class="nx-specs">' + specs + "</ul>" : '<ul class="nx-specs nx-specs--none"></ul>') +
      '<div class="nx-card__foot"><div>' +
      '<p class="nx-card__inst">' + (inst ? esc(inst) : "&nbsp;") + "</p>" +
      (u.ask
        ? '<p class="nx-card__price is-ask">' + esc(t.ask) + "</p>"
        : '<p class="nx-card__price"><bdi>' + money(u.p) + "</bdi> " + esc(t.egpLong) + "</p>") +
      "</div>" +
      '<div class="nx-card__cta">' +
      '<a class="nx-round nx-round--call" href="tel:+' + esc(phoneIntl()) + '" aria-label="' + esc(t.call) + '">' + IC.phone + "</a>" +
      '<a class="nx-round nx-round--wa" href="' + esc(u.wa) + '" target="_blank" rel="noopener" aria-label="' + esc(t.wa) + '">' + IC.wa + "</a>" +
      "</div></div></div></article>";
  }

  root.EliteCards = {
    TXT: TXT, TYPES: TYPES, AMENITIES: AMENITIES, IC: IC,
    esc: esc, money: money, loc: loc, isAsk: isAsk, imgSrc: imgSrc, typeLabel: typeLabel, initials: initials, waHref: waHref,
    byDefault: byDefault, byCompound: byCompound, priceHtml: priceHtml,
    card: card, sahelUnit: sahelUnit, nxCard: nxCard, planLine: planLine
  };
})(window);
