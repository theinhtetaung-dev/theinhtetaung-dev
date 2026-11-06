#!/usr/bin/env python3
"""Embed the profile illustration into both profile SVG variants."""

from __future__ import annotations

import base64
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "assets" / "chibi-office-prayer.png"
SVG_FILES = (
    ROOT / "assets" / "profile-light.svg",
    ROOT / "assets" / "profile-dark.svg",
)


def main() -> None:
    image_data = base64.b64encode(IMAGE.read_bytes()).decode("ascii")
    replacement = (
        '<g id="profileIllustration">'
        '<image x="10" y="170" width="380" height="253" '
        f'href="data:image/png;base64,{image_data}" '
        'preserveAspectRatio="xMidYMid meet"/>'
        '<g id="chantingMouth">'
        '<ellipse cx="185" cy="244" rx="4.8" ry="0.5" fill="#6b2730">'
        '<animate attributeName="ry" values="0.5;2.8;1.2;2.4;0.5" '
        'keyTimes="0;0.22;0.48;0.72;1" dur="1.35s" repeatCount="indefinite"/>'
        '</ellipse>'
        '<ellipse cx="185" cy="245.2" rx="2.5" ry="0.7" fill="#e98282" opacity="0">'
        '<animate attributeName="opacity" values="0;0.8;0.25;0.7;0" '
        'keyTimes="0;0.22;0.48;0.72;1" dur="1.35s" repeatCount="indefinite"/>'
        '</ellipse>'
        '</g>'
        '<g id="chantingText">'
        '<defs><clipPath id="chantingTextClip">'
        '<rect x="115" y="132" width="0" height="24">'
        '<animate attributeName="width" values="0;0;142;142;0" '
        'keyTimes="0;0.08;0.62;0.9;1" dur="4s" repeatCount="indefinite"/>'
        '</rect>'
        '</clipPath></defs>'
        '<text x="115" y="150" clip-path="url(#chantingTextClip)" '
        'font-family="Noto Sans Myanmar,Myanmar Text,Segoe UI Emoji,sans-serif" '
        'font-size="15" font-weight="600" fill="#ffffff" stroke="#252033" '
        'stroke-width="2.4" paint-order="stroke fill">Error ကင်းပါစေ🙏</text>'
        '<rect x="115" y="134" width="1.5" height="18" fill="#ffffff">'
        '<animate attributeName="x" values="115;115;257;257;115" '
        'keyTimes="0;0.08;0.62;0.9;1" dur="4s" repeatCount="indefinite"/>'
        '<animate attributeName="opacity" values="1;0.2;1;0.2;0" '
        'keyTimes="0;0.2;0.62;0.9;1" dur="4s" repeatCount="indefinite"/>'
        '</rect>'
        '</g>'
        '</g>'
    )
    pattern = re.compile(
        r'<g id="(?:petAnimation|profileIllustration)">.*?</g>'
        r'(?=</g><text x="(?:390|410)")'
    )

    for svg_file in SVG_FILES:
        original = svg_file.read_text(encoding="utf-8")
        updated, count = pattern.subn(replacement, original, count=1)
        if count != 1:
            raise RuntimeError(f"Could not locate profile illustration in {svg_file}")
        updated = updated.replace('viewBox="0 0 985 530"', 'viewBox="0 0 1010 530"')
        updated = updated.replace('<rect width="985" height="530"', '<rect width="1010" height="530"')
        updated = updated.replace('x="390"', 'x="410"')
        updated = updated.replace('<rect x="886" y="496"', '<rect x="906" y="496"')
        svg_file.write_text(updated, encoding="utf-8", newline="\n")
        print(f"Updated {svg_file.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
