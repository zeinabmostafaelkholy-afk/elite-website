#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generates the clean logo assets used across the site from the master artwork.

Input : assets/img/brand/logo-master.png   (original supplied file)
Output: assets/img/brand/logo.png          full stacked lockup, denoised + trimmed
        assets/img/brand/logo-mark.png     the "E + towers" monogram only
        assets/img/brand/logo-wordmark.png  ELITE / REAL ESTATE only
        assets/img/brand/logo-footer.png   horizontal lockup for the footer
        assets/img/brand/logo-white.png    white version of the full lockup
        assets/img/brand/favicon-*.png     square icons

Run:  python3 tools/make_logo_assets.py
"""

import os
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRAND = os.path.join(ROOT, "assets", "img", "brand")
MASTER = os.path.join(BRAND, "logo-master.png")


def load_master():
    im = Image.open(MASTER).convert("RGBA")
    return im


def denoise(im, min_frac=0.00002):
    """Drop tiny specks (scanner dust) from the alpha channel."""
    a = np.array(im.split()[-1])
    mask = a > 40
    lbl, n = ndimage.label(mask)
    if n == 0:
        return im
    sizes = ndimage.sum(mask, lbl, range(1, n + 1))
    keep = np.zeros(n + 1, dtype=bool)
    min_px = max(200, int(mask.size * min_frac))
    for i, s in enumerate(sizes, start=1):
        keep[i] = s >= min_px
    clean = keep[lbl]
    arr = np.array(im)
    arr[..., 3] = np.where(clean, arr[..., 3], 0)
    return Image.fromarray(arr, "RGBA")


def trim(im, pad=0):
    box = im.split()[-1].getbbox()
    im = im.crop(box)
    if pad:
        w, h = im.size
        out = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
        out.paste(im, (pad, pad))
        im = out
    return im


def row_gaps(im, min_gap=40):
    a = np.array(im.split()[-1])
    rows = a.sum(axis=1)
    gaps, start, inrun = [], 0, False
    for i, v in enumerate(rows):
        if v == 0 and not inrun:
            start, inrun = i, True
        elif v != 0 and inrun:
            if i - start >= min_gap:
                gaps.append((start, i))
            inrun = False
    return gaps


def blacken(im):
    """Force pure black ink, keep antialiasing in alpha."""
    arr = np.array(im).astype(np.uint16)
    a = arr[..., 3]
    # darkness of the ink also contributes to coverage
    lum = arr[..., :3].mean(axis=2)
    cov = np.clip(a * (255 - lum) / 255.0 + a * 0.0, 0, 255)
    cov = np.where(a > 0, np.maximum(cov, a * 0.35), 0)
    out = np.zeros_like(arr, dtype=np.uint8)
    out[..., 3] = cov.astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def tint(im, rgb):
    arr = np.array(im)
    arr[..., 0], arr[..., 1], arr[..., 2] = rgb
    return Image.fromarray(arr, "RGBA")


def fit(im, max_w=None, max_h=None):
    w, h = im.size
    s = min(
        max_w / w if max_w else 9e9,
        max_h / h if max_h else 9e9,
    )
    return im.resize((max(1, int(w * s)), max(1, int(h * s))), Image.LANCZOS)


def main():
    master = denoise(load_master())
    master = blacken(master)
    full = trim(master)
    full.save(os.path.join(BRAND, "logo.png"))
    print("logo.png          ", full.size)

    gaps = row_gaps(full, min_gap=80)
    if not gaps:
        raise SystemExit("could not split the lockup")
    split_at = gaps[0][0] + (gaps[0][1] - gaps[0][0]) // 2

    mark = trim(full.crop((0, 0, full.size[0], split_at)))
    word = trim(full.crop((0, split_at, full.size[0], full.size[1])))
    mark.save(os.path.join(BRAND, "logo-mark.png"))
    word.save(os.path.join(BRAND, "logo-wordmark.png"))
    print("logo-mark.png     ", mark.size)
    print("logo-wordmark.png ", word.size)

    # ---- horizontal lockup: monogram on the left, wordmark on the right ----
    H = 260
    m = fit(mark, max_h=H)
    # wordmark reads smaller so the two feel optically balanced
    w = fit(word, max_h=int(H * 0.62))
    gap = int(H * 0.30)
    pad = int(H * 0.06)
    lw = m.size[0] + gap + w.size[0] + pad * 2
    lh = H + pad * 2
    lock = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    lock.alpha_composite(m, (pad, pad + (H - m.size[1]) // 2))
    lock.alpha_composite(w, (pad + m.size[0] + gap, pad + (H - w.size[1]) // 2))
    lock = trim(lock, pad=6)
    lock.save(os.path.join(BRAND, "logo-footer.png"))
    print("logo-footer.png   ", lock.size)

    # ---- white variants (no CSS filter needed → crisper thin strokes) ----
    tint(fit(full, max_h=900), (255, 255, 255)).save(
        os.path.join(BRAND, "logo-white.png"))
    tint(fit(lock, max_h=320), (255, 255, 255)).save(
        os.path.join(BRAND, "logo-footer-white.png"))
    tint(fit(mark, max_h=512), (255, 255, 255)).save(
        os.path.join(BRAND, "logo-mark-white.png"))

    # ---- square icons on the brand navy, for favicon / whatsapp avatar ----
    for size in (192, 512):
        canvas = Image.new("RGBA", (size, size), (8, 25, 42, 255))
        mk = fit(tint(mark, (255, 255, 255)), max_h=int(size * 0.62),
                 max_w=int(size * 0.72))
        canvas.alpha_composite(
            mk, ((size - mk.size[0]) // 2, (size - mk.size[1]) // 2))
        canvas.save(os.path.join(BRAND, f"favicon-{size}.png"))
    print("favicon-192/512.png written")

    # compact copies actually shipped to the browser
    fit(full, max_h=520).save(os.path.join(BRAND, "logo.png"))
    print("done")


if __name__ == "__main__":
    main()
