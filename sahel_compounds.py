# -*- coding: utf-8 -*-
"""
Elite Real Estate — one page per compound on the Sahel map:  ar|en/sahel/<slug>.html

Every unit lives in data/properties.json and points at its compound with  "compound": "<slug>".
data/sahel_units.json only keeps compound details (developer, about, payment plan, gallery).

The page ships with the units already drawn (for search engines); assets/js/sahel-compound.js redraws
them from data/properties.js in the visitor's browser, so edits made in /admin show up without a rebuild.
assets/js/cards.js draws the same cards — keep the two in step (tools/parity_check.py compares them).

Called from build.py through sahel_map.build().  Edit data, then run  python3 build.py
"""

import json
import os
import re
from html import escape as html_escape
from urllib.parse import quote

TYPE_FALLBACK = {
    "cabin": ("كابينة", "Cabin"), "administrative": ("إداري", "Administrative"),
    "pharmacy": ("صيدلية", "Pharmacy"), "loft": ("لوفت", "Loft"), "unit": ("وحدة", "Unit"),
}
AMENITIES = {
    "garden": ("حديقة", "Garden"), "roof": ("روف", "Has roof"), "driver": ("غرفة سواق", "Driver room"),
    "nanny": ("غرفة مربية", "Nanny room"), "kitchen": ("مطبخ مجهز", "Kitchen cabinets"), "ac": ("تكييفات", "A/C"),
    "row5": ("الصف الخامس", "5th row"), "commercial": ("منطقة تجارية", "Commercial strip"),
    "clubhouse": ("كلوب هاوس", "Clubhouse"), "spa": ("سبا", "Shared spa"), "gym": ("جيم", "Shared gym"),
    "kids": ("منطقة ألعاب أطفال", "Children's play area"), "parking": ("جراج تحت الأرض", "Underground parking"),
    "seaView": ("إطلالة بحر", "Sea view"), "pool": ("حمام سباحة", "Pool"), "security": ("أمن 24 ساعة", "24/7 security"),
    "balcony": ("بلكونة", "Balcony"), "elevator": ("أسانسير", "Elevator"),
}
FREQ = {
    "quarterly": ("ربع سنوي", "Quarterly"), "monthly": ("شهري", "Monthly"),
    "semi-annually": ("نصف سنوي", "Semi-annually"), "annually": ("سنوي", "Annually"),
}
FINISH = {
    "finished": ("تشطيب كامل", "Finished"), "furnished": ("مفروش", "Furnished"),
    "semi_finished": ("نص تشطيب", "Semi finished"), "core_shell": ("على الطوب", "Core & shell"),
}


def slugify(s):
    s = s.lower().replace("'", "")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def _type_label(b, lang, ty):
    key = "type." + ty
    val = b.t(lang, key)
    if val != key:
        return val
    ar, en = TYPE_FALLBACK.get(ty, (ty.title(), ty.title()))
    return ar if lang == "ar" else en


def _local_ok(b, path):
    return bool(path) and path.rsplit(".", 1)[-1].lower() in ("jpg", "jpeg", "webp", "png") \
        and os.path.exists(os.path.join(b.ROOT, path))


def _loc(v, lang):
    if isinstance(v, dict):
        return v.get(lang) or v.get("en") or v.get("ar") or ""
    return v or ""


def is_ask(p):
    return bool(p.get("priceOnRequest")) or not ((p.get("price") or 0) > 0)


def _order_key(p):
    o = p.get("order")
    return 1e9 if o in (None, "") else float(o)


def sort_units(units):
    """featured first, then the admin's order number, then cheapest first (price on request last)."""
    return sorted(units, key=lambda p: (0 if p.get("featured") else 1, _order_key(p),
                                        1e15 if is_ask(p) else p["price"], str(p["id"])))


def _plans_of(p):
    out = []
    if p.get("plans"):
        for x in p["plans"]:
            if x and x.get("installment"):
                out.append({"i": x["installment"], "f": x.get("frequency") or "monthly", "y": x.get("years"), "d": x.get("down")})
        return out
    pp = p.get("paymentPlan") or {}
    if pp.get("minInstallment") and not pp.get("isCash"):
        out.append({"i": pp["minInstallment"], "f": pp.get("frequency") or "monthly",
                    "y": pp.get("years") or pp.get("numberOfInstallmentYears"), "d": pp.get("minDownPayment")})
    return out


