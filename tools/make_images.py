# -*- coding: utf-8 -*-
"""
Elite Real Estate — image tool (needs Pillow with raqm for Arabic shaping).

  1. assets/img/compounds/<slug>.jpg      one cover per compound on the Sahel map
                                          (name in Arabic + English, KM, Elite logo, "illustrative image")
  2. assets/img/brand/fallback.jpg        shown automatically when any image fails to load
  3. Temporary SVG artwork used by units and public projects is replaced by JPG covers
     and data/properties.json / data/projects.json are pointed at the new files.
  4. Photos over ~1.5 MB are resized (max 2200 px) and recompressed.

Real photos are never touched (only oversized ones are recompressed, in place).
    python3 tools/make_images.py
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import sahel_compounds as sc  # noqa: E402

AR_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
AR_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
EN_SERIF = "/usr/share/fonts/truetype/google-fonts/Lora-Variable.ttf"
LOGO = os.path.join(ROOT, "assets/img/brand/logo-footer-white.png")
NAVY, NAVY2, TEAL, BRASS = (13, 36, 56), (20, 49, 72), (29, 86, 112), (207, 169, 109)
RAQM = ImageFont.Layout.RAQM
W, H = 1200, 800


def font(path, size):
    return ImageFont.truetype(path, size, layout_engine=RAQM)


def fit(draw, text, path, size, max_w, min_size=28, **kw):
    while size > min_size:
        f = font(path, size)
        if draw.textlength(text, font=f, **kw) <= max_w:
            return f
        size -= 4
    return font(path, min_size)


def background(seed=0):
    img = Image.new("RGB", (W, H), NAVY)
    px = ImageDraw.Draw(img)
    for y in range(H):  # sky
        t = y / H
        px.line([(0, y), (W, y)], fill=tuple(int(NAVY[i] + (NAVY2[i] - NAVY[i]) * t) for i in range(3)))
    horizon = int(H * 0.75)
    sea = Image.new("RGB", (W, H - horizon))
    sd = ImageDraw.Draw(sea)
    for y in range(H - horizon):
        t = y / (H - horizon)
        sd.line([(0, y), (W, y)], fill=tuple(int(TEAL[i] + (NAVY[i] - TEAL[i]) * t) for i in range(3)))
    img.paste(sea, (0, horizon))
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    cx = int(W * (0.72 + 0.06 * ((seed % 5) - 2) / 2))
    gd.ellipse([cx - 210, horizon - 230, cx + 210, horizon + 190], fill=(70, 58, 38))
    glow = glow.filter(ImageFilter.GaussianBlur(90))
    img = Image.composite(img, img, Image.new("L", (W, H), 255))
    from PIL import ImageChops
    img = ImageChops.add(img, glow)
    d = ImageDraw.Draw(img, "RGBA")
    for k, off in enumerate((46, 104, 176)):
        d.line([(0, horizon + off), (W, horizon + off)], fill=(207, 233, 236, 46 - 10 * k), width=2)
    d.line([(0, horizon), (W, horizon)], fill=(207, 233, 236, 70), width=2)
    return img


def cover(out, name_ar, name_en, sub_ar="", sub_en="", seed=0):
    img = background(seed).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    logo = Image.open(LOGO).convert("RGBA")
    lw = 250
    logo = logo.resize((lw, int(logo.height * lw / logo.width)), Image.LANCZOS)
    img.alpha_composite(logo, ((W - lw) // 2, 70))

    y = 205
    f_ar = fit(d, name_ar, AR_BOLD, 84, 1000, language="ar", direction="rtl") if name_ar else None
    if f_ar:
        d.text((W // 2, y), name_ar, font=f_ar, fill=(255, 255, 255, 255), anchor="ma", language="ar", direction="rtl")
        y += int(f_ar.size * 1.55)
    f_en = fit(d, name_en, EN_SERIF, 50, 1000, min_size=26)
    d.text((W // 2, y), name_en, font=f_en, fill=BRASS + (255,), anchor="ma")
    y += int(f_en.size * 1.6)
    d.line([(W // 2 - 60, y), (W // 2 + 60, y)], fill=BRASS + (200,), width=2)
    y += 26
    if sub_ar:
        f = fit(d, sub_ar, AR_REG, 34, 1000, language="ar", direction="rtl")
        d.text((W // 2, y), sub_ar, font=f, fill=(255, 255, 255, 215), anchor="ma", language="ar", direction="rtl")
        y += int(f.size * 1.5)
    if sub_en:
        f = fit(d, sub_en, EN_SERIF, 30, 1000, min_size=20)
        d.text((W // 2, y), sub_en, font=f, fill=(255, 255, 255, 170), anchor="ma")

    cap_ar, cap_en = "صورة توضيحية", "Illustrative image"
    fa, fe = font(AR_REG, 24), font(EN_SERIF, 20)
    wa_, we_ = d.textlength(cap_ar, font=fa, language="ar", direction="rtl"), d.textlength(cap_en, font=fe)
    pw = int(wa_ + we_ + 74)
    x0, y0 = (W - pw) // 2, H - 84
    d.rounded_rectangle([x0, y0, x0 + pw, y0 + 46], radius=23, fill=(8, 25, 42, 150), outline=(255, 255, 255, 60))
    d.text((x0 + 22 + we_ + 30 + wa_, y0 + 10), cap_ar, font=fa, fill=(255, 255, 255, 220), anchor="ra", language="ar", direction="rtl")
    d.text((x0 + 22, y0 + 12), cap_en, font=fe, fill=(255, 255, 255, 200), anchor="la")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    img.convert("RGB").save(out, "JPEG", quality=80, optimize=True, progressive=True)


def fallback(out):
    img = background(3).convert("RGBA")
    logo = Image.open(LOGO).convert("RGBA")
    lw = 420
    logo = logo.resize((lw, int(logo.height * lw / logo.width)), Image.LANCZOS)
    img.alpha_composite(logo, ((W - lw) // 2, (H - logo.height) // 2 - 30))
    d = ImageDraw.Draw(img, "RGBA")
    f = font(AR_REG, 28)
    d.text((W // 2, H // 2 + 120), "صورة غير متاحة حاليًا", font=f, fill=(255, 255, 255, 190), anchor="ma", language="ar", direction="rtl")
    img.convert("RGB").save(out, "JPEG", quality=78, optimize=True, progressive=True)


def jload(name):
    with open(os.path.join(ROOT, "data", name), encoding="utf-8") as f:
        return json.load(f)


def jsave(name, obj, indent=1):
    with open(os.path.join(ROOT, "data", name), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent)
        f.write("\n")


def main():
    m = jload("sahel_map.json")
    n = 0
    for r in m["regions"]:
        for c in r["compounds"]:
            slug = c.get("slug") or sc.slugify(c["name"]["en"])
            out = os.path.join(ROOT, "assets/img/compounds", slug + ".jpg")
            cover(out, c["name"]["ar"], c["name"]["en"], f"الكيلو {c['km']} · {r['name']['ar']}",
                  f"KM {c['km']} · {r['name']['en']}", seed=c["km"])
            n += 1
    print(f"{n} compound covers")
    fallback(os.path.join(ROOT, "assets/img/brand/fallback.jpg"))

    # --- units still using temporary SVG artwork ---
    props = jload("properties.json")
    made = 0
    for p in props:
        for key in ("image",):
            path = p.get(key) or ""
            if not path.endswith(".svg"):
                continue
            stem = path[:-4]
            real = next((stem + e for e in (".webp", ".jpg", ".jpeg", ".png") if os.path.exists(os.path.join(ROOT, stem + e))), None)
            if not real:
                real = stem + ".jpg"
                loc = p["location"]
                cover(os.path.join(ROOT, real), p["title"]["ar"], p["title"]["en"], loc["ar"], loc["en"], seed=made)
                made += 1
            p["image"] = real
            if p.get("gallery"):
                p["gallery"] = [real if g == path else g for g in p["gallery"]]
            else:
                p["gallery"] = [real]
            if os.path.exists(os.path.join(ROOT, path)):
                os.remove(os.path.join(ROOT, path))
    jsave("properties.json", props)
    print(f"{made} unit covers")

    # --- public projects still using SVG ---
    projs = jload("projects.json")
    pm = 0
    for pr in projs:
        if pr["slug"] not in sc_public():
            continue
        def fix(path, idx):
            nonlocal pm
            if not path.endswith(".svg"):
                return path
            stem = path[:-4]
            real = next((stem + e for e in (".webp", ".jpg", ".jpeg", ".png") if os.path.exists(os.path.join(ROOT, stem + e))), None)
            if not real:
                real = stem + ".jpg"
                cover(os.path.join(ROOT, real), pr["name"]["ar"], pr["name"]["en"], pr["location"]["ar"], pr["location"]["en"], seed=pm + idx)
                pm += 1
            if os.path.exists(os.path.join(ROOT, path)):
                os.remove(os.path.join(ROOT, path))
            return real
        pr["hero"] = fix(pr["hero"], 0)
        pr["gallery"] = [fix(g, i + 1) for i, g in enumerate(pr["gallery"])]
    jsave("projects.json", projs)
    print(f"{pm} project covers")

    # --- oversized photos ---
    saved = 0
    for dp, _, files in os.walk(os.path.join(ROOT, "assets/img")):
        for fn in files:
            fp = os.path.join(dp, fn)
            if fn.lower().endswith((".jpg", ".jpeg")) and os.path.getsize(fp) > 1_500_000:
                before = os.path.getsize(fp)
                im = Image.open(fp)
                im.thumbnail((2200, 2200), Image.LANCZOS)
                im.convert("RGB").save(fp, "JPEG", quality=82, optimize=True, progressive=True)
                saved += before - os.path.getsize(fp)
                print(f"  compressed {os.path.relpath(fp, ROOT)}: {before/1e6:.1f} MB -> {os.path.getsize(fp)/1e6:.2f} MB")
    print(f"saved {saved/1e6:.1f} MB")


def sc_public():
    return {"the-one-smouha", "ajaza-new-alamein", "creeks-alexandria", "ogami-ras-el-hekma"}


if __name__ == "__main__":
    main()
