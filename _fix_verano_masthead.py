#!/usr/bin/env python3
"""Swap the fabricated CSS AROYA glyph in Verano PA masthead for the canonical wordmark SVG.

Source of truth: ~/Library/Mobile Documents/com~apple~CloudDocs/Aroya/AROYA_Brand_Kit/svg/AROYA_wordmark.svg
Reference impl: POWRHOUSE_Long_Term_Audit_2026-06-18.html (already uses canonical bytes).
"""
import re
from pathlib import Path

REPO = Path("/Users/ciansullivan/code/aroya-reports")
CANONICAL_WORDMARK = Path(
    "/Users/ciansullivan/Library/Mobile Documents/com~apple~CloudDocs/Aroya/AROYA_Brand_Kit/svg/AROYA_wordmark.svg"
)

WORDMARK_SVG = CANONICAL_WORDMARK.read_text()
inner_match = re.search(r"<svg[^>]*>(.*?)</svg>", WORDMARK_SVG, re.DOTALL)
assert inner_match, "canonical wordmark SVG parse failed"
INNER = inner_match.group(1).strip()

CANONICAL_SVG_INLINE = (
    '<svg class="aroya-wordmark" version="1.1" viewBox="0 0 202.1 75" '
    'xmlns="http://www.w3.org/2000/svg" '
    'style="height:36px;width:auto;fill:currentColor" '
    'aria-label="AROYA">'
    + INNER
    + "</svg>"
)


def strip_fabricated_css(html):
    html = re.sub(r"\.lockup-mark\{[^}]*\}", "", html)
    html = re.sub(r"\.lockup-glyph\{[^}]*\}", "", html)
    html = re.sub(r"\.lockup-glyph::before,\.lockup-glyph::after\{[^}]*\}", "", html)
    html = re.sub(r"\.lockup-glyph::before\{[^}]*\}", "", html)
    html = re.sub(r"\.lockup-glyph::after\{[^}]*\}", "", html)
    return html


def swap_masthead_body(html):
    fabricated = re.compile(
        r'<span class="lockup-glyph"></span>\s*<span class="lockup-mark">AROYA</span>',
        re.DOTALL,
    )
    if not fabricated.search(html):
        raise RuntimeError("fabricated masthead pattern not found — file may already be canonical")
    return fabricated.sub(CANONICAL_SVG_INLINE, html)


def ensure_aroya_wordmark_css(html):
    rule = ".aroya-wordmark{height:36px;width:auto;display:block;fill:currentColor;color:#fff}"
    if ".aroya-wordmark" in html:
        return html
    html = re.sub(r"(\.lockup\{[^}]*\})", r"\1" + rule, html, count=1)
    return html


def patch(path):
    orig = path.read_text()
    stripped = strip_fabricated_css(orig)
    with_css = ensure_aroya_wordmark_css(stripped)
    patched = swap_masthead_body(with_css)
    if patched == orig:
        print("NO CHANGE:", path)
        return
    path.write_text(patched)
    print("PATCHED :", path, "(", len(orig), "->", len(patched), "bytes)")


if __name__ == "__main__":
    targets = [
        REPO / "VeranoPA_Day1_Device_Mesh_Health_2026-07-01.html",
        REPO / "VeranoPA_Day1_Device_Mesh_Health_2026-07-01_dark.html",
    ]
    for t in targets:
        patch(t)
    mirror = Path("/Users/ciansullivan/Documents/Claude/Projects/AROYA (3)/verano-pa-day1-device-mesh-audit-2026-07-01.html")
    if mirror.exists():
        try:
            patch(mirror)
        except Exception as e:
            print("mirror skipped:", e)
    print("DONE — canonical wordmark from", CANONICAL_WORDMARK)
