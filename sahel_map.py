# -*- coding: utf-8 -*-
"""
Elite Real Estate — North Coast (Sahel) map page.

Reads data/sahel_map.json (regions -> compounds with KM markers, ordered west -> east,
KM 275 down to KM 92) and joins it with data/properties.json and data/projects.json to
show, for every compound: its KM, a photo, Elite's starting price, how many units Elite
has listed, and one-tap booking on Elite's WhatsApp / phone.

Every compound links to its own units page (ar|en/sahel/<slug>.html, built by sahel_compounds.py).
Called from build.py:  sahel_map.build(b, lang)   (b = the build module)
Edit the compound list in data/sahel_map.json, then run  python3 build.py
"""

import json
import math
import os
import re
from urllib.parse import quote

import sahel_compounds

MIN_KM, MAX_KM = 90, 277


def _load(root, name):
    with open(os.path.join(root, "data", name), encoding="utf-8") as f:
        return json.load(f)


def _plain(alias):
    """Turn a match pattern into a plain keyword usable by the properties search box."""
    s = re.sub(r"\\b|\(\?.*?\)|\^|\$|\[.*?\]|\\d|\*|\+|\?", "", alias)
    return s.strip()


def _compile(b):
    """Regions -> compounds (with slug, normalised units, prices, photo) — shared with the compound pages."""
    return sahel_compounds.compile_compounds(b)


# --------------------------------------------------------------------------
# Poster geometry (viewBox is 1000 wide; everything horizontal is in %)
# --------------------------------------------------------------------------
PAD_TOP, PAD_BOTTOM = 110, 90
ROW_H, REGION_H = 58, 118


def _coast_x(y):
    return 482 + 11 * math.sin(y / 190.0) + 6 * math.sin(y / 61.0)


def _road_x(y):
    return 448 + 9 * math.sin(y / 230.0 + 1.3)


def _poster_svg(height):
    H = height
    step = 30
    ys = list(range(0, H + step, step))
    coast = [(_coast_x(y), y) for y in ys]
    band2 = [(700 + 22 * math.sin(y / 260.0 + .7) + 8 * math.sin(y / 83.0), y) for y in ys]
    band3 = [(905 + 16 * math.sin(y / 300.0 + 2.1), y) for y in ys]

    def poly(edge):
        pts = " ".join(f"{x:.1f},{y}" for x, y in edge)
        return f"M1000,0 L{edge[0][0]:.1f},0 L{pts} L{edge[-1][0]:.1f},{H} L1000,{H} Z"

    def line(pts):
        return "M" + " L".join(f"{x:.1f},{y}" for x, y in pts)

    road = [(_road_x(y), y) for y in ys]
    road2 = [(28 + 26 * math.sin(y / 340.0) + 10 * math.sin(y / 97.0), y) for y in ys]
    return f"""<svg class="smap__bg" viewBox="0 0 1000 {H}" preserveAspectRatio="none" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">
  <rect width="1000" height="{H}" fill="#eadfc9"/>
  <path d="{poly(coast)}" fill="#0f2c44"/>
  <path d="{poly(band2)}" fill="#1d4b66"/>
  <path d="{poly(band3)}" fill="#2d6682"/>
  <path d="{line([(x + 7, y) for x, y in coast])}" fill="none" stroke="#1a3f58" stroke-width="10" opacity=".55" vector-effect="non-scaling-stroke"/>
  <path d="{line(road)}" fill="none" stroke="#b8a27c" stroke-width="7" stroke-linecap="round" vector-effect="non-scaling-stroke"/>
  <path d="{line(road2)}" fill="none" stroke="#c7b28c" stroke-width="7" stroke-linecap="round" vector-effect="non-scaling-stroke"/>
</svg>"""


HAND = ('<svg class="smap-hand" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" '
        'stroke-linecap="round" stroke-linejoin="round"><path d="M9 11V4.5a1.5 1.5 0 0 1 3 0V10"/>'
        '<path d="M12 9.5a1.5 1.5 0 0 1 3 0V11"/><path d="M15 10.5a1.5 1.5 0 0 1 3 0V12"/>'
        '<path d="M18 11.5a1.5 1.5 0 0 1 3 0V15a7 7 0 0 1-7 7h-1.2a6 6 0 0 1-4.6-2.2L4.3 16a1.6 1.6 0 0 1 2.4-2.1L9 16V11"/></svg>')