def _fmt_years(y):
    if y in (None, ""):
        return ""
    return f"{y:g}" if isinstance(y, (int, float)) else str(y)


def sahel_unit(b, p, lang, comp, base):
    """Unit record -> the object the compound page (and assets/js/cards.js) works with."""
    ar = lang == "ar"
    money = b.money
    name, name_en = comp["name"][lang], comp["name"]["en"]
    area_name = _loc(comp.get("areaName") or comp["regionName"], lang)
    sep = "، " if ar else ", "
    coast = "الساحل الشمالي" if ar else "North Coast"
    title = _loc(p.get("title"), lang) or (_type_label(b, lang, p.get("type", "unit")) + (" في " if ar else " in ") + name)
    dl = str(_loc(p.get("delivery"), lang) or "")
    ready = bool(re.search(r"ready|delivered|فوري", dl, re.I)) or (bool(re.fullmatch(r"\d{4}", dl)) and int(dl) <= 2025)
    dl_txt = ("استلام فوري" if ar else "Ready to move") if ready else dl
    plans = [{"i": x["i"], "f": FREQ.get(x["f"], ("", ""))[0 if ar else 1], "y": x["y"], "d": x["d"]} for x in _plans_of(p)]
    cash = (not plans) and bool((p.get("paymentPlan") or {}).get("isCash"))
    imgs = []
    for cand in [p.get("image", "")] + list(p.get("gallery") or []):
        if not cand or cand in imgs:
            continue
        if cand.startswith("http") or os.path.exists(os.path.join(b.ROOT, cand)):
            imgs.append(cand)
    src = lambda x: x if x.startswith("http") else base + x  # noqa: E731
    ask = is_ask(p)
    area_txt = ""
    if (p.get("area") or 0) > 0:
        area_txt = f"{p['area']:g}" if isinstance(p["area"], float) else str(p["area"])
        if (p.get("areaMax") or 0) > 0:
            area_txt += f" ~ {p['areaMax']}"
    sub = p.get("phase") or name
    bits = [title]
    if p.get("beds"):
        bits.append(f"{p['beds']} غرف" if ar else f"{p['beds']} beds")
    if area_txt:
        bits.append(f"{area_txt} م²" if ar else f"{area_txt} m²")
    ask_txt = "السعر عند الطلب" if ar else "Price on request"
    bits.append(ask_txt if ask else (f"السعر {money(p['price'])} جنيه" if ar else f"EGP {money(p['price'])}"))
    msg = (f"السلام عليكم، مهتم بالوحدة: {' - '.join(bits)} في {name} ({name_en}) - كود {p['id']}. (من موقع إيليت)" if ar
           else f"Hello, I'm interested in: {' - '.join(bits)} in {name_en} - ref {p['id']}. (From Elite's website)")
    am = [AMENITIES[a][0 if ar else 1] for a in (p.get("features") or []) if a in AMENITIES]
    return {
        "id": p["id"], "ref": p["id"], "t": title, "ct": title, "ty": _type_label(b, lang, p.get("type", "unit")),
        "type": p.get("type", "unit"),
        "loc": f"{sub}{sep}{area_name}{sep}{coast}", "cardLoc": f"{area_name}{sep}{coast}",
        "img": [src(x) for x in imgs], "p": p.get("price") or 0, "mx": p.get("maxPrice") or None, "ask": ask,
        "a": area_txt, "area": p.get("area") or 0, "bd": p.get("beds") or 0, "bt": p.get("baths") or 0,
        "dl": dl_txt, "cmp": sub, "sale": p.get("saleType") if p.get("saleType") in ("developer", "resale") else "",
        "fin": _loc(p.get("finishing"), lang), "am": am, "plans": plans, "cash": cash,
        "desc": _loc(p.get("description"), lang), "wa": f"https://wa.me/{b.PHONE_INTL}?text={quote(msg, safe='')}",
        "feat": bool(p.get("featured")), "name": name,
    }


