# -*- coding: utf-8 -*-
"""
Download every remote image used by the Sahel compound pages into the site itself,
so nothing is loaded from any other website.

    python3 tools/localize_sahel_images.py
    python3 build.py

Reads the compound galleries in data/sahel_units.json and every unit in data/properties.json,
saves images under assets/img/sahel/<compound>/ and rewrites the paths (backups are kept as
data/sahel_units.backup.json and data/properties.backup.json).
Careful: if you edit units in /admin on the live site, download data/properties.json from the server first.
Safe to run again: images already downloaded are skipped.
"""
import json
import os
import shutil
import sys
import time
import urllib.request
from urllib.parse import unquote, urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "sahel_units.json")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"


def ext_of(url):
    e = os.path.splitext(urlparse(url).path)[1].lower()
    return e if e in (".jpg", ".jpeg", ".png", ".webp") else ".webp"


def fetch(url, dest):
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return True
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r, open(dest, "wb") as f:
                shutil.copyfileobj(r, f)
            return os.path.getsize(dest) > 0
        except Exception as e:  # noqa: BLE001
            print(f"   retry {attempt + 1}: {e}")
            time.sleep(1.5)
    if os.path.exists(dest):
        os.remove(dest)
    return False


def localize(urls, folder, prefix):
    out, cache = [], {}
    os.makedirs(os.path.join(ROOT, folder), exist_ok=True)
    for n, u in enumerate(urls, 1):
        if not u.startswith("http"):
            out.append(u)
            continue
        if u in cache:
            out.append(cache[u])
            continue
        rel = f"{folder}/{prefix}-{n}{ext_of(unquote(u))}"
        print(f" - {rel}")
        if fetch(u, os.path.join(ROOT, rel)):
            cache[u] = rel
            out.append(rel)
        else:
            print(f"   !! failed, keeping remote url: {u}")
            out.append(u)
    return out


def main():
    with open(DATA, encoding="utf-8") as f:
        data = json.load(f)
    shutil.copyfile(DATA, os.path.join(ROOT, "data", "sahel_units.backup.json"))
    for slug, comp in data.get("compounds", {}).items():
        folder = f"assets/img/sahel/{slug}"
        if comp.get("gallery"):
            print(f"{slug}: gallery")
            comp["gallery"] = localize(comp["gallery"], folder, "gallery")
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

    pfile = os.path.join(ROOT, "data", "properties.json")
    with open(pfile, encoding="utf-8") as f:
        props = json.load(f)
    shutil.copyfile(pfile, os.path.join(ROOT, "data", "properties.backup.json"))
    left = 0
    for p in props:
        imgs = [p.get("image", "")] + list(p.get("gallery") or [])
        if not any(i.startswith("http") for i in imgs) or not p.get("compound"):
            left += sum(1 for i in imgs if i.startswith("http"))
            continue
        print(f"{p['compound']}: unit {p['id']}")
        new = localize([i for i in imgs if i], f"assets/img/sahel/{p['compound']}", f"unit-{p['id'].lower()}")
        p["image"] = new[0]
        p["gallery"] = new
        left += sum(1 for i in new if i.startswith("http"))
    with open(pfile, "w", encoding="utf-8") as f:
        json.dump(props, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"\nDone. Remote images left: {left}.  Now run:  python3 build.py")
    return 0 if left == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
