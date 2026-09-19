# -*- coding: utf-8 -*-
"""
Add units to a Sahel compound page from unit (property) page links.

Why links: listing sites load a compound's unit list with JavaScript, but each unit's own page
contains all of its data. Open the compound in your browser, copy the unit links, and paste them
into a text file (one per line). Then:

    python3 tools/import_sahel_units.py almaza-bay links.txt
    python3 tools/import_sahel_units.py jamila https://.../property/129370-...  https://.../property/...
    python3 tools/localize_sahel_images.py      # download the photos into the site
    python3 build.py

Units are added to data/properties.json (the same list the admin dashboard edits), linked to the compound.
If the compound only had the "price on request" placeholder, the placeholder is removed.

<compound-slug> is the page name in ar|en/sahel/<slug>.html (e.g. almaza-bay, jamila, alam-al-roum).
Units already in the file (same reference number) are updated, not duplicated.
Nothing from the source site is linked on Elite's pages: only the data and photos are kept.
"""
import html
import json
import os
import re
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "sahel_units.json")
PROPS = os.path.join(ROOT, "data", "properties.json")
sys.path.insert(0, os.path.join(ROOT, "tools"))
import migrate_units as mu  # noqa: E402
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
TYPES = ["townhouse", "twinhouse", "penthouse", "apartment", "chalet", "villa", "duplex", "studio",
         "cabin", "loft", "office", "retail", "medical", "pharmacy", "administrative"]
AMEN = {"garden": "garden", "has roof": "roof", "driver room": "driver", "nanny room": "nanny",
        "kitchen cabinets": "kitchen", "a/c": "ac", "5th row": "row5", "commercial strip": "commercial",
        "clubhouse": "clubhouse", "shared spa": "spa", "shared gym": "gym", "children's play area": "kids",
        "underground parking": "parking", "outdoor pools": "pool", "sea view": "seaView"}


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read().decode("utf-8", "replace")


def text_lines(page):
    page = re.sub(r"(?is)<(script|style|noscript)\b.*?</\1>", " ", page)
    page = re.sub(r"(?i)<br\s*/?>|</(p|div|h\d|li|span|dt|dd|section|a|button)>", "\n", page)
    page = re.sub(r"<[^>]+>", " ", page)
    lines = [re.sub(r"\s+", " ", html.unescape(x)).strip() for x in page.split("\n")]
    return [x for x in lines if x]


def num(s):
    s = re.sub(r"[^\d.]", "", s or "")
    return float(s) if s else 0


def after(lines, label):
    for i, x in enumerate(lines):
        if x.lower() == label.lower() and i + 1 < len(lines):
            return lines[i + 1]
    return ""