def compile_compounds(b):
    """Return the map regions with, for every compound, its slug and its unit records."""
    root = b.ROOT
    with open(os.path.join(root, "data", "sahel_map.json"), encoding="utf-8") as f:
        data = json.load(f)
    extra = {}
    extra_path = os.path.join(root, "data", "sahel_units.json")
    if os.path.exists(extra_path):
        with open(extra_path, encoding="utf-8") as f:
            extra = json.load(f).get("compounds", {})
    projects = {p["slug"]: p for p in b.PROJECTS_ALL}
    public = {p["slug"] for p in b.PROJECTS}

    by_comp = {}
    for p in b.PROPERTIES:
        if p.get("compound"):
            by_comp.setdefault(p["compound"], []).append(p)

    regions = []
    for r in data["regions"]:
        comps = []
        for c in r["compounds"]:
            slug = c.get("slug") or slugify(c["name"]["en"])
            ex = extra.get(slug, {})
            units = sort_units(by_comp.get(slug, []))
            pr = projects.get(c.get("project") or "")
            dev = ex.get("developer")
            if not dev:
                names = [u.get("developer") for u in units if u.get("developer")]
                d = (pr or {}).get("developer") or (names[0] if names else "")
                if isinstance(d, dict):
                    dev = d
                elif d:
                    dev = {"en": d, "ar": d}
            gallery = list(ex.get("gallery") or [])
            if pr:
                hero = b.img(pr.get("hero") or "")
                if _local_ok(b, hero):
                    gallery.insert(0, hero)
                for g in pr.get("gallery") or []:
                    gi = b.img(g)
                    if _local_ok(b, gi) and gi not in gallery:
                        gallery.append(gi)
            cover = f"assets/img/compounds/{slug}.jpg"
            priced = [u for u in units if not is_ask(u)]
            dev_prices = [u["price"] for u in priced if u.get("saleType") == "developer"]
            re_prices = [u["price"] for u in priced if u.get("saleType") == "resale"]
            all_prices = [u["price"] for u in priced]
            start = min(all_prices) if all_prices else (pr or {}).get("startingPrice") or 0
            photo = ""
            for u in units:
                for im in [u.get("image", "")] + list(u.get("gallery") or []):
                    if im and (im.startswith("http") or _local_ok(b, im)) and "assets/img/compounds/" not in im:
                        photo = im
                        break
                if photo:
                    break
            if not photo and gallery:
                photo = gallery[0]
            if not photo and _local_ok(b, cover):
                photo = cover
            comps.append({
                "km": c["km"], "name": c["name"], "slug": slug, "units": units,
                "price": start, "devStart": min(dev_prices) if dev_prices else 0,
                "resaleStart": min(re_prices) if re_prices else 0,
                "photo": photo, "cover": cover, "gallery": gallery, "developer": dev,
                "about": ex.get("about"), "plan": ex.get("plan"), "areaName": ex.get("area"),
                "regionName": r["name"], "regionId": r["id"],
                "project": c.get("project") if c.get("project") in public else "",
                "keyword": c.get("keyword") or c["match"][0],
            })
        comps.sort(key=lambda x: -x["km"])
        regions.append({"id": r["id"], "name": r["name"], "range": r["range"], "compounds": comps})
    return data, regions


def compounds_index(regions):
    """Small lookup used in the browser (data/compounds.js) and by the admin dashboard (data/compounds.json)."""
    out = {}
    for r in regions:
        for c in r["compounds"]:
            out[c["slug"]] = {
                "slug": c["slug"], "km": c["km"], "name": c["name"], "regionId": r["id"], "region": r["name"],
                "area": c.get("areaName") or r["name"], "developer": c.get("developer"),
                "cover": c["cover"], "photo": c["photo"], "galleryPhoto": (c.get("gallery") or [""])[0],
                "project": c.get("project") or "",
            }
    return out


