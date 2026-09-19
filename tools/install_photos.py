#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Installs official developer renders into the site's image slots.

Source images are extracted from the developer sales kits (PDF) supplied by
Elsewhere Developments. Each image is centre-cropped to the aspect ratio the
site expects, resized, and written as JPEG + WebP so build.py picks up the
real photo instead of the placeholder artwork.

Usage:
    python3 tools/install_photos.py <manifest.json>

Manifest format:
    [
      {"src": "/path/to/render.png", "slot": "assets/img/projects/creeks-alexandria-1"},
      {"src": "/path/to/other.png",  "slot": "assets/img/properties/elt-1006",
       "focus": "top"}
    ]

"focus" (optional): top | bottom | center — which part to keep when cropping.
"""

import json
import os
import sys
from PIL import Image

Image.MAX_IMAGE_PIXELS = None

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# target geometry per image family
TARGETS = {
    "projects":   (1600, 1067),   # 3:2
    "properties": (1200, 900),    # 4:3
    "brand":      (1920, 1080),   # 16:9
}


def target_for(slot):
    family = slot.split("/")[-2]
    return TARGETS.get(family, TARGETS["projects"])


def crop_to_ratio(im, ratio, focus="center"):
    w, h = im.size
    cur = w / h
    if abs(cur - ratio) < 0.005:
        return im
    if cur > ratio:                      # too wide -> trim sides
        nw = int(round(h * ratio))
        x = (w - nw) // 2
        return im.crop((x, 0, x + nw, h))
    nh = int(round(w / ratio))           # too tall -> trim top/bottom
    if focus == "top":
        y = 0
    elif focus == "bottom":
        y = h - nh
    else:
        y = (h - nh) // 2
    return im.crop((0, y, w, y + nh))


def install(src, slot, focus="center"):
    tw, th = target_for(slot)
    im = Image.open(src).convert("RGB")
    im = crop_to_ratio(im, tw / th, focus)
    if im.size[0] > tw:
        im = im.resize((tw, th), Image.LANCZOS)
    out = os.path.join(ROOT, slot)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    im.save(out + ".jpg", "JPEG", quality=86, optimize=True, progressive=True)
    im.save(out + ".webp", "WEBP", quality=82, method=6)
    return im.size


def main():
    manifest = json.load(open(sys.argv[1], encoding="utf-8"))
    for entry in manifest:
        size = install(entry["src"], entry["slot"], entry.get("focus", "center"))
        print(f"{entry['slot']}.jpg  {size[0]}x{size[1]}")
    print(f"\n{len(manifest)} images installed. Now run: python3 build.py")


if __name__ == "__main__":
    main()
