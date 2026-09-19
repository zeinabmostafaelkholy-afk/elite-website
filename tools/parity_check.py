# -*- coding: utf-8 -*-
"""
Checks that the compound pages drawn at build time (build.py -> sahel_compounds.nx_card) and the same
pages redrawn in the browser (assets/js/cards.js) come out identical.
Needs:  pip install playwright beautifulsoup4 && playwright install chromium
    python3 tools/parity_check.py
"""
import http.server
import os
import re
import socketserver
import threading
import urllib.request
from urllib.parse import unquote

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Quiet(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def log_message(self, *a):
        pass


def norm(x):
    return re.sub(r"\s+", " ", x or "").strip()


def summarize(card):
    q = lambda sel: card.select_one(sel)  # noqa: E731
    return {
        "data": {k: card.get(k) for k in ("data-sale", "data-type", "data-beds", "data-price", "data-ask", "data-area")},
        "title": norm(q(".nx-card__title").get_text()),
        "loc": norm(q(".nx-card__loc").get_text()),
        "specs": norm(q(".nx-specs").get_text(" ")),
        "inst": norm(q(".nx-card__inst").get_text()),
        "price": norm(q(".nx-card__price").get_text(" ")),
        "dl": norm((q(".nx-card__dl") or card).get_text(" ")) if q(".nx-card__dl") else "",
        "flag": bool(q(".nx-card__flag")),
        "wa": unquote(q(".nx-round--wa")["href"]),
        "img": (q(".nx-card__media img") or {}).get("src", "") if q(".nx-card__media img") else "",
        "fav": q("[data-fav]")["data-fav"],
        "logo": norm(q(".nx-logo").get_text()),
    }


def main():
    socketserver.ThreadingTCPServer.daemon_threads = True
    srv = socketserver.ThreadingTCPServer(("127.0.0.1", 0), Quiet)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    slugs = sorted(f[:-5] for f in os.listdir(os.path.join(ROOT, "ar/sahel")))
    bad = checked = 0
    with sync_playwright() as p:
        br = p.chromium.launch()
        page = br.new_page()
        page.route("**/*", lambda r: r.continue_() if r.request.url.startswith("http://127.0.0.1") else r.abort())
        for lang in ("ar", "en"):
            for slug in slugs:
                url = f"http://127.0.0.1:{port}/{lang}/sahel/{slug}.html"
                raw = urllib.request.urlopen(url).read().decode("utf-8")
                baked = [summarize(c) for c in BeautifulSoup(raw, "html.parser").select(".nx-card")]
                page.goto(url, wait_until="domcontentloaded")
                live_html = page.evaluate("() => document.querySelector('.nx-grid').outerHTML")
                live = [summarize(c) for c in BeautifulSoup(live_html, "html.parser").select(".nx-card")]
                checked += 1
                if baked != live:
                    bad += 1
                    print(f"MISMATCH {lang}/{slug}: baked {len(baked)} cards, live {len(live)}")
                    for i, (x, y) in enumerate(zip(baked, live)):
                        if x != y:
                            for k in x:
                                if x[k] != y[k]:
                                    print(f"   card {i} {k}:\n     baked={x[k]!r}\n     live ={y[k]!r}")
                            break
        br.close()
    print(f"{checked} pages compared, {bad} mismatches")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