def parse(url, page):
    lines = text_lines(page)
    body = "\n".join(lines)
    m = re.search(r"/property/(\d+)", url)
    nid = int(m.group(1)) if m else int(num(after(lines, "Reference No.")))
    title = next((x for x in lines if re.search(r" for (re)?sale in ", x, re.I)), "")
    typ = ""
    for t in TYPES:
        if re.search(r"\b" + t + r"\b", (after(lines, "Property") + " " + title).lower()):
            typ = t
            break
    area_line = next((x for x in lines if re.search(r"^\d[\d,.]*\s*m²?(\s*~\s*\d[\d,.]*\s*m²?)?$", x)), "")
    areas = [int(num(a)) for a in re.findall(r"\d[\d,.]*", area_line)]
    price = mx = 0
    m = re.search(r"Prices Start From\s*([\d,]+)\s*EGP\s*Max Price:?\s*([\d,]+)", body.replace("\n", " "))
    if m:
        price, mx = int(num(m.group(1))), int(num(m.group(2)))
    else:
        m = re.search(r"Price\s*([\d,]{6,})\s*EGP", body.replace("\n", " "))
        price = int(num(m.group(1))) if m else 0
    loc = next((x for x in lines if x.endswith("North Coast-Sahel") and "," in x), "")
    phase = loc.split(",")[0].strip() if loc else ""
    sale = after(lines, "Sale Type").lower()
    sale = "developer" if "developer" in sale else "resale" if "resale" in sale else ""
    fin = after(lines, "Finishing").lower()
    fin = "furnished" if "furnish" in fin else "semi_finished" if "semi" in fin else "finished" if "finish" in fin else ""
    plans = []
    flat = body.replace("\n", " ")
    for m in re.finditer(r"([\d,]+)\s*EGP\s*(quarterly|monthly|semi-annually|annually)\s*([\d.]+)\s*Years?\s*(?:([\d,]+)\s*EGP\s*Down Payment)?", flat, re.I):
        plans.append({"installment": int(num(m.group(1))), "frequency": m.group(2).lower(),
                      "years": float(m.group(3)) if "." in m.group(3) else int(m.group(3)),
                      "down": int(num(m.group(4))) if m.group(4) else None})
    date = re.search(r"delivery[^.]*?by (\d{4}-\d{2}-\d{2})", flat, re.I)
    imgs = []
    head = page.split('logo</a>')[0] if 'logo</a>' in page else page
    for s in re.findall(r'<img[^>]+src="([^"]+/(?:brochure_images|property_image|unlockedProperties|inventory)[^"]+)"', head):
        s = html.unescape(s)
        if "/icons/" in s or s in imgs:
            continue
        imgs.append(s)
    amen = sorted({v for k, v in AMEN.items() if re.search(r"(?m)^" + re.escape(k) + r"\s*$", body, re.I)})
    return {
        "nid": nid, "type": typ or "chalet", "phase": phase,
        "label": re.sub(r"\s+for (re)?sale in .*$", "", title, flags=re.I).strip(),
        "beds": int(num(after(lines, "Bedrooms"))), "baths": int(num(after(lines, "Bathrooms"))),
        "area": areas[0] if areas else 0, "areaMax": areas[1] if len(areas) > 1 else None,
        "price": price, "maxPrice": mx or None, "plans": plans,
        "delivery": after(lines, "Delivery In"), "deliveryDate": date.group(1) if date else "",
        "sale": sale, "finishing": fin, "images": imgs[:12], "amenities": amen,
        "soldOut": bool(re.search(r"(?m)^Sold Out$", body)),
    }


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 1
    slug, rest = argv[1], argv[2:]
    urls = []
    for a in rest:
        if os.path.isfile(a):
            with open(a, encoding="utf-8") as f:
                urls += [x.strip() for x in f if x.strip().startswith("http")]
        else:
            urls.append(a)
    with open(DATA, encoding="utf-8") as f:
        meta = json.load(f).get("compounds", {}).get(slug, {})
    comp = next((c for c in mu.compounds_from_map() if c["slug"] == slug), None)
    if comp is None:
        print(f"unknown compound slug: {slug} (see data/sahel_map.json)")
        return 1
    with open(PROPS, encoding="utf-8") as f:
        props = json.load(f)
    by_id = {p["id"]: i for i, p in enumerate(props)}
    ok = 0
    for url in urls:
        try:
            u = parse(url, get(url))
        except Exception as e:  # noqa: BLE001
            print(f"!! {url}\n   {e}")
            continue
        if u.pop("soldOut") or not u["price"]:
            print(f"-  skipped (sold out / no price): {u['nid']}")
            continue
        rec = mu.scraped_to_property(u, comp, meta)
        if rec["id"] in by_id:
            old = props[by_id[rec["id"]]]
            rec["featured"], rec["order"] = old.get("featured", False), old.get("order")
            props[by_id[rec["id"]]] = rec
        else:
            by_id[rec["id"]] = len(props)
            props.append(rec)
        ok += 1
        print(f"+  {u['nid']}  {u['type']}  {u['beds']} beds  {u['area']} m²  EGP {u['price']:,}  ({len(u['images'])} photos)")
        time.sleep(0.8)
    if ok:
        props = [p for p in props if not (p["id"].startswith("ELC-") and p.get("compound") == slug)]
    with open(PROPS, "w", encoding="utf-8") as f:
        json.dump(props, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"\n{ok} units saved to {slug}. Next: python3 tools/localize_sahel_images.py && python3 build.py")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
