#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Artwork generator for Elite Real Estate.

Produces layered SVG scenes (sunset coast, lagoon, skyline, villa street,
masterplan) so no project or listing is ever shown without an image.
Imported by build.py — real photos placed next to these files with the same
base name (.jpg / .webp / .png) always take priority.
"""

import hashlib


def _esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _rand(seed):
    """Deterministic pseudo-random stream from a string seed."""
    h = hashlib.sha256(seed.encode("utf-8")).digest()
    i = [0]

    def nxt(lo, hi):
        b = h[i[0] % len(h)] + h[(i[0] * 7 + 3) % len(h)] * 256
        i[0] += 1
        return lo + (b % max(1, (hi - lo + 1)))
    return nxt


# sky / water palettes: (sky top, sky bottom, sun, water, land)
PALETTES = [
    ("#0b2038", "#e8a15c", "#ffd9a0", "#123449", "#07182a"),   # warm sunset
    ("#0a1c33", "#c98a63", "#ffcf9b", "#0f2e45", "#061626"),   # dusk
    ("#0d2a3d", "#7fb4b8", "#eaf3ef", "#12495a", "#08202c"),   # cool morning
    ("#101d33", "#d0916e", "#ffe1b4", "#16334c", "#08162a"),   # amber
    ("#0a2430", "#8fc0b4", "#f0efe0", "#0f4450", "#061c24"),   # teal
    ("#122036", "#b58aa0", "#ffd7d0", "#183а4d".replace("а", "a"), "#0a1626"),  # rose
]


def _sky(pal, w, h, sun_x, sun_y, idx):
    top, bottom, sun, _water, _land = pal
    return f"""
  <defs>
    <linearGradient id="sky{idx}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{top}"/>
      <stop offset="55%" stop-color="{top}"/>
      <stop offset="100%" stop-color="{bottom}"/>
    </linearGradient>
    <radialGradient id="glow{idx}" cx="{sun_x/w}" cy="{sun_y/h}" r="0.55">
      <stop offset="0%" stop-color="{sun}" stop-opacity="0.95"/>
      <stop offset="35%" stop-color="{bottom}" stop-opacity="0.55"/>
      <stop offset="100%" stop-color="{bottom}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="water{idx}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{pal[3]}" stop-opacity="0.95"/>
      <stop offset="100%" stop-color="{pal[4]}"/>
    </linearGradient>
  </defs>
  <rect width="{w}" height="{h}" fill="url(#sky{idx})"/>
  <rect width="{w}" height="{h}" fill="url(#glow{idx})"/>
  <circle cx="{sun_x}" cy="{sun_y}" r="{int(h*0.045)}" fill="{sun}" opacity="0.9"/>"""


def _clouds(pal, w, horizon, rnd):
    out = ""
    for k in range(5):
        cy = rnd(int(horizon * 0.15), int(horizon * 0.75))
        cx = rnd(0, w)
        cw = rnd(int(w * 0.12), int(w * 0.34))
        ch = max(4, int(cw * 0.055))
        out += f'<rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="{ch//2}" fill="#ffffff" opacity="0.{rnd(6,14)}"/>'
    return out


def _palm(x, base_y, size, colour):
    """Simple palm silhouette."""
    trunk = f'<path d="M{x} {base_y} q {size*0.08} -{size*0.5} {size*0.02} -{size*0.9}" stroke="{colour}" stroke-width="{max(2,size*0.045)}" fill="none" stroke-linecap="round"/>'
    top = base_y - size * 0.9
    fronds = ""
    for dx, dy in [(-1, -0.28), (-0.75, 0.12), (1, -0.28), (0.75, 0.12), (0.1, -0.5)]:
        fronds += (f'<path d="M{x + size*0.02} {top} q {dx*size*0.32} {dy*size*0.55} '
                   f'{dx*size*0.52} {(dy+0.22)*size*0.62}" stroke="{colour}" '
                   f'stroke-width="{max(2,size*0.05)}" fill="none" stroke-linecap="round"/>')
    return trunk + fronds


def _windows(x, y, bw, bh, rnd, warm="#ffd9a0"):
    out = ""
    cols = max(2, int(bw // 22))
    rows = max(2, int(bh // 26))
    for c in range(cols):
        for r in range(rows):
            if rnd(0, 10) < 5:
                continue
            wx = x + 10 + c * (bw - 16) / cols
            wy = y + 12 + r * (bh - 18) / rows
            out += (f'<rect x="{wx:.0f}" y="{wy:.0f}" width="{max(4,(bw-16)/cols*0.55):.0f}" '
                    f'height="{max(5,(bh-18)/rows*0.42):.0f}" fill="{warm}" opacity="0.{rnd(28,62)}"/>')
    return out


def scene_svg(kind, seed, w=1600, h=1067):
    """kind: coastal | lagoon | skyline | villa | plan"""
    rnd = _rand(seed + kind)
    pal = PALETTES[rnd(0, 100) % len(PALETTES)]
    idx = abs(hash(seed + kind)) % 9999
    horizon = int(h * ((0.44 + rnd(0, 14) / 100.0) if kind != "skyline" else (0.55 + rnd(0, 10) / 100.0)))
    sun_x = rnd(int(w * 0.2), int(w * 0.8))
    sun_y = horizon - rnd(int(h * 0.02), int(h * 0.1))
    dark = pal[4]
    warm = pal[2]

    if kind == "plan":
        return _plan_svg(seed, w, h, pal)

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{_esc(kind)} view">']
    s.append(_sky(pal, w, h, sun_x, sun_y, idx))
    s.append(_clouds(pal, w, horizon, rnd))

    # distant headland
    s.append(f'<path d="M0 {horizon} L0 {horizon-int(h*0.09)} '
             f'Q {int(w*0.12)} {horizon-int(h*0.14)} {int(w*0.26)} {horizon-int(h*0.04)} '
             f'L {int(w*0.34)} {horizon} Z" fill="{dark}" opacity="0.75"/>')

    # water
    s.append(f'<rect x="0" y="{horizon}" width="{w}" height="{h-horizon}" fill="url(#water{idx})"/>')
    for k in range(9):
        ly = horizon + int((h - horizon) * (k + 1) / 11)
        lw = rnd(int(w * 0.1), int(w * 0.5))
        lx = max(0, sun_x - lw // 2 + rnd(-60, 60))
        s.append(f'<rect x="{lx}" y="{ly}" width="{lw}" height="{max(2,int(h*0.004))}" fill="{warm}" opacity="0.{rnd(12,34)}"/>')

    if kind == "skyline":
        base = horizon + int(h * 0.02)
        x = int(w * 0.08)
        while x < w * 0.94:
            bw = rnd(int(w * 0.05), int(w * 0.11))
            bh = rnd(int(h * 0.16), int(h * 0.42))
            y = base - bh
            s.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" fill="{dark}" opacity="0.95"/>')
            s.append(_windows(x, y, bw, bh, rnd, warm))
            x += bw + rnd(8, 26)
        s.append(f'<rect x="0" y="{base}" width="{w}" height="{h-base}" fill="{dark}"/>')

    elif kind == "villa":
        base = int(h * 0.82)
        s.append(f'<rect x="0" y="{horizon}" width="{w}" height="{base-horizon}" fill="{dark}" opacity="0.55"/>')
        x = int(w * 0.06)
        while x < w * 0.9:
            bw = rnd(int(w * 0.13), int(w * 0.2))
            bh = rnd(int(h * 0.15), int(h * 0.24))
            y = base - bh
            s.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="4" fill="#e9e2d6" opacity="0.72"/>')
            s.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{max(6,int(bh*0.08))}" fill="{dark}" opacity="0.35"/>')
            s.append(_windows(x, y + int(bh * 0.18), bw, int(bh * 0.7), rnd, "#2b3a44"))
            x += bw + rnd(int(w * 0.02), int(w * 0.05))
        s.append(f'<rect x="0" y="{base}" width="{w}" height="{h-base}" fill="#2b4433" opacity="0.7"/>')
        for k in range(4):
            s.append(_palm(rnd(int(w * 0.05), int(w * 0.95)), base + rnd(4, int(h * 0.1)), rnd(int(h * 0.12), int(h * 0.22)), "#12301f"))

    elif kind == "lagoon":
        top = int(h * 0.62)
        s.append(f'<path d="M0 {top} Q {int(w*0.25)} {top-int(h*0.09)} {int(w*0.5)} {top} '
                 f'T {w} {top-int(h*0.03)} L {w} {h} L 0 {h} Z" fill="{pal[3]}" opacity="0.92"/>')
        s.append(f'<path d="M0 {top+int(h*0.02)} Q {int(w*0.3)} {top-int(h*0.05)} {int(w*0.62)} {top+int(h*0.03)} '
                 f'T {w} {top} " stroke="#ffffff" stroke-opacity="0.3" stroke-width="3" fill="none"/>')
        bx = int(w * 0.1)
        while bx < w * 0.88:
            bw = rnd(int(w * 0.09), int(w * 0.14))
            bh = rnd(int(h * 0.1), int(h * 0.17))
            y = horizon + int(h * 0.03) - bh
            s.append(f'<rect x="{bx}" y="{y}" width="{bw}" height="{bh}" rx="3" fill="#e4ddd1" opacity="0.7"/>')
            s.append(_windows(bx, y, bw, bh, rnd, "#33454f"))
            bx += bw + rnd(int(w * 0.01), int(w * 0.04))
        for k in range(3):
            s.append(_palm(rnd(int(w * 0.05), int(w * 0.95)), top + rnd(int(h * 0.02), int(h * 0.16)), rnd(int(h * 0.1), int(h * 0.18)), "#11322b"))

    else:  # coastal
        beach = int(h * (0.72 + rnd(0, 12) / 100.0))
        s.append(f'<path d="M0 {beach} Q {int(w*0.35)} {beach-int(h*0.05)} {w} {beach-int(h*0.02)} L {w} {h} L 0 {h} Z" fill="#dccdb2" opacity="0.75"/>')
        bx = int(w * 0.08)
        while bx < w * 0.9:
            bw = rnd(int(w * 0.08), int(w * 0.14))
            bh = rnd(int(h * 0.08), int(h * 0.15))
            y = horizon - bh + int(h * 0.01)
            s.append(f'<rect x="{bx}" y="{y}" width="{bw}" height="{bh}" rx="3" fill="#e8e1d5" opacity="0.7"/>')
            s.append(f'<rect x="{bx}" y="{y}" width="{bw}" height="{max(5,int(bh*0.12))}" fill="{dark}" opacity="0.3"/>')
            bx += bw + rnd(int(w * 0.015), int(w * 0.05))
        for k in range(4):
            s.append(_palm(rnd(int(w * 0.04), int(w * 0.96)), beach + rnd(0, int(h * 0.14)), rnd(int(h * 0.1), int(h * 0.2)), "#1d3a2a"))

    if kind in ("coastal", "villa", "lagoon") and rnd(0, 10) > 4:
        py = int(h * 0.88)
        s.append(f'<rect x="{int(w*0.08)}" y="{py}" width="{int(w*0.84)}" height="{int(h*0.09)}" rx="6" fill="{pal[3]}" opacity="0.85"/>')
        s.append(f'<rect x="{int(w*0.08)}" y="{py}" width="{int(w*0.84)}" height="{max(3,int(h*0.008))}" fill="#ffffff" opacity="0.28"/>')

    # atmospheric haze + soft vignette (gradients, not flat bands)
    s.append(f'''<defs>
      <linearGradient id="hz{idx}" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="{pal[0]}" stop-opacity="0.45"/>
        <stop offset="45%" stop-color="{pal[0]}" stop-opacity="0"/>
        <stop offset="100%" stop-color="{pal[4]}" stop-opacity="0.4"/>
      </linearGradient>
      <radialGradient id="vg{idx}" cx="0.5" cy="0.5" r="0.75">
        <stop offset="55%" stop-color="#000000" stop-opacity="0"/>
        <stop offset="100%" stop-color="#000000" stop-opacity="0.3"/>
      </radialGradient>
    </defs>
    <rect width="{w}" height="{h}" fill="url(#hz{idx})"/>
    <rect width="{w}" height="{h}" fill="url(#vg{idx})"/>''')
    s.append("</svg>")
    return "".join(s)


def _plan_svg(seed, w, h, pal):
    """Abstract masterplan graphic: plots, canal, greenery."""
    rnd = _rand(seed + "plan")
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="masterplan">']
    s.append(f'<rect width="{w}" height="{h}" fill="#f2efe8"/>')
    s.append(f'<rect width="{w}" height="{h}" fill="{pal[0]}" opacity="0.06"/>')
    # green spine
    s.append(f'<path d="M{int(w*0.05)} {int(h*0.78)} Q {int(w*0.35)} {int(h*0.5)} {int(w*0.55)} {int(h*0.62)} '
             f'T {int(w*0.97)} {int(h*0.3)}" stroke="#8fae7f" stroke-width="{int(h*0.09)}" fill="none" stroke-linecap="round" opacity="0.55"/>')
    # canal
    s.append(f'<path d="M{int(w*0.02)} {int(h*0.35)} Q {int(w*0.3)} {int(h*0.2)} {int(w*0.52)} {int(h*0.42)} '
             f'T {w} {int(h*0.62)}" stroke="{pal[3]}" stroke-width="{int(h*0.055)}" fill="none" stroke-linecap="round" opacity="0.85"/>')
    # plots
    for k in range(38):
        bw = rnd(int(w * 0.03), int(w * 0.07))
        bh = rnd(int(h * 0.03), int(h * 0.07))
        x = rnd(int(w * 0.04), int(w * 0.92))
        y = rnd(int(h * 0.06), int(h * 0.88))
        rot = rnd(-8, 8)
        s.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="2" fill="{pal[4]}" opacity="0.{rnd(30,70)}" transform="rotate({rot} {x+bw//2} {y+bh//2})"/>')
    # roads
    for k in range(4):
        y = rnd(int(h * 0.1), int(h * 0.9))
        s.append(f'<path d="M0 {y} Q {int(w*0.5)} {y - rnd(int(h*0.1), int(h*0.2))} {w} {y + rnd(-40, 40)}" stroke="#ffffff" stroke-width="{int(h*0.012)}" fill="none" opacity="0.75"/>')
    s.append("</svg>")
    return "".join(s)


KIND_BY_TYPE = {
    "chalet": ["coastal", "lagoon", "plan", "coastal"],
    "apartment": ["skyline", "lagoon", "villa", "plan"],
    "villa": ["villa", "lagoon", "coastal", "plan"],
    "townhouse": ["villa", "lagoon", "plan", "villa"],
    "twinhouse": ["villa", "coastal", "plan", "lagoon"],
    "duplex": ["skyline", "villa", "plan", "lagoon"],
    "penthouse": ["skyline", "coastal", "villa", "plan"],
    "loft": ["skyline", "villa", "plan", "lagoon"],
    "office": ["skyline", "plan", "villa", "lagoon"],
    "retail": ["skyline", "plan", "villa", "coastal"],
}


def kinds_for(types):
    """Pick the 4 scene kinds that suit a project's unit mix."""
    primary = types[0] if types else "apartment"
    return KIND_BY_TYPE.get(primary, KIND_BY_TYPE["apartment"])