PIN = ('<svg class="smap-pin" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 22s7-6 7-12a7 7 0 1 0-14 0c0 6 7 12 7 12z"/>'
       '<circle cx="12" cy="10" r="2.6" fill="#fff"/></svg>')


def build(b, lang):
    t, IC, esc, money = b.t, b.IC, b.esc, b.money
    data, regions = _compile(b)
    base = "../"
    path = f"/{lang}/sahel-map.html"
    other = "en" if lang == "ar" else "ar"
    ar = lang == "ar"
    total = sum(len(r["compounds"]) for r in regions)

    title = ("خريطة الساحل الشمالي 2026 بالكيلو والأسعار | إيليت للتسويق العقاري" if ar
             else "North Coast (Sahel) Map 2026 — every compound by KM, with prices | Elite Real Estate")
    desc = (f"خريطة الساحل الشمالي 2026: {total} كمبوند من الكيلو 92 للكيلو 275 — سيدي حنيش، رأس الحكمة، الضبعة، غزالة باي، سيدي عبد الرحمن والعلمين الجديدة، بالأسعار وأرقام حجز إيليت."
            if ar else
            f"North Coast map 2026: {total} compounds from KM 92 to KM 275 — Sidi Heneish, Ras El Hekma, Al Dabaa, Ghazala Bay, Sidi Abdelrahman and New Alamein, with prices and Elite booking lines.")

    def wa(msg):
        return f"https://wa.me/{b.PHONE_INTL}?text={quote(msg)}"

    L = {
        "map": "خريطة الساحل" if ar else "SAHEL MAP",
        "hint": ("دوس على اسم أي كمبوند تشوف السعر والوحدات المتاحة وتحجز مع إيليت"
                 if ar else "Click on any compound name to see prices, available units and book with Elite"),
        "from": "يبدأ من" if ar else "From",
        "ask": "السعر عند الطلب" if ar else "Price on request",
        "units": "وحدة متاحة" if ar else "units listed",
        "unit1": "وحدة متاحة" if ar else "unit listed",
        "details": "كل الوحدات والأسعار" if ar else "All units & prices",
        "project": "صفحة المشروع" if ar else "Project page",
        "book": "احجز على واتساب" if ar else "Book on WhatsApp",
        "call": "اتصل بينا" if ar else "Call us",
        "print": "حمّل الخريطة PDF" if ar else "Download map (PDF)",
        "km": "كم" if ar else "km",
        "kmLong": "الكيلو" if ar else "KM",
        "close": "إغلاق" if ar else "Close",
        "ctaTitle": "عايز تحجز في الساحل؟ كلمنا دلوقتي" if ar else "Ready to book on the North Coast? Talk to us now",
        "ctaText": ("مستشارين إيليت هيبعتولك أحدث الأسعار وأنظمة السداد والوحدات المتاحة في أي كمبوند على الخريطة."
                    if ar else
                    "Elite advisors will send you the latest prices, payment plans and available units for any compound on this map."),
        "disclaimer": ("الأسعار المعروضة هي أقل سعر بيع للوحدات المسجلة عند إيليت أو سعر البداية المعلن من المطور، وقابلة للتغيير. "
                       "مواقع الكيلو تقريبية. تأكد من السعر والتوافر مع مستشار إيليت قبل الحجز.")
                      if ar else
                      ("Prices shown are the lowest sale price among units listed with Elite, or the developer's published starting price, and are subject to change. "
                       "KM positions are approximate. Please confirm price and availability with an Elite advisor before booking."),
    }
    general_msg = ("السلام عليكم، شفت خريطة الساحل الشمالي على موقع إيليت وعايز أحجز / أعرف الأسعار."
                   if ar else "Hello, I saw the North Coast map on Elite's website and would like to book / get prices.")

    rows, items = "", []
    height = PAD_TOP
    for r in regions:
        lo, hi = r["range"]
        rng = (f'<bdi dir="ltr">{lo}km-{hi}km</bdi>')
        rows += f"""
    <div class="smap-region" id="r-{r['id']}" style="height:{REGION_H}px">
      <span class="smap-region__rule"></span>
      <a class="smap-region__label" href="#r-{r['id']}">{HAND}<span>{r['name'][lang]}</span></a>
      <span class="smap-region__range">{rng}</span>
      <img class="smap-region__logo" src="{base}assets/img/brand/logo-footer-white.png" alt="{t(lang,'brand')}" width="514" height="160" loading="lazy">
    </div>"""
        height += REGION_H
        for c in r["compounds"]:
            i = len(items)
            nm = c["name"][lang]
            msg = (f"السلام عليكم، عايز أحجز / أعرف أسعار {nm} ({c['name']['en']}) - الكيلو {c['km']} - {r['name']['ar']}. (من خريطة الساحل على موقع إيليت)"
                   if ar else
                   f"Hello, I'd like to book / get prices for {nm} - KM {c['km']}, {r['name']['en']}. (From the Sahel map on Elite's website)")
            link, link_label = f"{base}{lang}/sahel/{c['slug']}.html", L["details"]
            price_txt = f'{t(lang,"common.egp")} {money(c["price"])}' if c["price"] else ""
            nu = sum(1 for u in c["units"] if not sahel_compounds.is_ask(u) or (u.get("area") or 0) > 0 or (u.get("beds") or 0) > 0)
            units_txt = (f'{nu} {L["units"] if (ar or nu > 1) else L["unit1"]}' if nu else "")
            items.append({
                "slug": c["slug"], "cover": base + c["cover"],
                "name": nm, "alt": c["name"]["en" if ar else "ar"], "km": c["km"], "region": r["name"][lang],
                "price": price_txt, "units": units_txt,
                "photo": (c["photo"] if c["photo"].startswith("http") else base + c["photo"]) if c["photo"] else "", "wa": wa(msg),
                "link": link, "linkLabel": link_label,
            })
            if c["photo"]:
                badge = f'<img src="{c["photo"] if c["photo"].startswith("http") else base + c["photo"]}" alt="" loading="lazy" width="80" height="80" referrerpolicy="no-referrer" data-fallback="{base + c["cover"]}">'
            else:
                initials = "".join(w[0] for w in c["name"]["en"].replace("-", " ").split()[:2]).upper()
                badge = f'<span>{esc(initials)}</span>'
            sub = (f'<small class="smap-row__price">{L["from"]} {price_txt}</small>' if price_txt
                   else f'<small class="smap-row__price is-ask">{L["ask"]}</small>')
            rows += f"""
    <div class="smap-row" data-slug="{c['slug']}" style="height:{ROW_H}px">
      <span class="smap-row__km"><b>{c['km']}</b>{L['km']}{PIN}</span>
      <span class="smap-row__line"></span>
      <span class="smap-row__badge">{badge}</span>
      <button type="button" class="smap-row__name" data-i="{i}" dir="{t(lang,'dir')}"><span dir="auto">{esc(nm)}</span>{sub}</button>
    </div>"""
            height += ROW_H
    height += PAD_BOTTOM

    ld = [{
        "@context": "https://schema.org", "@type": "ItemList", "name": title, "numberOfItems": total,
        "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": f'{x["name"]} — KM {x["km"]}'}
                            for i, x in enumerate(items)],
    }]

    html = b.head(lang, title, desc, path, base, ld)
    html += b.header(lang, base, "sahel", f"{base}{other}/sahel-map.html")
    html += f"""<main class="sahel">
<div class="smap-top"></div>
<section class="smap" dir="ltr" aria-label="{L['map']} 2026">
  {_poster_svg(height)}
  <img class="smap__wm smap__wm--1" src="{base}assets/img/brand/logo-mark-white.png" alt="" aria-hidden="true">
  <img class="smap__wm smap__wm--2" src="{base}assets/img/brand/logo-mark-white.png" alt="" aria-hidden="true">
  <img class="smap__wm smap__wm--3" src="{base}assets/img/brand/logo-mark-white.png" alt="" aria-hidden="true">

  <div class="smap-intro" dir="{t(lang,'dir')}">
    <img class="smap-intro__logo" src="{base}assets/img/brand/logo-footer.png" alt="{t(lang,'brand')}" width="437" height="136">
    <h1 class="smap-intro__title">{L['map']}<em>2026</em></h1>
    <p class="smap-intro__hint">{HAND}<span>{L['hint']}</span></p>
    <div class="smap-intro__actions">
      <a class="btn btn--wa" href="{wa(general_msg)}" target="_blank" rel="noopener">{IC['wa']}{L['book']}</a>
      <a class="smap-intro__tel" href="tel:+{b.PHONE_INTL}">{IC['phone']}<span dir="ltr">{b.PHONE_DISPLAY}</span></a>
      <button type="button" class="smap-intro__print" data-print>{L['print']}</button>
    </div>
  </div>

  <div class="smap__rows" style="padding-top:{PAD_TOP}px;padding-bottom:{PAD_BOTTOM}px">{rows}
  </div>
</section>

<section class="sahel-cta">
  <div class="wrap sahel-cta__inner">
    <div>
      <img class="sahel-cta__logo" src="{base}assets/img/brand/logo-footer-white.png" alt="{t(lang,'brand')}" width="514" height="160" loading="lazy">
      <h2>{L['ctaTitle']}</h2>
      <p>{L['ctaText']}</p>
    </div>
    <div class="sahel-cta__lines">
      <a class="btn btn--wa btn--block" href="{wa(general_msg)}" target="_blank" rel="noopener">{IC['wa']}{L['book']} · <span dir="ltr">{b.PHONE_DISPLAY}</span></a>
      <a class="btn btn--ghost btn--block" href="tel:+{b.PHONE_INTL}">{IC['phone']}{L['call']} · <span dir="ltr">{b.PHONE_LOCAL}</span></a>
      <a class="btn btn--ghost btn--block" href="mailto:{b.EMAIL}">{IC['mail']}{b.EMAIL}</a>
    </div>
  </div>
</section>
<div class="wrap"><p class="disclaimer sahel-disclaimer">{L['disclaimer']}</p></div>

<dialog class="smap-dialog" aria-labelledby="smap-d-name">
  <button type="button" class="smap-dialog__close" aria-label="{L['close']}">&times;</button>
  <div class="smap-dialog__media"></div>
  <div class="smap-dialog__body">
    <p class="smap-dialog__meta"></p>
    <h3 id="smap-d-name" class="smap-dialog__name"></h3>
    <p class="smap-dialog__alt"></p>
    <p class="smap-dialog__price"></p>
    <p class="smap-dialog__units"></p>
    <div class="smap-dialog__actions">
      <a class="btn btn--wa btn--block smap-dialog__wa" target="_blank" rel="noopener">{IC['wa']}{L['book']}</a>
      <a class="btn btn--outline btn--block" href="tel:+{b.PHONE_INTL}">{IC['phone']}{L['call']} · <span dir="ltr">{b.PHONE_LOCAL}</span></a>
      <a class="smap-dialog__link"></a>
    </div>
  </div>
</dialog>
</main>
"""
    labels = {"from": L["from"], "ask": L["ask"], "km": L["kmLong"], "arrow": IC["arrow"], "base": base,
              "egp": t(lang, "common.egp"), "units": L["units"], "unit1": L["unit1"], "ar": ar}
    js = (f'<script src="{base}data/properties.js"></script>\n<script src="{base}data/compounds.js"></script>\n'
          f'<script src="{base}assets/js/cards.js?v=2"></script>\n'
          "<script>window.SAHEL_MAP=" + json.dumps(items, ensure_ascii=False) + ";window.SAHEL_L="
          + json.dumps(labels, ensure_ascii=False) + ";</script>\n"
          f'<script src="{base}assets/js/sahel-map.js?v=2"></script>')
    html += b.footer(lang, base) + b.whatsapp_widget(lang, base) + b.scripts(base, js)
    b.write(f"{lang}/sahel-map.html", html)

    # one units page per compound
    for r in regions:
        for c in r["compounds"]:
            sahel_compounds.build(b, lang, r, c)
