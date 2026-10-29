#!/usr/bin/env python3
"""Report colors, fonts and emojis in HTML mockups that aren't allowed by the product identity.

Usage: check_brand.py tokens.json option-1.html [option-2.html ...]

tokens.json: {"colors": [...], "fonts": [...], "allow": [...]}
Exit code 1 if any off-identity color or font, or any emoji, is found.
"""
import colorsys
import json
import re
import sys
from pathlib import Path

NAMED = {"white": "#ffffff", "black": "#000000"}
KEYWORDS = {"transparent", "currentcolor", "inherit", "initial", "unset", "none"}
GENERIC_FONTS = {"serif", "sans-serif", "monospace", "cursive", "fantasy", "system-ui",
                 "ui-sans-serif", "ui-serif", "ui-monospace", "ui-rounded", "emoji",
                 "-apple-system", "blinkmacsystemfont", "segoe ui", "roboto", "helvetica",
                 "helvetica neue", "arial", "apple color emoji", "segoe ui emoji", "inherit"}

COLOR_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b|rgba?\([^)]*\)|hsla?\([^)]*\)")
EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F]")


def to_hex(value):
    """Normalize a CSS color to #rrggbb, ignoring alpha. None if unparseable."""
    v = value.strip().lower()
    if v in NAMED:
        return NAMED[v]
    if v.startswith("#"):
        h = v[1:]
        if len(h) in (3, 4):
            h = "".join(c * 2 for c in h[:3])
        elif len(h) in (6, 8):
            h = h[:6]
        else:
            return None
        return "#" + h
    nums = re.findall(r"-?[\d.]+%?", v)
    if len(nums) < 3:
        return None
    if v.startswith("rgb"):
        rgb = [float(n[:-1]) * 2.55 if n.endswith("%") else float(n) for n in nums[:3]]
    elif v.startswith("hsl"):
        h, s, l = (float(n.rstrip("%")) for n in nums[:3])
        r, g, b = colorsys.hls_to_rgb((h % 360) / 360, l / 100, s / 100)
        rgb = [r * 255, g * 255, b * 255]
    else:
        return None
    return "#" + "".join(f"{max(0, min(255, round(c))):02x}" for c in rgb)


def distance(a, b):
    ra, ga, ba = (int(a[i:i + 2], 16) for i in (1, 3, 5))
    rb, gb, bb = (int(b[i:i + 2], 16) for i in (1, 3, 5))
    return ((ra - rb) ** 2 + (ga - gb) ** 2 + (ba - bb) ** 2) ** 0.5


def css_of(html):
    """Style blocks, inline styles and SVG paint attributes; skips comments and scripts."""
    html = re.sub(r"<!--.*?-->", "", html, flags=re.S)
    html = re.sub(r"<script.*?</script>", "", html, flags=re.S | re.I)
    parts = re.findall(r"<style[^>]*>(.*?)</style>", html, flags=re.S | re.I)
    parts += re.findall(r'style="([^"]*)"', html)
    parts += re.findall(r'(?:fill|stroke|stop-color|color)="([^"]*)"', html)
    return re.sub(r"/\*.*?\*/", "", "\n".join(parts), flags=re.S)


def fonts_of(html, css):
    found = set()
    for fam in re.findall(r"family=([^&:\"']+)", html):
        found.add(fam.replace("+", " ").strip().lower())
    for decl in re.findall(r"font-family\s*:\s*([^;}{]+)", css):
        for f in decl.split(","):
            f = f.strip().strip("'\"").lower()
            if f and not f.startswith("var("):
                found.add(f)
    return found - GENERIC_FONTS


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    tokens = json.loads(Path(sys.argv[1]).read_text())
    palette = {to_hex(c) for c in tokens.get("colors", [])} - {None}
    allow = {a.lower() for a in tokens.get("allow", [])}
    fonts = {f.lower() for f in tokens.get("fonts", [])}
    bad = False
    for path in sys.argv[2:]:
        html = Path(path).read_text(errors="ignore")
        css = css_of(html)
        off = {}
        for raw in COLOR_RE.findall(css):
            if raw.lower() in allow:
                continue
            hx = to_hex(raw)
            if hx and hx not in palette:
                off.setdefault(hx, set()).add(raw)
        off_fonts = sorted(fonts_of(html, css) - fonts)
        visible = re.sub(r"<!--.*?-->", "", html, flags=re.S)
        emojis = [(i + 1, line.strip()[:70]) for i, line in enumerate(visible.splitlines())
                  if EMOJI_RE.search(line)]
        print(f"== {path}")
        if not off and not off_fonts and not emojis:
            print("   OK: colors and fonts are in the identity, no emojis")
            continue
        bad = True
        for hx, raws in sorted(off.items()):
            near = min(palette, key=lambda p: distance(p, hx)) if palette else None
            hint = f" (closest token: {near}, distance {distance(near, hx):.0f})" if near else ""
            print(f"   color {hx} as {', '.join(sorted(raws))}{hint}")
        for f in off_fonts:
            print(f"   font  '{f}' not in identity fonts {sorted(fonts)}")
        for n, text in emojis:
            print(f"   emoji line {n}: {text}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