# --------------------------------------------------------------------------
# page
# --------------------------------------------------------------------------
SVG = {
    "bed": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M3 18v-6.5A1.5 1.5 0 0 1 4.5 10h15a1.5 1.5 0 0 1 1.5 1.5V18M3 15h18M5 10V7a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v3M3 18v1.5M21 18v1.5"/></svg>',
    "bath": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M6 12V6.5a3 3 0 0 1 6 0M4 12h16v1.5a5.5 5.5 0 0 1-5.5 5.5h-5A5.5 5.5 0 0 1 4 13.5zM8 21l.5-2M16 21l-.5-2M10 17.5v.01M12 16v.01M14 17.5v.01"/></svg>',
    "area": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="3.5" y="3.5" width="17" height="17" rx="1.5"/><path d="M8 16V8h8"/></svg>',
    "share": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M14 4h6v6M20 4l-9 9M18 14v4a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4"/></svg>',
    "heart": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20s-7-4.4-9.2-9A5 5 0 0 1 12 6.3 5 5 0 0 1 21.2 11C19 15.6 12 20 12 20z"/></svg>',
    "filter": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M4 7h10M18 7h2M4 17h2M10 17h10"/><circle cx="16" cy="7" r="2"/><circle cx="8" cy="17" r="2"/></svg>',
    "sort": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M8 4v16M8 4 5 7M8 4l3 3M16 20V4M16 20l-3-3M16 20l3-3"/></svg>',
    "chev": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>',
}


def _initials(s):
    words = [w for w in re.split(r"[\s\-()]+", s or "") if w]
    return "".join(w[0] for w in words[:2]).upper() or "E"


CARD_TXT = {
    "ar": {"beds": "غرف", "baths": "حمام", "delivery": "الاستلام", "egp": "جنيه", "ask": "السعر عند الطلب", "featured": "مميزة",
           "call": "اتصل بنا", "wa": "واتساب", "years": "سنين", "cash": "كاش"},
    "en": {"beds": "Beds", "baths": "Baths", "delivery": "Delivery In", "egp": "EGP", "ask": "Price on request", "featured": "Featured",
           "call": "Call Us", "wa": "Whatsapp", "years": "Years", "cash": "Cash Payment"},
}


def _plan_line(b, u, lang):
    t = CARD_TXT[lang]
    if u["plans"] and u["plans"][0].get("i"):
        pl = u["plans"][0]
        yrs = _fmt_years(pl.get("y"))
        return f"{b.money(pl['i'])} {pl['f']}" + (f" /{yrs} {t['years']}" if yrs else "")
    return t["cash"] if u["cash"] else ""


