#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Elite Real Estate — static site generator.

Reads:   data/projects.json, data/properties.json, data/i18n.json
Writes:  ar/*.html, en/*.html, ar|en/projects/<slug>.html, sitemap.xml,
         robots.txt, data/*.js mirrors, index.html (language router)

Run after editing any JSON file:   python3 build.py
"""

import json
import os
import shutil
import sys
from datetime import date

import artwork

import sahel_compounds
import sahel_map  # North Coast map + compound units pages (footer link only)

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE_URL = "https://www.eliterealestateco.com"
PHONE_INTL = "201111788812"
PHONE_LOCAL = "01111788812"
PHONE_DISPLAY = "+20 111 178 8812"
EMAIL = "info@eliterealestateco.com"
LANGS = ["ar", "en"]
TODAY = date.today().isoformat()


def load(name):
    with open(os.path.join(ROOT, "data", name), encoding="utf-8") as f:
        return json.load(f)


I18N = load("i18n.json")
PROJECTS_ALL = sorted(load("projects.json"), key=lambda p: p.get("order", 99))
PUBLIC_PROJECT_SLUGS = {"the-one-smouha", "ajaza-new-alamein", "creeks-alexandria", "ogami-ras-el-hekma"}
PROJECTS = [p for p in PROJECTS_ALL if p.get("slug") in PUBLIC_PROJECT_SLUGS]
PROPERTIES = load("properties.json")

CITIES = ["alexandria", "north-coast", "cairo", "giza", "other"]
TYPES = ["apartment", "villa", "chalet", "townhouse", "twinhouse", "duplex", "penthouse", "office", "retail", "medical", "studio"]

# --------------------------------------------------------------------------
# icons
# --------------------------------------------------------------------------
IC = {
    "pin": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 21s7-5.6 7-11a7 7 0 1 0-14 0c0 5.4 7 11 7 11z"/><circle cx="12" cy="10" r="2.5"/></svg>',
    "arrow": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M5 12h14m-6-6 6 6-6 6"/></svg>',
    "arrowLeft": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M19 12H5m6 6-6-6 6-6"/></svg>',
    "area": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 9V4h5M20 15v5h-5M20 9V4h-5M4 15v5h5"/></svg>',
    "bed": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M3 18v-6h18v6M3 12V7m18 5V9a2 2 0 0 0-2-2h-5v5"/><circle cx="7.5" cy="9.5" r="1.8"/></svg>',
    "bath": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 12h16v3a4 4 0 0 1-4 4H8a4 4 0 0 1-4-4v-3zM7 12V6a2 2 0 0 1 4 0"/></svg>',
    "phone": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a1 1 0 0 1-1 1A16 16 0 0 1 4 5a1 1 0 0 1 1-1z"/></svg>',
    "mail": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>',
    "clock": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
    "search": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>',
    "building": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 21V6l7-3v18M11 21h9V10l-9-3"/><path d="M14 12h3M14 16h3M7 10h1M7 14h1"/></svg>',
    "tag": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M3 12V4h8l9 9-8 8-9-9z"/><circle cx="7.5" cy="7.5" r="1.2"/></svg>',
    "expand": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 9V4h5M20 15v5h-5M20 9V4h-5M4 15v5h5"/></svg>',
    "diamond": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2"><path d="m12 3 6 6-6 12L6 9z"/><path d="M6 9h12"/></svg>',
    "advisor": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2"><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/></svg>',
    "shield": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2"><path d="M12 3l8 3v6c0 5-3.4 8.4-8 9-4.6-.6-8-4-8-9V6z"/><path d="m9 12 2 2 4-4"/></svg>',
    "support": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2"><path d="M4 13v-2a8 8 0 0 1 16 0v2"/><rect x="2.5" y="13" width="4" height="6" rx="1.5"/><rect x="17.5" y="13" width="4" height="6" rx="1.5"/><path d="M20 19a4 4 0 0 1-4 3h-2"/></svg>',
    "check": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="m4 12 5 5L20 6"/></svg>',
    "plus": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M12 5v14M5 12h14"/></svg>',
    "wa": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M17.5 14.4c-.3-.2-1.7-.8-2-.9-.3-.1-.5-.2-.7.2-.2.3-.7.9-.9 1.1-.2.2-.3.2-.6.1-1.7-.9-2.9-1.6-4-3.5-.3-.5.3-.5.8-1.5.1-.2 0-.4 0-.5 0-.2-.7-1.6-.9-2.2-.2-.6-.5-.5-.7-.5h-.6c-.2 0-.5.1-.8.4-.3.3-1 1-1 2.5s1.1 2.9 1.2 3.1c.2.2 2.2 3.3 5.3 4.6 2 .8 2.7.9 3.7.8.6-.1 1.7-.7 2-1.4.2-.7.2-1.2.2-1.4-.1-.1-.3-.2-.6-.4z"/><path d="M12 2a10 10 0 0 0-8.6 15L2 22l5.2-1.4A10 10 0 1 0 12 2zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3.1.8.8-3-.2-.3A8.2 8.2 0 1 1 12 20.2z"/></svg>',
    "facebook": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M13.5 22v-8h2.7l.4-3h-3.1V9c0-.9.3-1.5 1.6-1.5H17V4.8c-.3 0-1.2-.1-2.3-.1-2.4 0-4 1.4-4 4.1V11H8v3h2.7v8z"/></svg>',
    "instagram": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="3.6"/><circle cx="17.2" cy="6.8" r="1"/></svg>',
    "linkedin": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M6.9 8.5H4V20h2.9zM5.4 3.9a1.7 1.7 0 1 0 0 3.4 1.7 1.7 0 0 0 0-3.4zM20 13.6c0-3-1.6-4.4-3.8-4.4-1.7 0-2.5.9-2.9 1.6V8.5H10.4V20h2.9v-6.2c0-1.4.6-2.2 1.8-2.2s1.9.8 1.9 2.2V20H20z"/></svg>',
    "youtube": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M22 12s0-3.2-.4-4.7a2.5 2.5 0 0 0-1.8-1.8C18.2 5 12 5 12 5s-6.2 0-7.8.5A2.5 2.5 0 0 0 2.4 7.3C2 8.8 2 12 2 12s0 3.2.4 4.7a2.5 2.5 0 0 0 1.8 1.8C5.8 19 12 19 12 19s6.2 0 7.8-.5a2.5 2.5 0 0 0 1.8-1.8C22 15.2 22 12 22 12zM10 15V9l5.2 3z"/></svg>',
}


def t(lang, key):
    return I18N[lang].get(key, key)


def money(n):
    return "{:,}".format(int(n))


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


# --------------------------------------------------------------------------
# placeholder imagery (replace the SVG files with real photos when available)
# --------------------------------------------------------------------------
PALETTES = [
    ("#0d2438", "#1d5670", "#57a0a8"),
    ("#12233a", "#27506b", "#7fb0b8"),
    ("#0b2030", "#245665", "#9ec7c1"),
    ("#101f36", "#2b4c6f", "#6f97b5"),
    ("#0e2a35", "#2a6a6a", "#a8c9b6"),
    ("#141d31", "#37506e", "#8ea2bd"),
]


def placeholder_svg(label, sub, seed, w=1200, h=800):
    label = esc(label)
    sub = esc(sub)
    c1, c2, c3 = PALETTES[seed % len(PALETTES)]
    horizon = int(h * 0.62)
    caption = ""
    if label:
        caption = (
            f'<text x="{int(w/2)}" y="{int(h*0.5)}" fill="#ffffff" fill-opacity="0.9" '
            f'font-family="Georgia, serif" font-size="{int(h*0.075)}" text-anchor="middle" letter-spacing="2">{label}</text>'
            f'<text x="{int(w/2)}" y="{int(h*0.5)+int(h*0.06)}" fill="#ffffff" fill-opacity="0.55" '
            f'font-family="Helvetica, Arial, sans-serif" font-size="{int(h*0.03)}" text-anchor="middle" letter-spacing="6">{sub}</text>'
        )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{label}">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0.3" y2="1">
      <stop offset="0%" stop-color="{c2}"/><stop offset="60%" stop-color="{c1}"/><stop offset="100%" stop-color="{c1}"/>
    </linearGradient>
    <linearGradient id="sea" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{c3}" stop-opacity="0.55"/><stop offset="100%" stop-color="{c1}" stop-opacity="0.9"/>
    </linearGradient>
  </defs>
  <rect width="{w}" height="{h}" fill="url(#sky)"/>
  <circle cx="{int(w*0.76)}" cy="{int(h*0.3)}" r="{int(h*0.12)}" fill="{c3}" opacity="0.18"/>
  <rect y="{horizon}" width="{w}" height="{h-horizon}" fill="url(#sea)"/>
  <g fill="{c1}" opacity="0.75">
    <rect x="{int(w*0.05)}" y="{horizon-190}" width="120" height="190"/>
    <rect x="{int(w*0.05)+140}" y="{horizon-260}" width="90" height="260"/>
    <rect x="{int(w*0.05)+250}" y="{horizon-150}" width="150" height="150"/>
    <rect x="{int(w*0.62)}" y="{horizon-215}" width="110" height="215"/>
    <rect x="{int(w*0.62)+130}" y="{horizon-140}" width="170" height="140"/>
  </g>
  <g stroke="{c3}" stroke-opacity="0.35" stroke-width="2">
    <path d="M0 {horizon+50} H{w}"/><path d="M0 {horizon+110} H{w}"/><path d="M0 {horizon+180} H{w}"/>
  </g>
  {caption}
</svg>"""


def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)


PHOTO_EXTS = [".jpg", ".jpeg", ".webp", ".png"]


def img(path):
    """Prefer a real photo dropped next to the generated artwork."""
    stem = os.path.splitext(path)[0]
    for ext in PHOTO_EXTS:
        if os.path.exists(os.path.join(ROOT, stem + ext)):
            return stem + ext
    return path


def build_images():
    """Generate artwork for anything that has no real photo yet."""
    for i, p in enumerate(PROJECTS):
        kinds = artwork.kinds_for(p.get("types", []))
        for n in range(1, 5):
            rel = f"assets/img/projects/{p['slug']}-{n}.svg"
            if img(rel) != rel or os.path.exists(os.path.join(ROOT, rel)):
                continue
            write(rel, artwork.scene_svg(kinds[n - 1], p["slug"] + str(n)))
    for pr in PROPERTIES:
        rel = pr["image"]
        if not rel or rel.startswith(("http", "data:")) or img(rel) != rel or os.path.exists(os.path.join(ROOT, rel)):
            continue
        kinds = artwork.KIND_BY_TYPE.get(pr["type"], ["coastal"])
        write(rel, artwork.scene_svg(kinds[0], pr["id"], 1200, 900))
    for name in ["hero", "cta", "page", "about"]:
        rel = f"assets/img/brand/{name}.svg"
        if img(rel) != rel or os.path.exists(os.path.join(ROOT, rel)):
            continue
        write(rel, artwork.scene_svg("coastal", "brand-" + name, 1920, 1080))


def build_image_manifest():
    """List every image slot so real photos can be dropped in by name."""
    lines = ["# قائمة الصور المطلوبة\n",
             "حطي الصورة بنفس الاسم وامتداد `.jpg` أو `.webp` في نفس الفولدر، ",
             "وشغّلي `python3 build.py` — الموقع هيستخدم الصورة الحقيقية تلقائيًا بدل الرسم المؤقت.\n",
             "\n| المشروع / الوحدة | مسار الصورة | الحالة |\n|---|---|---|\n"]
    for p in PROJECTS:
        for n in range(1, 5):
            rel = f"assets/img/projects/{p['slug']}-{n}.svg"
            real = img(rel)
            state = "✅ صورة حقيقية" if real != rel else "⬜ مؤقتة"
            lines.append(f"| {p['name']['ar']} ({n}) | `{os.path.splitext(rel)[0]}.jpg` | {state} |\n")
    for pr in PROPERTIES:
        if not pr["image"] or pr["image"].startswith(("http", "data:")):
            continue
        real = img(pr["image"])
        state = "✅ صورة حقيقية" if real != pr["image"] and not real.endswith(".svg") else ("⬜ مؤقتة" if real.endswith(".svg") else "✅ صورة")
        lines.append(f"| {pr['title']['ar']} | `{os.path.splitext(pr['image'])[0]}.jpg` | {state} |\n")
    for name in ["hero", "cta", "page", "about"]:
        rel = f"assets/img/brand/{name}.svg"
        state = "✅ صورة حقيقية" if img(rel) != rel else "⬜ مؤقتة"
        lines.append(f"| خلفية {name} | `assets/img/brand/{name}.jpg` | {state} |\n")
    write("IMAGES.md", "".join(lines))


# --------------------------------------------------------------------------
# shared chrome
# --------------------------------------------------------------------------
def head(lang, title, desc, path, base, jsonld=None, image="assets/img/brand/hero.svg"):
    other = "en" if lang == "ar" else "ar"
    other_path = path.replace(f"/{lang}/", f"/{other}/", 1)
    dirn = t(lang, "dir")
    fonts = (
        '<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    )
    if lang == "ar":
        fonts += '<link href="https://fonts.googleapis.com/css2?family=El+Messiri:wght@400;500;600;700&family=Tajawal:wght@300;400;500;700&display=swap" rel="stylesheet">'
    else:
        fonts += '<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500&family=Jost:wght@300;400;500&display=swap" rel="stylesheet">'

    ld = ""
    if jsonld:
        for block in jsonld:
            ld += '<script type="application/ld+json">' + json.dumps(block, ensure_ascii=False) + "</script>\n"

    return f"""<!DOCTYPE html>
<html lang="{lang}" dir="{dirn}" data-base="{base}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="{SITE_URL}{path}">
<link rel="alternate" hreflang="{lang}" href="{SITE_URL}{path}">
<link rel="alternate" hreflang="{other}" href="{SITE_URL}{other_path}">
<link rel="alternate" hreflang="x-default" href="{SITE_URL}{path.replace('/'+lang+'/', '/en/', 1)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{t(lang,'brand')}">
<meta property="og:locale" content="{'ar_EG' if lang=='ar' else 'en_US'}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{SITE_URL}{path}">
<meta property="og:image" content="{SITE_URL}/{image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{SITE_URL}/{image}">
<meta name="theme-color" content="#08192a">
<link rel="icon" type="image/png" sizes="192x192" href="{base}assets/img/brand/favicon-192.png">
<link rel="apple-touch-icon" sizes="512x512" href="{base}assets/img/brand/favicon-512.png">
{fonts}
<link rel="stylesheet" href="{base}assets/css/main.css?v=3">
<script src="{base}assets/js/imgfix.js"></script>
{ld}</head>
<body>
"""


def nav_items(lang, base):
    return [
        (t(lang, "nav.home"), f"{base}{lang}/index.html", "home"),
        (t(lang, "nav.properties"), f"{base}{lang}/properties.html", "properties"),
        (t(lang, "nav.projects"), f"{base}{lang}/projects.html", "projects"),
        (t(lang, "nav.about"), f"{base}{lang}/about.html", "about"),
        (t(lang, "nav.contact"), f"{base}{lang}/contact.html", "contact"),
        (t(lang, "nav.valuation"), f"{base}{lang}/valuation.html", "valuation"),
    ]


def header(lang, base, active, other_href):
    links = "".join(
        f'<a href="{href}"{" aria-current=\"page\"" if key == active else ""}>{label}</a>'
        for label, href, key in nav_items(lang, base)
    )
    drawer_links = "".join(
        f'<a href="{href}">{label}</a>' for label, href, key in nav_items(lang, base)
    )
    return f"""<header class="header">
  <div class="wrap header__inner">
    <a class="logo" href="{base}{lang}/index.html" aria-label="{t(lang,'brand')}">
      <img src="{base}assets/img/brand/logo-footer-white.png" alt="{t(lang,'brand')}" width="514" height="160">
    </a>
    <nav class="nav" aria-label="{t(lang,'nav.home')}">{links}</nav>
    <div class="header__actions">
      <a class="lang-switch" href="{other_href}" hreflang="{'en' if lang=='ar' else 'ar'}">{t(lang,'otherLangName')}</a>
      <a class="btn btn--ghost" href="{base}{lang}/contact.html">{t(lang,'nav.book')}</a>
      <button class="burger" aria-label="Menu" aria-expanded="false" aria-controls="drawer"><span></span><span></span><span></span></button>
    </div>
  </div>
</header>

<div class="drawer" id="drawer">
  <div class="drawer__top">
    <a class="logo" href="{base}{lang}/index.html"><img src="{base}assets/img/brand/logo-footer-white.png" alt="{t(lang,'brand')}" width="514" height="160"></a>
    <button class="drawer__close" data-drawer-close aria-label="Close">&times;</button>
  </div>
  <nav>{drawer_links}</nav>
  <div class="drawer__footer">
    <a class="btn btn--wa" href="https://wa.me/{PHONE_INTL}" target="_blank" rel="noopener">{t(lang,'cta.whatsapp')}</a>
    <a class="lang-switch" href="{other_href}">{t(lang,'otherLangName')}</a>
  </div>
</div>
"""


def whatsapp_widget(lang, base):
    return f"""<div class="wa">
  <div class="wa__panel" role="dialog" aria-label="{t(lang,'whatsapp.title')}">
    <div class="wa__head">
      <span class="wa__avatar"><img src="{base}assets/img/brand/logo-mark.png" alt="" width="172" height="160"></span>
      <span><strong>{t(lang,'whatsapp.title')}</strong><span>{t(lang,'whatsapp.status')}</span></span>
      <button class="wa__close" aria-label="Close">&times;</button>
    </div>
    <div class="wa__body"><p class="wa__bubble">{t(lang,'whatsapp.intro')}</p></div>
    <form class="wa__form">
      <textarea placeholder="{t(lang,'whatsapp.placeholder')}" aria-label="{t(lang,'whatsapp.placeholder')}"></textarea>
      <button class="btn btn--wa btn--block" type="submit">{IC['wa']}{t(lang,'whatsapp.send')}</button>
    </form>
  </div>
  <button class="wa__btn" aria-label="{t(lang,'whatsapp.open')}" aria-expanded="false">{IC['wa']}</button>
</div>
"""


def footer(lang, base):
    types_links = "".join(
        f'<li><a href="{base}{lang}/properties.html?type={ty}">{t(lang, "type."+ty)}</a></li>'
        for ty in ["apartment", "villa", "chalet", "office", "retail"]
    )
    quick = "".join(f'<li><a href="{href}">{label}</a></li>' for label, href, _ in nav_items(lang, base))
    quick += f'<li><a href="{base}{lang}/sahel-map.html">{t(lang, "nav.sahel")}</a></li>'
    return f"""<footer class="footer">
  <div class="wrap">
    <div class="footer__grid">
      <div>
        <a class="footer__logo" href="{base}{lang}/index.html"><img src="{base}assets/img/brand/logo-footer-white.png" alt="{t(lang,'brand')}" width="514" height="160"></a>
        <p>{t(lang,'footer.about')}</p>
        <div class="socials">
          <a href="https://facebook.com/" aria-label="Facebook" target="_blank" rel="noopener">{IC['facebook']}</a>
          <a href="https://instagram.com/" aria-label="Instagram" target="_blank" rel="noopener">{IC['instagram']}</a>
          <a href="https://linkedin.com/" aria-label="LinkedIn" target="_blank" rel="noopener">{IC['linkedin']}</a>
          <a href="https://youtube.com/" aria-label="YouTube" target="_blank" rel="noopener">{IC['youtube']}</a>
        </div>
      </div>
      <div>
        <h4>{t(lang,'footer.quick')}</h4>
        <ul>{quick}</ul>
      </div>
      <div>
        <h4>{t(lang,'footer.types')}</h4>
        <ul>{types_links}</ul>
      </div>
      <div>
        <h4>{t(lang,'footer.newsletter')}</h4>
        <p>{t(lang,'footer.newsletterDesc')}</p>
        <form class="newsletter" id="newsletter-form">
          <input type="email" required placeholder="{t(lang,'footer.emailPlaceholder')}" aria-label="{t(lang,'footer.emailPlaceholder')}">
          <button type="submit" aria-label="{t(lang,'footer.newsletter')}">{IC['arrow']}</button>
        </form>
      </div>
    </div>
    <div class="footer__bottom">
      <span>&copy; <span data-year>2026</span> {t(lang,'brand')}. {t(lang,'footer.rights')}</span>
      <nav><a href="{base}{lang}/privacy.html">{t(lang,'footer.privacy')}</a><a href="{base}{lang}/terms.html">{t(lang,'footer.terms')}</a></nav>
    </div>
  </div>
</footer>
"""


def scripts(base, extra=""):
    return f"""<script src="{base}assets/js/config.js"></script>
<script src="{base}assets/js/app.js"></script>
{extra}
</body>
</html>
"""


def cta_band(lang, base):
    return f"""<section class="cta-band">
  <div class="cta-band__media"><img src="{base}{img("assets/img/brand/cta.svg")}" alt="" loading="lazy" width="1920" height="1080"></div>
  <div class="wrap cta-band__inner">
    <div>
      <p class="eyebrow eyebrow--light">{t(lang,'cta.eyebrow')}</p>
      <h2>{t(lang,'cta.title')}</h2>
      <a class="btn btn--ghost" href="{base}{lang}/contact.html">{t(lang,'cta.btn')}{IC['arrow']}</a>
    </div>
    <div class="cta-band__divider"></div>
    <ul class="contact-list">
      <li>{IC['phone']}<a href="tel:+{PHONE_INTL}" dir="ltr">{PHONE_DISPLAY}</a></li>
      <li>{IC['mail']}<a href="mailto:{EMAIL}">{EMAIL}</a></li>
      <li>{IC['pin']}<span>{I18N[lang]['brand'] and ('123 شارع الكورنيش، الإسكندرية' if lang=='ar' else '123 El Corniche St., Alexandria, Egypt')}</span></li>
    </ul>
  </div>
</section>
"""


# --------------------------------------------------------------------------
# cards
# --------------------------------------------------------------------------
def property_card(lang, base, p):
    url = f"{base}{lang}/property.html?id={p['id']}"
    badge = t(lang, "badge.rent") if p["purpose"] == "rent" else t(lang, "badge.sale")
    ask = sahel_compounds.is_ask(p)
    if ask:
        price = f'<span class="is-ask">{t(lang, "common.requestPrice")}</span>'
    else:
        price = f"{t(lang,'common.egp')} {money(p['price'])}"
        if p["priceUnit"] == "monthly":
            price += f" <small>{t(lang,'common.month')}</small>"
    meta = ""
    if (p.get("area") or 0) > 0:
        meta += f'<span>{IC["area"]}{p["area"]} {t(lang,"common.sqm")}</span>'
    if p["beds"]:
        meta += f'<span>{IC["bed"]}{p["beds"]} {t(lang,"common.beds")}</span>'
    if p["baths"]:
        meta += f'<span>{IC["bath"]}{p["baths"]} {t(lang,"common.baths")}</span>'
    source_badge = f'<span class="card__source">{t(lang, "recommended.source")}</span>' if p.get("sourceUrl") else ""
    flag = f'<span class="card__flag">{"مميزة" if lang == "ar" else "Featured"}</span>' if p.get("featured") else ""
    im = img(p["image"]) if not p["image"].startswith("http") else p["image"]
    im = im if im.startswith("http") else base + im
    return f"""<article class="card scroll-fade" data-id="{p['id']}">
  <a class="card__media" href="{url}">
    <img src="{im}" alt="{esc(p['title'][lang])}" loading="lazy" width="900" height="675" referrerpolicy="no-referrer">
    <span class="card__badge">{badge}</span>{flag}{source_badge}
  </a>
  <div class="card__body">
    <h3 class="card__title"><a href="{url}">{esc(p['title'][lang])}</a></h3>
    <p class="card__place">{IC['pin']}{esc(p['location'][lang])}</p>
    <div class="card__meta">{meta}</div>
    <p class="card__price{' is-ask' if ask else ''}">{price}</p>
  </div>
  <a class="card__foot" href="{url}">{t(lang,'featured.viewDetails')}{IC['arrow']}</a>
</article>"""


def project_price_display(lang, amount):
    return t(lang, "common.requestPrice") if not amount else f"{t(lang, 'common.egp')} {money(amount)}"


def project_card(lang, base, pr):
    url = f"{base}{lang}/projects/{pr['slug']}.html"
    types = "، ".join(t(lang, "type." + x) for x in pr["types"][:3]) if lang == "ar" else ", ".join(t(lang, "type." + x) for x in pr["types"][:3])
    return f"""<article class="card scroll-fade">
  <a class="card__media" href="{url}">
    <img src="{base}{img(pr['gallery'][0])}" alt="{pr['name'][lang]}" loading="lazy" width="1200" height="800">
    <span class="card__badge">{t(lang,'city.'+pr['city'])}</span>
  </a>
  <div class="card__body">
    <h3 class="card__title"><a href="{url}">{pr['name'][lang]}</a></h3>
    <p class="card__place">{IC['pin']}{pr['location'][lang]}</p>
    <div class="card__meta"><span>{IC['building']}{pr['developer'][lang]}</span></div>
    <div class="card__meta"><span>{IC['tag']}{types}</span></div>
    <p class="card__price"><small>{t(lang,'common.from')}</small> {project_price_display(lang, pr['startingPrice'])}</p>
  </div>
  <a class="card__foot" href="{url}">{t(lang,'featured.viewDetails')}{IC['arrow']}</a>
</article>"""


# --------------------------------------------------------------------------
# pages
# --------------------------------------------------------------------------
def price_bands(lang):
    bands = [("", t(lang, "search.anyPrice")), ("0-5000000", "< 5M"), ("5000000-10000000", "5M - 10M"),
             ("10000000-20000000", "10M - 20M"), ("20000000-40000000", "20M - 40M"), ("40000000-999000000", "40M+")]
    return "".join(f'<option value="{v}">{l}</option>' for v, l in bands)


def area_bands(lang):
    bands = [("", t(lang, "search.anyArea")), ("0-120", "< 120"), ("120-200", "120 - 200"),
             ("200-300", "200 - 300"), ("300-9999", "300+")]
    return "".join(f'<option value="{v}">{l}</option>' for v, l in bands)


def build_home(lang):
    base = "../"
    path = f"/{lang}/index.html"
    other = "en" if lang == "ar" else "ar"
    title = ("إيليت للتسويق العقاري | وحدات مختارة بعناية في جميع أنحاء مصر"
             if lang == "ar" else
             "Elite Real Estate | Handpicked Properties Across Egypt")
    desc = ("إيليت للتسويق العقاري: وحدات مختارة للبيع والإيجار في جميع أنحاء مصر، بأسعار وأنظمة سداد واضحة ومستشارين متخصصين."
            if lang == "ar" else
            "Elite Real Estate: handpicked homes for sale and rent across Egypt, with clear pricing, payment plans and expert advisors.")

    ld = [
        {
            "@context": "https://schema.org",
            "@type": "RealEstateAgent",
            "name": t(lang, "brand"),
            "url": f"{SITE_URL}{path}",
            "image": f"{SITE_URL}/assets/img/brand/logo.png",
            "logo": f"{SITE_URL}/assets/img/brand/logo.png",
            "telephone": "+" + PHONE_INTL,
            "email": EMAIL,
            "areaServed": "Egypt",
            "address": {"@type": "PostalAddress", "streetAddress": "123 El Corniche St.",
                        "addressLocality": "Alexandria", "addressCountry": "EG"},
            "openingHours": "Sa-Th 10:00-20:00",
            "sameAs": ["https://facebook.com/", "https://instagram.com/", "https://linkedin.com/", "https://youtube.com/"],
        },
        {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": t(lang, "brand"),
            "url": f"{SITE_URL}/{lang}/",
            "inLanguage": lang,
            "potentialAction": {
                "@type": "SearchAction",
                "target": f"{SITE_URL}/{lang}/properties.html?keyword={{search_term_string}}",
                "query-input": "required name=search_term_string",
            },
        },
    ]

    featured_props = sahel_compounds.sort_units([p for p in PROPERTIES if p.get("featured")])[:3]
    recommended_props = sahel_compounds.sort_units([p for p in PROPERTIES if p.get("recommended")])[:3]
    featured_projects = [p for p in PROJECTS if p.get("featured")][:4]

    loc_opts = f'<option value="">{t(lang,"search.allLocations")}</option>' + "".join(
        f'<option value="{c}">{t(lang,"city."+c)}</option>' for c in CITIES)
    type_opts = f'<option value="">{t(lang,"search.allTypes")}</option>' + "".join(
        f'<option value="{ty}">{t(lang,"type."+ty)}</option>' for ty in TYPES)

    html = head(lang, title, desc, path, base, ld)
    html += header(lang, base, "home", f"{base}{other}/index.html")

    html += f"""<main>
<section class="hero">
  <div class="hero__media"><img src="{base}{img("assets/img/brand/hero.svg")}" alt="" width="1920" height="1080" fetchpriority="high"></div>
  <div class="wrap">
    <h1>{t(lang,'hero.title')}</h1>
    <hr class="rule">
    <p class="hero__sub">{t(lang,'hero.sub')}</p>
    <div class="hero__cta">
      <a class="btn btn--solid" href="{base}{lang}/properties.html">{t(lang,'hero.cta1')}{IC['arrow']}</a>
      <a class="btn btn--ghost" href="{base}{lang}/contact.html">{t(lang,'hero.cta2')}</a>
    </div>
  </div>
</section>

<div class="searchbar">
  <div class="wrap">
    <form class="searchbar__inner" id="hero-search" role="search">
      <label class="sf">
        <span class="sf__icon">{IC['pin']}</span>
        <span class="sf__body"><span class="sf__label">{t(lang,'search.location')}</span>
        <select name="location">{loc_opts}</select></span>
      </label>
      <label class="sf">
        <span class="sf__icon">{IC['building']}</span>
        <span class="sf__body"><span class="sf__label">{t(lang,'search.type')}</span>
        <select name="type">{type_opts}</select></span>
      </label>
      <label class="sf">
        <span class="sf__icon">{IC['tag']}</span>
        <span class="sf__body"><span class="sf__label">{t(lang,'search.price')}</span>
        <span class="sf__row">
          <input type="number" name="minPrice" min="0" step="100000" placeholder="{t(lang,'filters.minPrice')}" aria-label="{t(lang,'filters.minPrice')}">
          <input type="number" name="maxPrice" min="0" step="100000" placeholder="{t(lang,'filters.maxPrice')}" aria-label="{t(lang,'filters.maxPrice')}">
        </span></span>
      </label>
      <label class="sf">
        <span class="sf__icon">{IC['expand']}</span>
        <span class="sf__body"><span class="sf__label">{t(lang,'search.area')}</span>
        <span class="sf__row">
          <input type="number" name="minArea" min="0" step="10" placeholder="{t(lang,'filters.minArea')}" aria-label="{t(lang,'filters.minArea')}">
          <input type="number" name="maxArea" min="0" step="10" placeholder="{t(lang,'filters.maxArea')}" aria-label="{t(lang,'filters.maxArea')}">
        </span></span>
      </label>
      <button class="btn btn--solid" type="submit">{IC['search']}{t(lang,'search.submit')}</button>
    </form>
  </div>
</div>

<section class="section section--cream">
  <div class="wrap featured-grid">
    <div class="scroll-fade">
      <p class="eyebrow">{t(lang,'featured.eyebrow')}</p>
      <h2 class="section__title">{t(lang,'featured.title')}</h2>
      <hr class="rule">
      <p>{t(lang,'featured.desc')}</p>
      <a class="link-arrow" href="{base}{lang}/properties.html">{t(lang,'featured.viewAll')}{IC['arrow']}</a>
    </div>
    <div class="cards" data-live="featured">
      {"".join(property_card(lang, base, p) for p in featured_props)}
    </div>
  </div>
</section>

<section class="section section--sand recommendation-section">
  <div class="wrap featured-grid">
    <div class="scroll-fade">
      <p class="eyebrow">{t(lang,'recommended.eyebrow')}</p>
      <h2 class="section__title">{t(lang,'recommended.title')}</h2>
      <hr class="rule">
      <p>{t(lang,'recommended.desc')}</p>
      <a class="link-arrow" href="{base}{lang}/properties.html">{t(lang,'recommended.viewAll')}{IC['arrow']}</a>
    </div>
    <div class="cards" data-live="recommended">
      {"".join(property_card(lang, base, p) for p in recommended_props)}
    </div>
  </div>
</section>

<section class="section section--dark">
  <div class="wrap">
    <div class="section__head">
      <p class="eyebrow eyebrow--light" style="margin:0">{t(lang,'projects.eyebrow')}</p>
      <a class="link-arrow link-arrow--light" href="{base}{lang}/projects.html">{t(lang,'projects.viewAll')}{IC['arrow']}</a>
    </div>
    <div class="tiles" data-carousel>
      {"".join(f'''<a class="tile scroll-fade" href="{base}{lang}/projects/{pr['slug']}.html">
        <img src="{base}{img(pr['gallery'][0])}" alt="{pr['name'][lang]}" loading="lazy" width="1200" height="800">
        <span class="tile__label"><h3>{pr['name'][lang]}</h3><span>{t(lang,'city.'+pr['city'])}</span></span>
      </a>''' for pr in featured_projects)}
    </div>
  </div>
</section>

<section class="section section--cream">
  <div class="wrap why-grid">
    <div class="scroll-fade">
      <p class="eyebrow">{t(lang,'why.eyebrow')}</p>
      <h2 class="section__title section__title--underlined">{t(lang,'why.title')}</h2>
    </div>
    <div class="why-list">
      <div class="why-item scroll-fade"><span class="why-item__icon">{IC['diamond']}</span><h3>{t(lang,'why.1t')}</h3><p>{t(lang,'why.1d')}</p></div>
      <div class="why-item scroll-fade"><span class="why-item__icon">{IC['advisor']}</span><h3>{t(lang,'why.2t')}</h3><p>{t(lang,'why.2d')}</p></div>
      <div class="why-item scroll-fade"><span class="why-item__icon">{IC['shield']}</span><h3>{t(lang,'why.3t')}</h3><p>{t(lang,'why.3d')}</p></div>
      <div class="why-item scroll-fade"><span class="why-item__icon">{IC['support']}</span><h3>{t(lang,'why.4t')}</h3><p>{t(lang,'why.4d')}</p></div>
    </div>
  </div>
</section>

{cta_band(lang, base)}
</main>
"""
    html += footer(lang, base) + whatsapp_widget(lang, base) + scripts(
        base, f'<script src="{base}data/properties.js"></script>\n<script src="{base}assets/js/cards.js?v=2"></script>\n'
              f'<script src="{base}assets/js/home-live.js"></script>')
    write(f"{lang}/index.html", html)


def build_properties(lang):
    base = "../"
    path = f"/{lang}/properties.html"
    other = "en" if lang == "ar" else "ar"
    title = ("الوحدات المتاحة للبيع والإيجار | إيليت للتسويق العقاري"
             if lang == "ar" else "Properties for sale and rent | Elite Real Estate")
    desc = ("ابحث في وحدات إيليت: شقق وفيلات وشاليهات وتاون هاوس في جميع أنحاء مصر، بفلاتر للسعر والمساحة وعدد الغرف."
            if lang == "ar" else
            "Search Elite's listings: apartments, villas, chalets and townhouses across Egypt, filtered by price, area and bedrooms.")

    ld = [{
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": title,
        "url": f"{SITE_URL}{path}",
        "inLanguage": lang,
        "isPartOf": {"@type": "WebSite", "name": t(lang, "brand"), "url": f"{SITE_URL}/{lang}/"},
    }]

    loc_opts = f'<option value="">{t(lang,"search.allLocations")}</option>' + "".join(
        f'<option value="{c}">{t(lang,"city."+c)}</option>' for c in CITIES)
    type_opts = f'<option value="">{t(lang,"search.allTypes")}</option>' + "".join(
        f'<option value="{ty}">{t(lang,"type."+ty)}</option>' for ty in TYPES)
    proj_opts = f'<option value="">{t(lang,"filters.all")}</option>' + "".join(
        f'<option value="{pr["slug"]}">{pr["name"][lang]}</option>' for pr in PROJECTS)

    beds_chips = "".join(
        f'<button type="button" class="chip" data-beds="{b}">{b}</button>' for b in ["1", "2", "3", "4+"])

    html = head(lang, title, desc, path, base, ld)
    html += header(lang, base, "properties", f"{base}{other}/properties.html")
    html += f"""<main>
<section class="page-hero">
  <div class="page-hero__media"><img src="{base}{img("assets/img/brand/page.svg")}" alt="" width="1920" height="1080"></div>
  <div class="wrap">
    <nav class="breadcrumbs" aria-label="breadcrumb">
      <a href="{base}{lang}/index.html">{t(lang,'breadcrumb.home')}</a> <span>/</span> <span>{t(lang,'nav.properties')}</span>
    </nav>
    <h1>{t(lang,'nav.properties')}</h1>
    <p>{desc}</p>
  </div>
</section>

<section class="section">
  <div class="wrap listing" id="listing">
    <aside class="filters" id="filters">
      <h2>{t(lang,'filters.title')}</h2>
      <form id="filters-form">
        <div class="filter">
          <span class="filter__label">{t(lang,'search.keyword')}</span>
          <input type="search" id="f-keyword" placeholder="{t(lang,'search.keyword')}" aria-label="{t(lang,'search.keyword')}">
        </div>
        <div class="filter">
          <span class="filter__label">{t(lang,'filters.purpose')}</span>
          <div class="chips">
            <button type="button" class="chip" data-purpose="sale">{t(lang,'filters.sale')}</button>
            <button type="button" class="chip" data-purpose="rent">{t(lang,'filters.rent')}</button>
          </div>
        </div>
        <div class="filter">
          <label for="f-location">{t(lang,'search.location')}</label>
          <select id="f-location" name="location">{loc_opts}</select>
        </div>
        <div class="filter">
          <label for="f-type">{t(lang,'search.type')}</label>
          <select id="f-type" name="type">{type_opts}</select>
        </div>
        <div class="filter">
          <label for="f-project">{t(lang,'filters.project')}</label>
          <select id="f-project" name="project">{proj_opts}</select>
        </div>
        <div class="filter">
          <span class="filter__label">{t(lang,'search.price')} ({t(lang,'common.egp')})</span>
          <div class="filter__row">
            <input type="number" name="minPrice" min="0" step="100000" placeholder="{t(lang,'filters.minPrice')}" aria-label="{t(lang,'filters.minPrice')}">
            <input type="number" name="maxPrice" min="0" step="100000" placeholder="{t(lang,'filters.maxPrice')}" aria-label="{t(lang,'filters.maxPrice')}">
          </div>
        </div>
        <div class="filter">
          <span class="filter__label">{t(lang,'search.area')}</span>
          <div class="filter__row">
            <input type="number" name="minArea" min="0" step="10" placeholder="{t(lang,'filters.minArea')}" aria-label="{t(lang,'filters.minArea')}">
            <input type="number" name="maxArea" min="0" step="10" placeholder="{t(lang,'filters.maxArea')}" aria-label="{t(lang,'filters.maxArea')}">
          </div>
        </div>
        <div class="filter">
          <span class="filter__label">{t(lang,'filters.bedrooms')}</span>
          <div class="chips">{beds_chips}</div>
        </div>
        <button type="button" class="btn btn--outline btn--block" id="filters-reset">{t(lang,'filters.reset')}</button>
      </form>
    </aside>

    <div>
      <div class="listing__bar">
        <p class="listing__count" id="results-count"></p>
        <div class="listing__sort">
          <button class="chip filters-toggle" id="filters-toggle" type="button">{t(lang,'filters.title')}</button>
          <label for="sort">{t(lang,'results.sort')}</label>
          <select id="sort">
            <option value="newest">{t(lang,'sort.newest')}</option>
            <option value="priceAsc">{t(lang,'sort.priceAsc')}</option>
            <option value="priceDesc">{t(lang,'sort.priceDesc')}</option>
            <option value="areaDesc">{t(lang,'sort.areaDesc')}</option>
          </select>
        </div>
      </div>
      <div class="cards" id="results-grid"></div>
      <div style="text-align:center;margin-top:34px">
        <button class="btn btn--outline" id="load-more" hidden>{t(lang,'results.loadMore')}</button>
      </div>
      <p class="disclaimer" style="margin-top:40px">{t(lang,'disclaimer')}</p>
    </div>
  </div>
</section>
</main>
"""
    html += footer(lang, base) + whatsapp_widget(lang, base)
    html += f'<script type="application/json" id="i18n-data">{json.dumps(I18N[lang], ensure_ascii=False)}</script>\n'
    html += scripts(base, f'<script src="{base}data/properties.js"></script>\n<script src="{base}assets/js/cards.js?v=2"></script>\n<script src="{base}assets/js/search.js?v=2"></script>')
    write(f"{lang}/properties.html", html)


def build_property_detail(lang):
    """Single template rendered client-side from ?id=."""
    base = "../"
    path = f"/{lang}/property.html"
    other = "en" if lang == "ar" else "ar"
    title = ("تفاصيل الوحدة | إيليت للتسويق العقاري" if lang == "ar" else "Property details | Elite Real Estate")
    desc = ("تفاصيل الوحدة: المساحة والسعر والتشطيب والموقع، مع إمكانية التواصل المباشر على واتساب."
            if lang == "ar" else
            "Property details: area, price, finishing and location, with direct WhatsApp contact.")

    html = head(lang, title, desc, path, base)
    html = html.replace('<meta name="robots" content="index, follow, max-image-preview:large">',
                        '<meta name="robots" content="noindex, follow">')
    html += header(lang, base, "properties", f"{base}{other}/property.html")
    html += f"""<main id="property-root" class="section" style="padding-top:140px">
  <div class="wrap"><p>{t(lang,'results.none')}</p></div>
</main>
"""
    html += footer(lang, base) + whatsapp_widget(lang, base)
    html += f'<script type="application/json" id="i18n-data">{json.dumps(I18N[lang], ensure_ascii=False)}</script>\n'
    html += scripts(base, f'<script src="{base}data/properties.js"></script>\n<script src="{base}data/projects.js"></script>\n<script src="{base}data/compounds.js"></script>\n<script src="{base}assets/js/cards.js?v=2"></script>\n<script src="{base}assets/js/property.js?v=2"></script>')
    write(f"{lang}/property.html", html)


def build_projects_index(lang):
    base = "../"
    path = f"/{lang}/projects.html"
    other = "en" if lang == "ar" else "ar"
    title = ("مشاريع وكومباوندات في جميع أنحاء مصر | إيليت"
             if lang == "ar" else "Compounds and projects across Egypt | Elite")
    desc = ("دليل مشاريع إيليت في جميع أنحاء مصر: كريكس، ذا ون سموحة، أجازة العلمين، مراسي، هاسيندا باي وغيرها بالأسعار وأنظمة السداد."
            if lang == "ar" else
            "A guide to developments across Egypt: CREEKS, THE ONE Smouha, AJAZA New Alamein, Marassi, Hacienda Bay and more, with pricing and payment plans.")

    ld = [{
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": title,
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": pr["name"][lang],
             "url": f"{SITE_URL}/{lang}/projects/{pr['slug']}.html"}
            for i, pr in enumerate(PROJECTS)
        ],
    }]

    html = head(lang, title, desc, path, base, ld)
    html += header(lang, base, "projects", f"{base}{other}/projects.html")
    html += f"""<main>
<section class="page-hero">
  <div class="page-hero__media"><img src="{base}{img("assets/img/brand/page.svg")}" alt="" width="1920" height="1080"></div>
  <div class="wrap">
    <nav class="breadcrumbs"><a href="{base}{lang}/index.html">{t(lang,'breadcrumb.home')}</a> <span>/</span> <span>{t(lang,'nav.projects')}</span></nav>
    <h1>{t(lang,'projects.title')}</h1>
    <p>{t(lang,'projects.subtitle')}</p>
  </div>
</section>
<section class="section">
  <div class="wrap">
    <div class="cards">{"".join(project_card(lang, base, pr) for pr in PROJECTS)}</div>
    <p class="disclaimer" style="margin-top:44px">{t(lang,'disclaimer')}</p>
  </div>
</section>
{cta_band(lang, base)}
</main>
"""
    html += footer(lang, base) + whatsapp_widget(lang, base) + scripts(base)
    write(f"{lang}/projects.html", html)


def build_project_page(lang, pr):
    base = "../../"
    slug = pr["slug"]
    path = f"/{lang}/projects/{slug}.html"
    other = "en" if lang == "ar" else "ar"
    name = pr["name"][lang]

    title = (f"{name} - أسعار ووحدات وأنظمة سداد | إيليت للتسويق العقاري"
             if lang == "ar" else f"{name} - prices, units and payment plans | Elite Real Estate")
    desc = pr["tagline"][lang] + " — " + (
        f"{pr['developer'][lang]}، {pr['location'][lang]}." if pr['startingPrice'] else f"{pr['developer'][lang]}، {pr['location'][lang]}. السعر عند الطلب."
        if lang == "ar" else
        f"{pr['developer'][lang]}, {pr['location'][lang]}. Prices from EGP {money(pr['startingPrice'])}.")

    breadcrumb = {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": t(lang, "breadcrumb.home"), "item": f"{SITE_URL}/{lang}/index.html"},
            {"@type": "ListItem", "position": 2, "name": t(lang, "nav.projects"), "item": f"{SITE_URL}/{lang}/projects.html"},
            {"@type": "ListItem", "position": 3, "name": name, "item": f"{SITE_URL}{path}"},
        ],
    }
    residence = {
        "@context": "https://schema.org",
        "@type": "ApartmentComplex",
        "name": name,
        "description": pr["about"][lang][0],
        "url": f"{SITE_URL}{path}",
        "image": [f"{SITE_URL}/{img(g)}" for g in pr["gallery"]],
        "address": {"@type": "PostalAddress", "addressLocality": t(lang, "city." + pr["city"]),
                    "addressRegion": pr["location"][lang], "addressCountry": "EG"},
        "numberOfAvailableAccommodationUnits": len(pr["unitTypes"]),
        "amenityFeature": [{"@type": "LocationFeatureSpecification", "name": t(lang, "am." + a), "value": True}
                           for a in pr["amenities"]],
        "makesOffer": {"@type": "Offer", "price": pr["startingPrice"], "priceCurrency": "EGP",
                       "availability": "https://schema.org/InStock",
                       "seller": {"@type": "RealEstateAgent", "name": t(lang, "brand"), "telephone": "+" + PHONE_INTL}},
    }
    ld = [breadcrumb, residence]
    if pr["faq"]:
        ld.append({
            "@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": f["q"][lang],
                            "acceptedAnswer": {"@type": "Answer", "text": f["a"][lang]}} for f in pr["faq"]],
        })

    wa_ctx = (f"مهتم بمشروع {name} - {pr['location'][lang]}" if lang == "ar"
              else f"I'm interested in {name} - {pr['location'][lang]}")

    about_html = "".join(f"<p>{p}</p>" for p in pr["about"][lang])
    highlights = "".join(f'<span class="pill">{IC["check"]}{h[lang]}</span>' for h in pr["highlights"])
    amenities = "".join(f'<span class="pill">{IC["check"]}{t(lang, "am."+a)}</span>' for a in pr["amenities"])
    nearby = "".join(f'<span class="pill">{IC["pin"]}{n[lang]}</span>' for n in pr["nearby"])
    units = "".join(
        f"<tr><td>{u['name'][lang]}</td><td>{u['area']} {t(lang,'common.sqm')}</td><td>{u['beds']} {t(lang,'common.beds')}</td></tr>"
        for u in pr["unitTypes"])
    plans = "".join(
        f'<div class="plan"><b>{p["dp"]}%</b><span>{t(lang,"common.downPayment")}</span><hr class="rule" style="margin:12px auto"><b>{p["years"]}</b><span>{t(lang,"common.years")}</span></div>'
        for p in pr["payment"])
    faqs = "".join(
        f'''<div class="faq-item"><button class="faq-q" aria-expanded="false">{f["q"][lang]}{IC["plus"]}</button>
        <div class="faq-a"><p>{f["a"][lang]}</p></div></div>''' for f in pr["faq"])

    similar = [x for x in PROJECTS if x["slug"] != slug and x["city"] == pr["city"]][:3]
    if len(similar) < 3:
        similar += [x for x in PROJECTS if x["slug"] != slug and x not in similar][:3 - len(similar)]

    html = head(lang, title, desc, path, base, ld, image=img(pr["gallery"][0]))
    html = html.replace("<body>", f'<body data-wa-context="{wa_ctx}">')
    html += header(lang, base, "projects", f"{base}{other}/projects/{slug}.html")

    html += f"""<main>
<section class="proj-hero" style="padding-top:84px">
  <div class="proj-gallery">
    <div class="proj-gallery__main"><img src="{base}{img(pr['gallery'][0])}" alt="{name}" width="1200" height="800" fetchpriority="high"></div>
    <div class="proj-gallery__side">
      <img src="{base}{img(pr['gallery'][1 % len(pr['gallery'])])}" alt="{name}" loading="lazy" width="1200" height="800">
      <img src="{base}{img(pr['gallery'][2 % len(pr['gallery'])])}" alt="{name}" loading="lazy" width="1200" height="800">
    </div>
  </div>
</section>

<div class="wrap">
  <div class="proj-layout">
    <div>
      <nav class="breadcrumbs" style="color:var(--muted);margin-top:26px">
        <a href="{base}{lang}/index.html">{t(lang,'breadcrumb.home')}</a> <span>/</span>
        <a href="{base}{lang}/projects.html">{t(lang,'nav.projects')}</a> <span>/</span> <span>{name}</span>
      </nav>

      <div class="proj-head">
        <div>
          <h1>{name}</h1>
          <p class="card__place">{IC['pin']}{pr['location'][lang]}</p>
        </div>
        <div class="proj-price">
          <small>{t(lang,'common.from')}</small>
          <strong>{project_price_display(lang, pr['startingPrice'])}</strong>
        </div>
      </div>

      <div class="facts">
        <div class="fact"><span>{t(lang,'common.developer')}</span><b>{pr['developer'][lang]}</b></div>
        <div class="fact"><span>{t(lang,'common.landArea')}</span><b>{pr['landArea'][lang]}</b></div>
        <div class="fact"><span>{t(lang,'common.delivery')}</span><b>{pr['delivery'][lang] if isinstance(pr['delivery'], dict) else pr['delivery']}</b></div>
        <div class="fact"><span>{t(lang,'common.status')}</span><b>{pr['status'][lang]}</b></div>
      </div>

      <div class="block">
        <h2>{t(lang,'common.about')}</h2>
        {about_html}
      </div>

      <div class="block">
        <h2>{t(lang,'common.highlights')}</h2>
        <div class="pill-list">{highlights}</div>
      </div>

      <div class="block">
        <h2>{t(lang,'common.unitTypes')}</h2>
        <table class="table">
          <thead><tr><th>{t(lang,'common.unitType')}</th><th>{t(lang,'common.area')}</th><th>{t(lang,'filters.bedrooms')}</th></tr></thead>
          <tbody>{units}</tbody>
        </table>
      </div>

      <div class="block">
        <h2>{t(lang,'common.payment')}</h2>
        <div class="plans">{plans}</div>
      </div>

      <div class="block">
        <h2>{t(lang,'common.amenities')}</h2>
        <div class="pill-list">{amenities}</div>
      </div>

      <div class="block">
        <h2>{t(lang,'common.nearby')}</h2>
        <div class="pill-list">{nearby}</div>
      </div>

      <div class="block">
        <h2>{t(lang,'common.mapTitle')}</h2>
        <iframe class="map-embed" src="{pr['map']}" title="{name}" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
      </div>

      {f'<div class="block"><h2>{t(lang,"common.faq")}</h2>{faqs}</div>' if faqs else ''}

      <p class="disclaimer">{t(lang,'disclaimer')}</p>
    </div>

    <aside>
      <div class="aside-card">
        <h3>{t(lang,'cta.requestPrice')}</h3>
        <p>{t(lang,'contact.subtitle')}</p>
        <a class="btn btn--wa" href="https://wa.me/{PHONE_INTL}" data-wa>{IC['wa']}{t(lang,'cta.whatsapp')}</a>
        <a class="btn btn--outline" href="tel:+{PHONE_INTL}">{IC['phone']}{t(lang,'cta.call')}</a>
        <a class="btn btn--solid" href="{base}{lang}/contact.html">{t(lang,'cta.bookVisit')}</a>
        <p class="aside-note">{t(lang,'disclaimer')}</p>
      </div>
    </aside>
  </div>
</div>

<section class="section section--cream">
  <div class="wrap">
    <h2 class="section__title" style="margin-bottom:32px">{t(lang,'common.similar')}</h2>
    <div class="cards">{"".join(project_card(lang, base, s) for s in similar)}</div>
  </div>
</section>
</main>
"""
    html += footer(lang, base) + whatsapp_widget(lang, base) + scripts(base)
    write(f"{lang}/projects/{slug}.html", html)


def build_about(lang):
    base = "../"
    path = f"/{lang}/about.html"
    other = "en" if lang == "ar" else "ar"
    title = ("من نحن | إيليت للتسويق العقاري" if lang == "ar" else "About us | Elite Real Estate")
    desc = ("إيليت للتسويق العقاري: فريق استشاري متخصص في السوق العقاري المصري، بنساعدك تختار الوحدة الصح بمعلومات صادقة."
            if lang == "ar" else
            "Elite Real Estate: an advisory team specialising in the Egyptian property market, helping you choose the right home with straight answers.")

    body_ar = """<p>إيليت للتسويق العقاري شركة تسويق عقاري مقرها الإسكندرية، متخصصة في الوحدات المتميزة المختارة بعناية في جميع أنحاء مصر. شغلنا الأساسي إننا نوصل العميل للوحدة اللي فعلًا مناسبة له، مش اللي إحنا عايزين نبيعها.</p>
<p>بنشتغل مع كبرى شركات التطوير العقاري، وبنتابع المشاريع من الطرح لحد التسليم، عشان نقدر نقول لك بصراحة إيه اللي يستاهل وإيه اللي لأ. ولما نرشحلك مشروع، بنقولك مميزاته وعيوبه، وبنوضح الفرق بين الأسعار وأنظمة السداد المختلفة.</p>
<p>سواء بتدور على سكن دائم، أو شاليه على البحر، أو فرصة استثمارية بعائد إيجار في أي مدينة في مصر، فريقنا هيساعدك تقارن بين الخيارات بالأرقام وتاخد قرارك وإنت فاهم كل تفصيلة.</p>"""
    body_en = """<p>Elite Real Estate is an Alexandria-based property advisory specialising in premium, carefully selected homes across Egypt. Our job is to get you to the unit that actually fits, not the one we would prefer to sell.</p>
<p>We work with the country's major developers and follow projects from launch to handover, which is what lets us tell you plainly what is worth it and what isn't. When we shortlist something, you get its trade-offs as well as its strengths, and a clear comparison of pricing and payment terms.</p>
<p>Whether you're after a permanent home, a chalet by the sea, or an investment with rental yield anywhere in Egypt, our team will help you compare the options on the numbers and decide with the full picture.</p>"""

    stats = [
        ("+500", "وحدة تم بيعها" if lang == "ar" else "Properties sold"),
        ("+12", "مشروع نمثله" if lang == "ar" else "Projects represented"),
        ("+10", "سنوات خبرة" if lang == "ar" else "Years of experience"),
        ("98%", "رضا العملاء" if lang == "ar" else "Client satisfaction"),
    ]
    stats_html = "".join(f'<div class="stat scroll-fade"><b>{v}</b><span>{l}</span></div>' for v, l in stats)

    ld = [{"@context": "https://schema.org", "@type": "AboutPage", "name": title, "url": f"{SITE_URL}{path}"}]
    html = head(lang, title, desc, path, base, ld)
    html += header(lang, base, "about", f"{base}{other}/about.html")
    html += f"""<main>
<section class="page-hero">
  <div class="page-hero__media"><img src="{base}{img("assets/img/brand/about.svg")}" alt="" width="1920" height="1080"></div>
  <div class="wrap">
    <nav class="breadcrumbs"><a href="{base}{lang}/index.html">{t(lang,'breadcrumb.home')}</a> <span>/</span> <span>{t(lang,'nav.about')}</span></nav>
    <h1>{t(lang,'about.title')}</h1>
    <p>{desc}</p>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="prose">{body_ar if lang == 'ar' else body_en}</div>
    <hr class="rule" style="margin:48px 0">
    <div class="stats">{stats_html}</div>
  </div>
</section>

<section class="section section--cream">
  <div class="wrap why-grid">
    <div>
      <p class="eyebrow">{t(lang,'why.eyebrow')}</p>
      <h2 class="section__title section__title--underlined">{t(lang,'why.title')}</h2>
    </div>
    <div class="why-list">
      <div class="why-item"><span class="why-item__icon">{IC['diamond']}</span><h3>{t(lang,'why.1t')}</h3><p>{t(lang,'why.1d')}</p></div>
      <div class="why-item"><span class="why-item__icon">{IC['advisor']}</span><h3>{t(lang,'why.2t')}</h3><p>{t(lang,'why.2d')}</p></div>
      <div class="why-item"><span class="why-item__icon">{IC['shield']}</span><h3>{t(lang,'why.3t')}</h3><p>{t(lang,'why.3d')}</p></div>
      <div class="why-item"><span class="why-item__icon">{IC['support']}</span><h3>{t(lang,'why.4t')}</h3><p>{t(lang,'why.4d')}</p></div>
    </div>
  </div>
</section>

{cta_band(lang, base)}
</main>
"""
    html += footer(lang, base) + whatsapp_widget(lang, base) + scripts(base)
    write(f"{lang}/about.html", html)


def build_contact(lang):
    base = "../"
    path = f"/{lang}/contact.html"
    other = "en" if lang == "ar" else "ar"
    title = ("تواصل معنا | إيليت للتسويق العقاري" if lang == "ar" else "Contact us | Elite Real Estate")
    desc = ("كلمنا على واتساب أو التليفون أو ابعتلنا استفسارك، وفريق إيليت هيرشحلك الوحدات المناسبة لميزانيتك."
            if lang == "ar" else
            "Message us on WhatsApp, call, or send an enquiry and the Elite team will shortlist properties that fit your budget.")

    interest = "".join(f'<option value="{t(lang,"type."+ty)}">{t(lang,"type."+ty)}</option>' for ty in TYPES)
    ld = [{
        "@context": "https://schema.org", "@type": "ContactPage", "name": title, "url": f"{SITE_URL}{path}",
        "mainEntity": {"@type": "RealEstateAgent", "name": t(lang, "brand"), "telephone": "+" + PHONE_INTL,
                       "email": EMAIL},
    }]

    html = head(lang, title, desc, path, base, ld)
    html += header(lang, base, "contact", f"{base}{other}/contact.html")
    html += f"""<main>
<section class="page-hero">
  <div class="page-hero__media"><img src="{base}{img("assets/img/brand/page.svg")}" alt="" width="1920" height="1080"></div>
  <div class="wrap">
    <nav class="breadcrumbs"><a href="{base}{lang}/index.html">{t(lang,'breadcrumb.home')}</a> <span>/</span> <span>{t(lang,'nav.contact')}</span></nav>
    <h1>{t(lang,'contact.title')}</h1>
    <p>{t(lang,'contact.subtitle')}</p>
  </div>
</section>

<section class="section">
  <div class="wrap contact-grid">
    <form id="contact-form">
      <div class="form-row">
        <div class="field"><label for="c-name">{t(lang,'contact.name')}</label><input id="c-name" name="name" required></div>
        <div class="field"><label for="c-phone">{t(lang,'contact.phone')}</label><input id="c-phone" name="phone" type="tel" required></div>
      </div>
      <div class="form-row">
        <div class="field"><label for="c-email">{t(lang,'contact.email')}</label><input id="c-email" name="email" type="email"></div>
        <div class="field"><label for="c-interest">{t(lang,'contact.interest')}</label>
          <select id="c-interest" name="interest"><option value="">—</option>{interest}</select></div>
      </div>
      <div class="field"><label for="c-message">{t(lang,'contact.message')}</label><textarea id="c-message" name="message"></textarea></div>
      <button class="btn btn--wa" type="submit">{IC['wa']}{t(lang,'contact.send')}</button>
    </form>

    <aside class="info-card">
      <ul class="contact-list">
        <li>{IC['phone']}<a href="tel:+{PHONE_INTL}" dir="ltr">{PHONE_DISPLAY}</a></li>
        <li>{IC['wa']}<a href="https://wa.me/{PHONE_INTL}" target="_blank" rel="noopener">{t(lang,'cta.whatsapp')}</a></li>
        <li>{IC['mail']}<a href="mailto:{EMAIL}">{EMAIL}</a></li>
        <li>{IC['pin']}<span>{'123 شارع الكورنيش، الإسكندرية، مصر' if lang == 'ar' else '123 El Corniche St., Alexandria, Egypt'}</span></li>
        <li>{IC['clock']}<span>{t(lang,'contact.hoursValue')}</span></li>
      </ul>
      <hr class="rule">
      <iframe class="map-embed" style="height:260px" src="https://maps.google.com/maps?q=Alexandria%2C%20Egypt&t=&z=12&ie=UTF8&iwloc=&output=embed" title="{t(lang,'common.mapTitle')}" loading="lazy"></iframe>
    </aside>
  </div>
</section>
</main>
"""
    html += footer(lang, base) + whatsapp_widget(lang, base) + scripts(base)
    write(f"{lang}/contact.html", html)


def build_legal(lang, kind):
    base = "../"
    path = f"/{lang}/{kind}.html"
    other = "en" if lang == "ar" else "ar"
    is_privacy = kind == "privacy"
    title = (t(lang, "footer.privacy") if is_privacy else t(lang, "footer.terms")) + " | " + t(lang, "brand")
    desc = title
    if lang == "ar":
        body = ("""<p>بنحترم خصوصيتك. الموقع بيجمع بس البيانات اللي بتدخلها بنفسك في نموذج التواصل أو النشرة البريدية (الاسم، الموبايل، البريد الإلكتروني) عشان نقدر نرد على استفسارك.</p>
<p>مش بنبيع بياناتك أو نشاركها مع أطراف تالتة لأغراض تسويقية. ممكن نستخدم أدوات تحليل زيارات لتحسين الموقع.</p>
<p>لو عايز تحذف بياناتك من عندنا، ابعتلنا على البريد الإلكتروني وهنتصرف خلال أيام عمل قليلة.</p>"""
                if is_privacy else
                """<p>المعلومات المعروضة على الموقع (الأسعار، المساحات، أنظمة السداد، مواعيد التسليم) استرشادية وقابلة للتغيير حسب تحديثات المطورين وتوافر الوحدات، وميعتبرش أي منها إيجابًا أو التزامًا تعاقديًا.</p>
<p>إيليت للتسويق العقاري بتعمل كوسيط تسويقي، والتعاقد النهائي بيتم مباشرة مع الشركة المطورة وبالشروط المكتوبة في العقد.</p>
<p>الأسماء والعلامات التجارية للمشاريع والمطورين مملوكة لأصحابها، وبتُستخدم هنا لأغراض التعريف فقط.</p>""")
    else:
        body = ("""<p>We respect your privacy. This site only collects the details you enter yourself in the contact form or newsletter (name, phone, email) so that we can answer your enquiry.</p>
<p>We do not sell your data or share it with third parties for marketing. We may use analytics tools to improve the site.</p>
<p>If you'd like your data removed, email us and we'll action it within a few working days.</p>"""
                if is_privacy else
                """<p>Information shown on this site (prices, areas, payment plans, delivery dates) is indicative and subject to change based on developer updates and availability. Nothing here constitutes an offer or a contractual commitment.</p>
<p>Elite Real Estate acts as a marketing intermediary; the final contract is signed directly with the developer under the terms written into that contract.</p>
<p>Project and developer names and trademarks belong to their owners and are used here for identification purposes only.</p>""")

    html = head(lang, title, desc, path, base)
    html += header(lang, base, "", f"{base}{other}/{kind}.html")
    html += f"""<main>
<section class="page-hero">
  <div class="page-hero__media"><img src="{base}{img("assets/img/brand/page.svg")}" alt="" width="1920" height="1080"></div>
  <div class="wrap"><h1>{title.split(' | ')[0]}</h1></div>
</section>
<section class="section"><div class="wrap prose">{body}<p class="disclaimer">{t(lang,'disclaimer')}</p></div></section>
</main>
"""
    html += footer(lang, base) + whatsapp_widget(lang, base) + scripts(base)
    write(f"{lang}/{kind}.html", html)


# --------------------------------------------------------------------------
# property valuation (same fields and flow as the Aqarmap estimate tool)
# --------------------------------------------------------------------------
VAL_FINISHES = ["extra-super-lux", "super-lux", "lux", "semi", "core"]
VAL_VIEWS = [  # id in valuation-data.json features, ar, en
    ("main-street", "شارع رئيسي", "Main street"),
    ("garden", "جنينة", "Garden"),
    ("side-street", "شارع فرعي", "Side street"),
    ("sea-view", "البحر / النيل", "Sea / Nile"),
    ("corner", "ناصية", "Corner"),
]
VAL_INTENTS = [
    ("own", "لدي عقار بهذه المواصفات", "I own a property with these specs"),
    ("buy", "أريد شراء عقار بهذه المواصفات", "I want to buy a property with these specs"),
]
VAL_COUNTRIES = [  # iso, dial, ar, en
    ("eg", "20", "مصر", "Egypt"), ("sa", "966", "السعودية", "Saudi Arabia"),
    ("ae", "971", "الإمارات", "United Arab Emirates"), ("kw", "965", "الكويت", "Kuwait"),
    ("qa", "974", "قطر", "Qatar"), ("bh", "973", "البحرين", "Bahrain"),
    ("om", "968", "عُمان", "Oman"), ("jo", "962", "الأردن", "Jordan"),
    ("lb", "961", "لبنان", "Lebanon"), ("ly", "218", "ليبيا", "Libya"),
    ("iq", "964", "العراق", "Iraq"), ("sd", "249", "السودان", "Sudan"),
    ("gb", "44", "المملكة المتحدة", "United Kingdom"), ("de", "49", "ألمانيا", "Germany"),
    ("fr", "33", "فرنسا", "France"), ("it", "39", "إيطاليا", "Italy"),
    ("us", "1", "الولايات المتحدة", "United States"), ("ca", "1", "كندا", "Canada"),
]

VAL_TEXT = {
    "ar": {
        "title": "التقييم العقاري | إيليت للتسويق العقاري",
        "desc": "حدد المنطقة والمساحة والتشطيب واعرف سعر الشقة التقريبي بناءً على بيانات أسعار الوحدات في السوق.",
        "h1": "أداة التقييم العقاري من إيليت",
        "lead": "حدد المنطقة والمساحة والتشطيب واعرف سعر الشقة التقريبي بناءً على بيانات آلاف العقارات المعروضة في السوق",
        "secArea": "بيانات المنطقة", "secProp": "بيانات العقار",
        "city": "الرجاء اختيار المدينة", "zone": "الرجاء اختيار المنطقة",
        "area": "المساحة الإجمالية", "sqm": "متر²",
        "finish": "التشطيب", "view": "الإطلالة", "intent": "هدف استخدامك للخدمة؟",
        "reg1": "للحصول على التقييم، يرجى التسجيل في الخدمة",
        "reg2": "سيتواصل معك أحد خبراء إيليت لمراجعة التقييم معك",
        "name": "الإسم", "phone": "التليفون", "email": "البريد الإلكتروني",
        "submit": "إحسب سعر العقار", "country": "كود الدولة",
        "privacy": "بياناتك تُستخدم فقط للتواصل معك بخصوص هذا التقييم.",
    },
    "en": {
        "title": "Property Valuation | Elite Real Estate",
        "desc": "Choose the area, size and finishing and get an approximate apartment price based on current market listing data.",
        "h1": "Elite Property Valuation Tool",
        "lead": "Choose the area, size and finishing and get an approximate apartment price based on data from thousands of properties listed on the market",
        "secArea": "Location details", "secProp": "Property details",
        "city": "Please select a city", "zone": "Please select an area",
        "area": "Total area", "sqm": "m²",
        "finish": "Finishing", "view": "View", "intent": "Why are you using this service?",
        "reg1": "To get your valuation, please register for the service",
        "reg2": "An Elite property advisor will contact you to review the valuation with you",
        "name": "Name", "phone": "Phone", "email": "Email",
        "submit": "Calculate property price", "country": "Country code",
        "privacy": "Your details are only used to contact you about this valuation.",
    },
}

VAL_JS_TEXT = {
    "ar": {
        "errRegion": "اختار المدينة", "errZone": "اختار المنطقة",
        "errArea": "اكتب مساحة بين 25 و 2000 متر", "errFinish": "اختار التشطيب",
        "errIntent": "اختار هدف استخدامك للخدمة", "errName": "اكتب الإسم",
        "errPhone": "رقم التليفون غير صحيح", "errEmail": "البريد الإلكتروني غير صحيح",
        "calculating": "جاري حساب السعر...",
        "resultTitle": "السعر التقريبي لعقارك", "apartment": "شقة", "sqm": "م²", "currency": "جنيه",
        "low": "أقل سعر متوقع", "high": "أعلى سعر متوقع", "mid": "السعر التقديري",
        "perSqm": "سعر المتر لعقارك", "zoneSqm": "متوسط سعر المتر في المنطقة",
        "rent": "الإيجار الشهري المتوقع", "rentSeason": "إيجار الموسم المتوقع",
        "compareTitle": "مقارنة سعر المتر في {region}", "perSqmUnit": "جنيه / م²",
        "similarTitle": "وحدات معروضة لدى إيليت في نفس المنطقة", "similarAll": "كل الوحدات",
        "again": "قيّم عقار آخر", "talk": "راجع التقييم مع خبير",
        "sentOk": "تم تسجيل طلبك، وهيتواصل معاك فريق إيليت قريب.",
        "updated": "آخر تحديث لبيانات الأسعار: {date}",
        "disclaimer": "التقييم استرشادي ومبني على متوسطات أسعار السوق المتاحة لدى إيليت، ولا يُعد تقييماً رسمياً. السعر الفعلي بيتأثر بالدور وحالة العقار والموقف القانوني.",
        "waMsg": "السلام عليكم، عملت تقييم لشقة {area} م² في {zone} والسعر التقريبي طلع {value} جنيه. عايز أراجع التقييم مع حد من فريق إيليت.",
        "noResults": "لا توجد نتائج", "search": "ابحث...",
    },
    "en": {
        "errRegion": "Select a city", "errZone": "Select an area",
        "errArea": "Enter an area between 25 and 2000 m²", "errFinish": "Select the finishing",
        "errIntent": "Select why you're using the service", "errName": "Enter your name",
        "errPhone": "Enter a valid phone number", "errEmail": "Enter a valid email address",
        "calculating": "Calculating price...",
        "resultTitle": "Your property's approximate price", "apartment": "Apartment", "sqm": "m²", "currency": "EGP",
        "low": "Lowest expected price", "high": "Highest expected price", "mid": "Estimated price",
        "perSqm": "Price per m² for your property", "zoneSqm": "Average price per m² in the area",
        "rent": "Expected monthly rent", "rentSeason": "Expected seasonal rent",
        "compareTitle": "Price per m² across {region}", "perSqmUnit": "EGP / m²",
        "similarTitle": "Elite listings in the same area", "similarAll": "All properties",
        "again": "Value another property", "talk": "Review it with an advisor",
        "sentOk": "Your request is registered. The Elite team will contact you shortly.",
        "updated": "Price data last updated: {date}",
        "disclaimer": "This is an indicative estimate based on market averages held by Elite, not an official appraisal. The final price also depends on floor, condition and legal status.",
        "waMsg": "Hello, I valued a {area} m² apartment in {zone} and the approximate price came to EGP {value}. I'd like to review it with the Elite team.",
        "noResults": "No results", "search": "Search...",
    },
}


def build_valuation(lang):
    base = "../"
    path = f"/{lang}/valuation.html"
    other = "en" if lang == "ar" else "ar"
    T = VAL_TEXT[lang]
    D = load("valuation-data.json")
    ar = lang == "ar"

    regions = "".join(f'<option value="{r["id"]}">{r[lang]}</option>' for r in D["regions"])
    fin_by_id = {f["id"]: f for f in D["finishes"]}
    finishes = "".join(f'<option value="{fid}">{fin_by_id[fid][lang]}</option>' for fid in VAL_FINISHES)
    views = "".join(
        f'<li role="option" aria-selected="false" data-value="{vid}" tabindex="-1">{a if ar else e}</li>'
        for vid, a, e in VAL_VIEWS
    )
    intents = "".join(f'<option value="{iid}">{a if ar else e}</option>' for iid, a, e in VAL_INTENTS)
    countries = "".join(
        f'<li role="option" aria-selected="{"true" if iso == "eg" else "false"}" data-iso="{iso}" data-dial="{dial}" tabindex="-1">'
        f'<img src="https://flagcdn.com/24x18/{iso}.png" alt="" width="24" height="18" loading="lazy">'
        f'<span>{an if ar else en}</span><span class="vx-dial" dir="ltr">+{dial}</span></li>'
        for iso, dial, an, en in VAL_COUNTRIES
    )
    caret = '<svg class="vx-caret" viewBox="0 0 12 12" aria-hidden="true"><path d="M2.5 4.5 6 8l3.5-3.5" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>'

    ld = [{
        "@context": "https://schema.org", "@type": "WebApplication", "name": T["title"],
        "applicationCategory": "FinanceApplication", "operatingSystem": "Web", "url": f"{SITE_URL}{path}",
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EGP"},
        "provider": {"@type": "RealEstateAgent", "name": t(lang, "brand"), "telephone": "+" + PHONE_INTL, "email": EMAIL},
    }]

    cfg = {
        "lang": lang, "apiBase": f"{base}api/", "base": base,
        "propertiesSrc": f"{base}data/properties.js",
        "waNumber": PHONE_INTL, "t": VAL_JS_TEXT[lang],
    }

    html = head(lang, T["title"], T["desc"], path, base, ld)
    html = html.replace("</head>", f'<link rel="stylesheet" href="{base}assets/css/valuation.css?v=3">\n</head>', 1)
    html += header(lang, base, "valuation", f"{base}{other}/valuation.html")
    html += f"""<main>
<section class="page-hero page-hero--val">
  <div class="page-hero__media"><img src="{base}{img("assets/img/brand/page.svg")}" alt="" width="1920" height="1080"></div>
  <div class="wrap">
    <nav class="breadcrumbs"><a href="{base}{lang}/index.html">{t(lang,'breadcrumb.home')}</a> <span>/</span> <span>{t(lang,'nav.valuation')}</span></nav>
    <h1>{T['h1']}</h1>
    <p>{T['lead']}</p>
  </div>
</section>

<section class="vx" id="vx">
  <form class="vx-form" id="vx-form" novalidate>
    <div class="vx-sec">
      <h2 class="vx-sec__title">{T['secArea']}</h2>
      <div class="vx-col">
        <div class="vx-f">
          <div class="vx-select">
            <select id="vx-region" name="region" aria-label="{T['city']}"><option value="">{T['city']}</option>{regions}</select>{caret}
          </div>
          <p class="vx-err" role="alert"></p>
        </div>
        <div class="vx-f" id="vx-zone-wrap" hidden>
          <div class="vx-select">
            <select id="vx-zone" name="zone" aria-label="{T['zone']}"><option value="">{T['zone']}</option></select>{caret}
          </div>
          <p class="vx-err" role="alert"></p>
        </div>
      </div>
    </div>

    <div class="vx-sec">
      <h2 class="vx-sec__title">{T['secProp']}</h2>
      <div class="vx-col">
        <div class="vx-f">
          <div class="vx-group">
            <input id="vx-area" name="area" type="number" min="25" max="2000" step="1" inputmode="numeric" placeholder="{T['area']}" aria-label="{T['area']}">
            <span class="vx-addon">{T['sqm']}</span>
          </div>
          <p class="vx-err" role="alert"></p>
        </div>
        <div class="vx-f">
          <div class="vx-select">
            <select id="vx-finish" name="finish" aria-label="{T['finish']}"><option value="">{T['finish']}</option>{finishes}</select>{caret}
          </div>
          <p class="vx-err" role="alert"></p>
        </div>
        <div class="vx-f">
          <div class="vx-multi" id="vx-view">
            <button type="button" class="vx-multi__btn" aria-haspopup="listbox" aria-expanded="false" aria-label="{T['view']}">
              <span class="vx-multi__chips"><span class="vx-multi__ph">{T['view']}</span></span>
              <svg class="vx-tri" viewBox="0 0 10 6" aria-hidden="true"><path d="M0 0h10L5 6z" fill="currentColor"/></svg>
            </button>
            <ul class="vx-menu" role="listbox" aria-multiselectable="true" hidden>{views}</ul>
          </div>
        </div>
        <div class="vx-f">
          <div class="vx-select">
            <select id="vx-intent" name="intent" aria-label="{T['intent']}"><option value="">{T['intent']}</option>{intents}</select>{caret}
          </div>
          <p class="vx-err" role="alert"></p>
        </div>
      </div>
    </div>

    <div class="vx-sec vx-sec--last">
      <p class="vx-reg">{T['reg1']}<br>{T['reg2']}</p>
      <div class="vx-col">
        <div class="vx-f">
          <input id="vx-name" name="name" autocomplete="name" placeholder="{T['name']}" aria-label="{T['name']}">
          <p class="vx-err" role="alert"></p>
        </div>
        <div class="vx-f">
          <div class="vx-tel" id="vx-tel">
            <button type="button" class="vx-tel__btn" aria-haspopup="listbox" aria-expanded="false" aria-label="{T['country']}">
              <img src="https://flagcdn.com/24x18/eg.png" alt="" width="24" height="18"><svg class="vx-tri" viewBox="0 0 10 6" aria-hidden="true"><path d="M0 0h10L5 6z" fill="currentColor"/></svg>
            </button>
            <input id="vx-phone" name="phone" type="tel" inputmode="tel" autocomplete="tel-national" placeholder="{T['phone']}" aria-label="{T['phone']}">
            <ul class="vx-menu vx-menu--tel" role="listbox" hidden>{countries}</ul>
          </div>
          <p class="vx-err" role="alert"></p>
        </div>
        <div class="vx-f">
          <input id="vx-email" name="email" type="email" dir="ltr" autocomplete="email" placeholder="{T['email']}" aria-label="{T['email']}">
          <p class="vx-err" role="alert"></p>
        </div>
      </div>
      <button class="vx-submit" type="submit"><span>{T['submit']}</span></button>
      <p class="vx-privacy">{T['privacy']}</p>
    </div>
  </form>

  <div class="vx-result" id="vx-result" hidden tabindex="-1"></div>
</section>
</main>
"""
    extra = (
        f'<script>window.ELITE_VAL = {json.dumps(cfg, ensure_ascii=False)};</script>\n'
        f'<script src="{base}assets/js/valuation-data.js?v=3"></script>\n'
        f'<script src="{base}assets/js/valuation.js?v=3"></script>'
    )
    html += footer(lang, base) + whatsapp_widget(lang, base) + scripts(base, extra)
    write(f"{lang}/valuation.html", html)


def build_router():
    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Elite Real Estate | Handpicked Properties Across Egypt</title>
<meta name="description" content="Elite Real Estate - handpicked properties across Egypt. Arabic and English.">
<link rel="canonical" href="{site}/en/index.html">
<link rel="alternate" hreflang="ar" href="{site}/ar/index.html">
<link rel="alternate" hreflang="en" href="{site}/en/index.html">
<link rel="alternate" hreflang="x-default" href="{site}/en/index.html">
<link rel="icon" type="image/png" sizes="192x192" href="assets/img/brand/favicon-192.png">
<script>
  (function () {{
    var stored = null;
    try {{ stored = localStorage.getItem("elite-lang"); }} catch (e) {{}}
    var lang = stored || ((navigator.language || "en").toLowerCase().indexOf("ar") === 0 ? "ar" : "en");
    location.replace(lang + "/index.html");
  }})();
</script>
<meta http-equiv="refresh" content="0; url=en/index.html">
<style>body{{font-family:Arial,sans-serif;background:#08192a;color:#fff;display:grid;place-items:center;height:100vh;margin:0;gap:14px}}a{{color:#cfa96d}}</style>
</head>
<body>
  <p>Elite Real Estate</p>
  <p><a href="ar/index.html">العربية</a> &nbsp;|&nbsp; <a href="en/index.html">English</a></p>
</body>
</html>
""".replace("{site}", SITE_URL)
    write("index.html", html)


def build_data_mirrors():
    """JS mirrors so the site also works when opened from the file system."""
    props = json.loads(json.dumps(PROPERTIES, ensure_ascii=False))
    for p in props:
        p["image"] = img(p["image"])
    projs = json.loads(json.dumps(PROJECTS, ensure_ascii=False))
    for p in projs:
        p["hero"] = img(p["hero"])
        p["gallery"] = [img(g) for g in p["gallery"]]
    write("data/properties.js", "window.ELITE_PROPERTIES = " + json.dumps(props, ensure_ascii=False, separators=(",", ":")) + ";\n")
    write("data/projects.js", "window.ELITE_PROJECTS = " + json.dumps(projs, ensure_ascii=False) + ";\n")


SAHEL_SLUGS = []


def build_sitemap():
    urls = []
    for lang in LANGS:
        for page in ["index.html", "properties.html", "projects.html", "about.html", "contact.html", "valuation.html"]:
            urls.append((f"/{lang}/{page}", "1.0" if page == "index.html" else "0.8"))
        for pr in PROJECTS:
            urls.append((f"/{lang}/projects/{pr['slug']}.html", "0.9"))
        urls.append((f"/{lang}/sahel-map.html", "0.8"))
        for slug in SAHEL_SLUGS:
            urls.append((f"/{lang}/sahel/{slug}.html", "0.7"))
        for page in ["privacy.html", "terms.html"]:
            urls.append((f"/{lang}/{page}", "0.2"))

    body = ""
    for loc, prio in urls:
        other = "/en/" if loc.startswith("/ar/") else "/ar/"
        alt = loc.replace("/ar/", other, 1) if loc.startswith("/ar/") else loc.replace("/en/", other, 1)
        body += f"""  <url>
    <loc>{SITE_URL}{loc}</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>{prio}</priority>
    <xhtml:link rel="alternate" hreflang="{'ar' if loc.startswith('/ar/') else 'en'}" href="{SITE_URL}{loc}"/>
    <xhtml:link rel="alternate" hreflang="{'en' if loc.startswith('/ar/') else 'ar'}" href="{SITE_URL}{alt}"/>
  </url>
"""
    write("sitemap.xml", f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
{body}</urlset>
""")
    write("robots.txt", f"""User-agent: *
Allow: /
Disallow: /admin/
Disallow: /*/property.html

