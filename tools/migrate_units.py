# -*- coding: utf-8 -*-
"""
Elite Real Estate — one-time data migration (safe to run twice).

Before:  units lived in two places
           data/properties.json      (the main listing, joined to compounds by a title regex)
           data/sahel_units.json     (scraped units per compound)
After:   every unit lives in data/properties.json and carries its own  "compound": "<slug>"
         so the admin dashboard, the units page, the compound pages and the map all read one list.

Compounds that still have no units get ONE placeholder unit marked "price on request"
(no area / beds / price) so every compound on the map has something to show and to edit.

    python3 tools/migrate_units.py
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import sahel_compounds as sc  # noqa: E402

TODAY = "2026-09-19"
PUBLIC_PROJECTS = {"the-one-smouha", "ajaza-new-alamein", "creeks-alexandria", "ogami-ras-el-hekma"}
COAST_AR, COAST_EN = "الساحل الشمالي", "North Coast"
FINISH = sc.FINISH


def jload(name):
    with open(os.path.join(ROOT, "data", name), encoding="utf-8") as f:
        return json.load(f)


def jsave(name, obj):
    with open(os.path.join(ROOT, "data", name), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")


I18N = jload("i18n.json")


def type_label(ty, lang):
    v = I18N[lang].get("type." + ty)
    if v:
        return v
    ar, en = sc.TYPE_FALLBACK.get(ty, (ty.title(), ty.title()))
    return ar if lang == "ar" else en


def compounds_from_map():
    m = jload("sahel_map.json")
    out = []
    for r in m["regions"]:
        for c in r["compounds"]:
            c = dict(c)
            c["slug"] = c.get("slug") or sc.slugify(c["name"]["en"])
            c["region"] = r
            out.append(c)
    return out


def delivery_of(u):
    dl = str(u.get("delivery") or "")
    ready = bool(re.search(r"ready|delivered|فوري", dl, re.I)) or (dl.isdigit() and int(dl) <= 2025)
    if ready:
        return {"ar": "استلام فوري", "en": "Ready to move"}
    return {"ar": dl, "en": dl}


def place(name, area, coast):
    parts = []
    for x in (name, area, coast):
        if x and x not in parts:
            parts.append(x)
    return parts


def scraped_to_property(u, comp, extra):
    ty = u["type"]
    tl_ar, tl_en = type_label(ty, "ar"), type_label(ty, "en")
    name_ar, name_en = comp["name"]["ar"], comp["name"]["en"]
    phase = u.get("phase") or ""
    sub_ar, sub_en = phase or name_ar, phase or name_en
    label = u.get("label") or ""
    title_en = f"{label} for sale in {sub_en}" if label else f"{tl_en} for sale in {sub_en}"
    title_ar = f"{tl_ar} للبيع في {sub_ar}" + (f" - {u['beds']} غرف" if u.get("beds") else "")
    area_obj = (extra or {}).get("area") or comp["region"]["name"]
    fin = FINISH.get(u.get("finishing", ""), ("", ""))
    dl = delivery_of(u)
    area_txt = f"{u['area']}" + (f" ~ {u['areaMax']}" if u.get("areaMax") else "")
    beds, baths = u.get("beds") or 0, u.get("baths") or 0
    d_ar = (f"{tl_ar} {beds} غرف في {sub_ar}، {name_ar}. المساحة {area_txt} م² و{baths} حمام"
            + (f"، {fin[0]}" if fin[0] else "")
            + (f"، الاستلام {u.get('deliveryDate') or dl['ar']}." if dl["ar"] else "."))
    d_en = (f"A {beds} bedroom {tl_en.lower()} in {sub_en}, {name_en}. The unit is {area_txt} m² with {baths} bathrooms"
            + (f", {fin[1].lower()}" if fin[1] else "")
            + (f", delivery {u.get('deliveryDate') or dl['en']}." if dl["en"] else "."))
    imgs = [i for i in (u.get("images") or []) if i]
    dev = (extra or {}).get("developer") or {}
    return {
        "id": f"EL-{u['nid']}", "featured": False, "recommended": False, "purpose": "sale", "type": ty,
        "title": {"ar": title_ar, "en": title_en}, "city": "north-coast",
        "location": {"ar": "، ".join(place(name_ar, area_obj["ar"], COAST_AR)), "en": ", ".join(place(name_en, area_obj["en"], COAST_EN))},
        "project": comp.get("project") if comp.get("project") in PUBLIC_PROJECTS else None,
        "compound": comp["slug"], "priceOnRequest": False,
        "price": u.get("price") or 0, "maxPrice": u.get("maxPrice"), "priceUnit": "total",
        "area": u.get("area") or 0, "areaMax": u.get("areaMax"), "beds": beds, "baths": baths, "floor": None,
        "finishing": {"ar": fin[0], "en": fin[1]}, "delivery": dl, "deliveryDate": u.get("deliveryDate") or "",
        "image": imgs[0] if imgs else "", "gallery": imgs,
        "description": {"ar": d_ar, "en": d_en}, "features": list(u.get("amenities") or []), "createdAt": TODAY,
        "saleType": u.get("sale") or "", "phase": phase, "plans": u.get("plans") or [],
        "developer": dev.get("en") or "", "sourceReference": "Sahel compound import",
    }


def placeholder_unit(comp, seq):
    name_ar, name_en = comp["name"]["ar"], comp["name"]["en"]
    area_obj = comp["region"]["name"]
    return {
        "id": f"ELC-{seq:03d}", "featured": False, "recommended": False, "purpose": "sale", "type": "unit",
        "title": {"ar": f"وحدات في {name_ar}", "en": f"Units in {name_en}"}, "city": "north-coast",
        "location": {"ar": "، ".join(place(name_ar, area_obj["ar"], COAST_AR)), "en": ", ".join(place(name_en, area_obj["en"], COAST_EN))},
        "project": comp.get("project") if comp.get("project") in PUBLIC_PROJECTS else None,
        "compound": comp["slug"], "priceOnRequest": True,
        "price": 0, "maxPrice": None, "priceUnit": "total",
        "area": 0, "areaMax": None, "beds": 0, "baths": 0, "floor": None,
        "finishing": {"ar": "", "en": ""}, "delivery": {"ar": "", "en": ""}, "deliveryDate": "",
        "image": f"assets/img/compounds/{comp['slug']}.jpg", "gallery": [],
        "description": {
            "ar": f"وحدات متاحة في {name_ar} عند الكيلو {comp['km']}. المساحات والأسعار وأنظمة السداد متاحة عند الطلب — كلم مستشار إيليت وهيبعتلك كل التفاصيل.",
            "en": f"Units available in {name_en} at KM {comp['km']}. Sizes, prices and payment plans are available on request — contact an Elite advisor for full details.",
        },
        "features": [], "createdAt": TODAY, "saleType": "", "phase": "", "plans": [],
        "developer": "", "sourceReference": "Placeholder — price on request",
        "imageSource": "Illustrative cover generated for the website; not a photograph of the compound.",
    }


def main():
    props = jload("properties.json")
    units_file = jload("sahel_units.json")
    extra = units_file.get("compounds", {})
    comps = compounds_from_map()
    by_slug = {c["slug"]: c for c in comps}
    have = {p["id"] for p in props}

    # 1) link existing properties to their compound (same title rule the map used, most specific alias wins)
    linked = 0
    for p in props:
        if p.get("compound"):
            continue
        if p.get("purpose") != "sale" or p.get("priceUnit", "total") != "total":
            p["compound"] = None
            continue
        title = p["title"]["en"].lower()
        best = None
        for c in comps:
            pats = [re.compile(a) for a in c["match"]]
            ex = [re.compile(e) for e in c.get("exclude", [])]
            hits = [x.search(title) for x in pats]
            hits = [h for h in hits if h]
            if hits and not any(x.search(title) for x in ex):
                score = max(len(h.group(0)) for h in hits)
                if best is None or score > best[0]:
                    best = (score, c["slug"])
        p["compound"] = best[1] if best else None
        linked += 1 if best else 0

    # 2) move scraped units into the main list
    moved = 0
    for slug, ex in extra.items():
        comp = by_slug.get(slug)
        if not comp:
            continue
        for u in ex.get("units", []):
            pid = f"EL-{u['nid']}"
            if pid in have:
                continue
            props.append(scraped_to_property(u, comp, ex))
            have.add(pid)
            moved += 1
        ex["units"] = []  # units now live in properties.json; this file keeps compound details only
    units_file["_about"] = ("Compound details for the Sahel pages (developer, about, payment plan, gallery). "
                            "Units live in data/properties.json and point here with their \"compound\" slug.")
    jsave("sahel_units.json", units_file)

    # 3) every compound gets at least one unit
    counts = {}
    for p in props:
        if p.get("compound"):
            counts[p["compound"]] = counts.get(p["compound"], 0) + 1
    added = 0
    seq = sum(1 for p in props if str(p["id"]).startswith("ELC-"))
    for c in comps:
        if counts.get(c["slug"], 0) == 0:
            seq += 1
            props.append(placeholder_unit(c, seq))
            added += 1

    jsave("properties.json", props)
    print(f"linked {linked} existing units, moved {moved} scraped units, added {added} price-on-request units")
    print(f"total units now: {len(props)}")


if __name__ == "__main__":
    main()