def nx_card(b, lang, u, i, cover, dev_src, base):
    """One compound-page card. Mirrors EliteCards.nxCard() in assets/js/cards.js."""
    e = lambda x: html_escape(str(x if x is not None else ""), quote=True)  # noqa: E731
    money = b.money
    t = CARD_TXT[lang]
    if u["img"]:
        media = (f'<img src="{e(u["img"][0])}" alt="{e(u["t"])}" loading="lazy" referrerpolicy="no-referrer"'
                 f' data-fallback="{e(base + cover)}">')
    else:
        media = f'<span class="nx-card__ph">{e(_initials(u["name"]))}</span>'
    specs = ""
    if u["bd"]:
        specs += f'<li>{SVG["bed"]}<b>{u["bd"]}</b><small>{t["beds"]}</small></li>'
    if u["bt"]:
        specs += f'<li>{SVG["bath"]}<b>{u["bt"]}</b><small>{t["baths"]}</small></li>'
    if u["a"]:
        specs += f'<li>{SVG["area"]}<b dir="ltr">{e(u["a"])}</b><small>m²</small></li>'
    inst = _plan_line(b, u, lang)
    price = (f'<p class="nx-card__price is-ask">{t["ask"]}</p>' if u["ask"]
             else f'<p class="nx-card__price"><bdi>{money(u["p"])}</bdi> {t["egp"]}</p>')
    return (
        f'<article class="nx-card" data-i="{i}" data-sale="{e(u["sale"])}" data-type="{e(u["type"])}" data-beds="{u["bd"]}"'
        f' data-price="{0 if u["ask"] else u["p"]}" data-ask="{1 if u["ask"] else 0}" data-area="{u["area"]}">'
        f'<button type="button" class="nx-card__media" data-open="{i}" aria-label="{e(u["t"])}">{media}'
        + (f'<span class="nx-card__dl"><small>{t["delivery"]}</small><b>{e(u["dl"])}</b></span>' if u["dl"] else "")
        + (f'<span class="nx-card__flag">{t["featured"]}</span>' if u["feat"] else "")
        + '</button>'
        f'<div class="nx-card__icons"><button type="button" class="nx-ic" data-share="{i}" aria-label="Share">{SVG["share"]}</button>'
        f'<button type="button" class="nx-ic" data-fav="{e(u["ref"])}" aria-label="Favourite" aria-pressed="false">{SVG["heart"]}</button></div>'
        f'<div class="nx-card__body"><div class="nx-card__head"><span class="nx-logo nx-logo--sm" aria-hidden="true">{e(_initials(dev_src))}</span><div>'
        f'<p class="nx-card__loc">{e(u["cardLoc"])}</p>'
        f'<h3 class="nx-card__title"><button type="button" data-open="{i}">{e(u["t"])}</button></h3></div></div>'
        + (f'<ul class="nx-specs">{specs}</ul>' if specs else '<ul class="nx-specs nx-specs--none"></ul>')
        + f'<div class="nx-card__foot"><div><p class="nx-card__inst">{e(inst) if inst else "&nbsp;"}</p>{price}</div>'
        f'<div class="nx-card__cta"><a class="nx-round nx-round--call" href="tel:+{b.PHONE_INTL}" aria-label="{t["call"]}">{b.IC["phone"]}</a>'
        f'<a class="nx-round nx-round--wa" href="{e(u["wa"])}" target="_blank" rel="noopener" aria-label="{t["wa"]}">{b.IC["wa"]}</a>'
        '</div></div></div></article>'
    )