Sitemap: {SITE_URL}/sitemap.xml
""")


def main():
    # Remove stale generated project pages after changing the public project allowlist.
    for lang in LANGS:
        shutil.rmtree(os.path.join(ROOT, lang, "projects"), ignore_errors=True)
        shutil.rmtree(os.path.join(ROOT, lang, "sahel"), ignore_errors=True)
    build_images()
    build_data_mirrors()
    build_router()
    for lang in LANGS:
        build_home(lang)
        build_properties(lang)
        build_property_detail(lang)
        build_projects_index(lang)
        build_about(lang)
        build_contact(lang)
        build_valuation(lang)
        build_legal(lang, "privacy")
        build_legal(lang, "terms")
        for pr in PROJECTS:
            build_project_page(lang, pr)
        sahel_map.build(sys.modules[__name__], lang)
    _, sahel_regions = sahel_map._compile(sys.modules[__name__])
    SAHEL_SLUGS[:] = [c["slug"] for r in sahel_regions for c in r["compounds"]]
    idx = sahel_compounds.compounds_index(sahel_regions)
    write("data/compounds.json", json.dumps(idx, ensure_ascii=False, indent=1) + "\n")
    write("data/compounds.js", "window.ELITE_COMPOUNDS = " + json.dumps(idx, ensure_ascii=False, separators=(",", ":")) + ";\n")
    build_sitemap()
    build_image_manifest()
    total = len(LANGS) * (10 + len(PROJECTS) + len(SAHEL_SLUGS)) + 1
    print(f"Built {total} pages for {len(PROJECTS)} projects and {len(PROPERTIES)} properties.")


if __name__ == "__main__":
    main()