def build(b, lang, region, comp):
    t, IC, esc, money = b.t, b.IC, b.esc, b.money
    ar = lang == "ar"
    base = "../../"
    slug = comp["slug"]
    path = f"/{lang}/sahel/{slug}.html"
    other = "en" if ar else "ar"
    name = comp["name"][lang]
    name_en = comp["name"]["en"]
    area_name = (comp.get("areaName") or region["name"])[lang]
    dev = comp.get("developer") or {}
    dev_name = dev.get(lang) if dev else ""
    coast = "الساحل الشمالي" if ar else "North Coast-Sahel"
    egp = "جنيه" if ar else "EGP"

    L = {
        "compound": "كمبوند" if ar else "Compound",
        "by": "من" if ar else "by", "in": "في" if ar else "in",
        "devStart": "سعر البداية من المطور" if ar else "Developer Start Price",
        "reStart": "سعر البداية لإعادة البيع" if ar else "Resale Start Price",
        "call": "اتصل بنا" if ar else "Call Us", "wa": "واتساب" if ar else "Whatsapp",
        "explore": f"استكشف الوحدات في {name}" if ar else f"Explore Properties In {name}",
        "results": "نتيجة متاحة" if ar else "Results Available",
        "filter": "فلتر" if ar else "Filter", "sort": "ترتيب" if ar else "Sort By",
        "all": "الكل" if ar else "All", "dev": "بيع من المطور" if ar else "Developer Sale",
        "resale": "إعادة بيع" if ar else "Resale",
        "delivery": "الاستلام" if ar else "Delivery In", "ready": "استلام فوري" if ar else "Ready to move",
        "beds": "غرف" if ar else "Beds", "baths": "حمام" if ar else "Baths",
        "years": "سنين" if ar else "Years", "cash": "كاش" if ar else "Cash Payment",
        "empty": ("مفيش وحدات منشورة للكمبوند ده دلوقتي على الموقع — كلم إيليت وهنبعتلك كل الوحدات المتاحة والأسعار وأنظمة السداد."
                  if ar else "No units are published for this compound right now — contact Elite and we'll send every available unit, price and payment plan."),
        "noMatch": "مفيش وحدات مطابقة للفلتر" if ar else "No units match these filters",
        "type": "نوع الوحدة" if ar else "Property type", "bedsF": "عدد الغرف" if ar else "Bedrooms",
        "any": "الكل" if ar else "Any", "reset": "مسح" if ar else "Reset",
        "sDefault": "الافتراضي" if ar else "Default", "sLow": "السعر: من الأقل" if ar else "Price: low to high",
        "sHigh": "السعر: من الأعلى" if ar else "Price: high to low", "sArea": "المساحة: الأكبر" if ar else "Area: largest",
        "about": f"عن {name}" if ar else f"About {name}",
        "plan": "نظام السداد" if ar else "Payment Plan", "down": "مقدم" if ar else "Down Payment",
        "map": "خريطة الساحل" if ar else "Sahel Map", "project": "صفحة المشروع" if ar else "Project page",
        "km": "الكيلو" if ar else "KM",
        "ask": "السعر عند الطلب" if ar else "Price on request",
    }
    wa_general = (f"السلام عليكم، عايز أعرف الوحدات المتاحة والأسعار في {name} ({name_en}) - الكيلو {comp['km']}. (من موقع إيليت)"
                  if ar else f"Hello, I'd like the available units and prices in {name_en} - KM {comp['km']}. (From Elite's website)")

    def wa(msg):
        return f"https://wa.me/{b.PHONE_INTL}?text={quote(msg)}"

    def src(p):
        return p if p.startswith("http") else base + p

    logo = f'<span class="nx-logo" aria-hidden="true">{esc(_initials(dev.get("en") if dev else name_en))}</span>'

    units = comp["units"]
    comp_v = dict(comp)
    js_units = [sahel_unit(b, p, lang, comp_v, base) for p in units]
    dev_src = (dev.get("en") if dev else "") or name_en
    cards = "".join(nx_card(b, lang, u, i, comp["cover"], dev_src, base) for i, u in enumerate(js_units))

    n = len(units)
    dev_start = f'<b>{money(comp["devStart"])}</b> <small>{egp}</small>' if comp["devStart"] else "<b>-</b>"
    re_start = f'<b>{money(comp["resaleStart"])}</b> <small>{egp}</small>' if comp["resaleStart"] else "<b>-</b>"
    n_dev = sum(1 for u in js_units if u["sale"] == "developer")
    n_re = sum(1 for u in js_units if u["sale"] == "resale")
    types = sorted({u["type"] for u in js_units}, key=lambda x: [u["type"] for u in js_units].index(x))
    type_opts = "".join(f'<option value="{ty}">{_type_label(b, lang, ty)}</option>' for ty in types)

    gal = [src(g) for g in comp.get("gallery") or []][:5]
    gallery_html = ""
    if len(gal) >= 3:
        tiles = "".join(f'<figure class="nx-gal__t{" nx-gal__t--main" if k == 0 else ""}"><img src="{esc(g)}" alt="{esc(name)}" loading="{"eager" if k == 0 else "lazy"}" referrerpolicy="no-referrer" data-fallback="{base + comp["cover"]}"></figure>'
                        for k, g in enumerate(gal))
        gallery_html = f'<div class="nx-gal nx-gal--{len(gal)}">{tiles}</div>'

    about = (comp.get("about") or {}).get(lang) if comp.get("about") else ""
    plan_html = ""
    if comp.get("plan"):
        pl = comp["plan"]
        plan_html = f"""<div class="nx-plan"><h3>{L['plan']}</h3><div class="nx-plan__row">
          <span><b>{pl['down']}%</b> {L['down']}</span><span><b>{pl['years']}</b> {L['years']}</span></div></div>"""

    project_link = (f'<a class="nx-link" href="{base}{lang}/projects/{comp["project"]}.html">{L["project"]}{IC["arrow"]}</a>'
                    if comp.get("project") else "")

    title = (f"وحدات للبيع في {name} الساحل الشمالي — الأسعار وأنظمة السداد | إيليت للتسويق العقاري" if ar
             else f"{name} North Coast — units for sale, prices & payment plans | Elite Real Estate")
    desc_meta = (f"{n} وحدة للبيع في {name} عند الكيلو {comp['km']} ({region['name']['ar']})، بالأسعار وأنظمة السداد. احجز مع إيليت."
                 if ar else f"{n} units for sale in {name_en} at KM {comp['km']} ({region['name']['en']}), with prices and payment plans. Book with Elite.")
    ld = [{"@context": "https://schema.org", "@type": "ItemList", "name": title, "numberOfItems": n,
           "itemListElement": [{"@type": "ListItem", "position": k + 1, "name": x["t"]} for k, x in enumerate(js_units)]}]

    html = b.head(lang, title, desc_meta, path, base, ld)
    html += b.header(lang, base, "sahel", f"{base}{other}/sahel/{slug}.html")
    html += f"""<main class="nx">
<div class="nx-top"></div>
<div class="wrap">
  <nav class="breadcrumbs nx-crumbs"><a href="{base}{lang}/index.html">{t(lang,'breadcrumb.home')}</a> <span>/</span> <a href="{base}{lang}/sahel-map.html">{L['map']}</a> <span>/</span> <a href="{base}{lang}/sahel-map.html#r-{region['id']}">{region['name'][lang]}</a> <span>/</span> <span>{esc(name)}</span></nav>
  {gallery_html}
  <section class="nx-hd">
    {logo}
    <div class="nx-hd__main">
      <div class="nx-hd__title"><h1>{esc(name)} {L['in']} {esc(area_name)}{f' {L["by"]} {esc(dev_name)}' if dev_name else ''}</h1><span class="nx-chip">{L['compound']}</span>
        <span class="nx-chip nx-chip--km">{L['km']} {comp['km']}</span></div>
      <div class="nx-hd__prices">
        <div><p>{L['devStart']}</p><p class="nx-hd__val" data-dev-start>{dev_start}</p></div>
        <div><p>{L['reStart']}</p><p class="nx-hd__val" data-re-start>{re_start}</p></div>
      </div>
    </div>
    <div class="nx-hd__cta">
      <a class="nx-btn nx-btn--call" href="tel:+{b.PHONE_INTL}">{IC['phone']}<span>{L['call']}</span></a>
      <a class="nx-btn nx-btn--wa" href="{wa(wa_general)}" target="_blank" rel="noopener">{IC['wa']}<span>{L['wa']}</span></a>
    </div>
  </section>

  <section class="nx-list" aria-labelledby="nx-explore">
    <div class="nx-list__bar">
      <div><h2 id="nx-explore">{esc(L['explore'])}</h2><p class="nx-count"><span data-count>{n}</span> {L['results']}</p></div>
      <div class="nx-tools">
        <button type="button" class="nx-tool nx-tool--primary" data-filter-toggle aria-expanded="false">{SVG['filter']}<span>{L['filter']}</span></button>
        <label class="nx-tool nx-tool--sort">{SVG['sort']}<select data-sort aria-label="{L['sort']}">
          <option value="">{L['sort']}</option><option value="low">{L['sLow']}</option><option value="high">{L['sHigh']}</option><option value="area">{L['sArea']}</option></select></label>
      </div>
    </div>
    <div class="nx-filters" hidden>
      <label>{L['type']}<select data-f-type><option value="">{L['any']}</option>{type_opts}</select></label>
      <label>{L['bedsF']}<select data-f-beds><option value="">{L['any']}</option><option value="1">1</option><option value="2">2</option><option value="3">3</option><option value="4">4</option><option value="5">5+</option></select></label>
      <button type="button" class="nx-reset" data-f-reset>{L['reset']}</button>
    </div>
    <div class="nx-tabs" role="tablist">
      <button type="button" role="tab" aria-selected="true" data-tab="">{L['all']} <small>({n})</small></button>
      <button type="button" role="tab" aria-selected="false" data-tab="developer">{L['dev']} <small>({n_dev})</small></button>
      <button type="button" role="tab" aria-selected="false" data-tab="resale">{L['resale']} <small>({n_re})</small></button>
    </div>
    <div class="nx-grid">{cards}
    </div>
    <p class="nx-empty" {'hidden' if n else ''}>{L['empty'] if not n else L['noMatch']}</p>
    <p class="nx-empty-cta" {'hidden' if n else ''}><a class="nx-btn nx-btn--wa" href="{wa(wa_general)}" target="_blank" rel="noopener">{IC["wa"]}<span>{L["wa"]}</span></a> <a class="nx-btn nx-btn--call" href="tel:+{b.PHONE_INTL}">{IC["phone"]}<span dir="ltr">{b.PHONE_DISPLAY}</span></a></p>
  </section>

  {f'<section class="nx-about"><h2>{esc(L["about"])}</h2><p>{esc(about)}</p>{plan_html}{project_link}</section>' if about or project_link else ''}
</div>

<dialog class="nx-unit" aria-labelledby="nxu-title">
  <button type="button" class="nx-unit__close" aria-label="Close">&times;</button>
  <div class="nx-unit__gal">
    <img class="nx-unit__img" alt="" referrerpolicy="no-referrer">
    <button type="button" class="nx-unit__nav nx-unit__nav--prev" aria-label="Previous">{SVG['chev']}</button>
    <button type="button" class="nx-unit__nav nx-unit__nav--next" aria-label="Next">{SVG['chev']}</button>
    <span class="nx-unit__counter"></span>
  </div>
  <div class="nx-unit__thumbs"></div>
  <div class="nx-unit__body">
    <div class="nx-unit__top">
      <div>
        <span class="nx-chip">{"وحدة" if ar else "Property"}</span>
        <h2 id="nxu-title" class="nx-unit__title"></h2>
        <p class="nx-unit__loc"></p>
      </div>
      <div class="nx-unit__pricebox">
        <p class="nx-unit__price"></p>
        <div class="nx-unit__cta">
          <a class="nx-btn nx-btn--call" href="tel:+{b.PHONE_INTL}">{IC['phone']}<span>{L['call']}</span></a>
          <a class="nx-btn nx-btn--wa nx-unit__wa" target="_blank" rel="noopener">{IC['wa']}<span>{L['wa']}</span></a>
        </div>
      </div>
    </div>
    <dl class="nx-unit__facts"></dl>
    <div class="nx-unit__am"></div>
    <div class="nx-unit__plans"></div>
    <div class="nx-unit__about"></div>
  </div>
</dialog>
</main>
"""
    labels = {
        "egp": egp, "from": "السعر يبدأ من" if ar else "Prices Start From", "max": "أعلى سعر" if ar else "Max Price",
        "price": "السعر" if ar else "Price", "ref": "كود الوحدة" if ar else "Reference No.",
        "beds": "غرف النوم" if ar else "Bedrooms", "baths": "الحمامات" if ar else "Bathrooms",
        "dl": "الاستلام" if ar else "Delivery In", "cmp": "الكمبوند" if ar else "Compound",
        "sale": "نوع البيع" if ar else "Sale Type", "fin": "التشطيب" if ar else "Finishing",
        "dev": L["dev"], "resale": L["resale"], "am": "المميزات" if ar else "Amenities",
        "plans": "أنظمة السداد" if ar else "Payment Plans", "down": L["down"], "years": L["years"],
        "cash": L["cash"], "about": "عن الوحدة" if ar else "About the unit", "plan": "خطة" if ar else "Plan",
        "copied": "تم نسخ الرابط" if ar else "Link copied", "ask": L["ask"],
    }
    ctx = {"slug": slug, "lang": lang, "base": base, "devInitials": dev_src, "emptyText": L["empty"], "noMatchText": L["noMatch"]}
    js = (f'<script src="{base}data/properties.js"></script>\n<script src="{base}data/compounds.js"></script>\n'
          f'<script src="{base}assets/js/cards.js?v=2"></script>\n'
          "<script>window.NX_CTX=" + json.dumps(ctx, ensure_ascii=False) + ";window.NX_UNITS=" + json.dumps(js_units, ensure_ascii=False)
          + ";window.NX_L=" + json.dumps(labels, ensure_ascii=False) + ";</script>\n"
          f'<script src="{base}assets/js/sahel-compound.js?v=2"></script>')
    html += b.footer(lang, base) + b.whatsapp_widget(lang, base) + b.scripts(base, js)
    b.write(f"{lang}/sahel/{slug}.html", html)
