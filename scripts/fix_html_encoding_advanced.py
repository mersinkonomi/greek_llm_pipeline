#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced HTML Encoding Fixer

Handles more complex encoding issues including:
- Gzip-compressed HTML files
- Mojibake fixes (mis-decoded UTF-8)
- Multiple encoding fallbacks
- Forces UTF-8 meta tags
"""

import re
import gzip
from pathlib import Path

SRC = Path("./data/ap_decisions_all/html")
OUT = SRC.parent / "html_utf8"


def smart_decode(raw: bytes) -> str:
    """Intelligent decoding with multiple fallbacks and mojibake detection."""
    # 1) If gzip-compressed, decompress first
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    
    # 2) Try UTF-8 → cp1253 → iso-8859-7
    for enc in ("utf-8", "cp1253", "iso-8859-7"):
        try:
            txt = raw.decode(enc)
            break
        except UnicodeDecodeError:
            txt = None
    
    # 3) Final fallback: cp1253 with error replacement
    if txt is None:
        txt = raw.decode("cp1253", errors="replace")
    
    # 4) Mojibake fix if we see lots of Î/Ï/Ξ
    def looks_mojibake(s):
        return s.count("Î") + s.count("Ï") + s.count("Ξ") > 50
    
    if looks_mojibake(txt):
        try:
            # UTF-8 that was read as cp1253/latin1 → convert back to UTF-8
            txt_fix = txt.encode("cp1253", errors="ignore").decode("utf-8", errors="ignore")
            if not looks_mojibake(txt_fix):
                txt = txt_fix
            else:
                txt_fix2 = txt.encode("latin1", errors="ignore").decode("utf-8", errors="ignore")
                if not looks_mojibake(txt_fix2):
                    txt = txt_fix2
        except Exception:
            pass
    
    return txt


def force_meta_utf8(html: str) -> str:
    """Force UTF-8 meta tag in HTML head."""
    head_match = re.search(r'(?is)<head.*?>', html)
    
    if re.search(r'(?i)charset\s*=', html[:4000]):
        html = re.sub(
            r'(?is)charset\s*=\s*["\']?[^"\' >]+',
            'charset="utf-8"',
            html,
            count=1
        )
    elif head_match:
        i = head_match.end()
        html = html[:i] + '\n<meta charset="utf-8">' + html[i:]
    else:
        html = '<meta charset="utf-8">\n' + html
    
    return html


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    
    count = 0
    for f in sorted(SRC.glob("*.html")):
        raw = f.read_bytes()
        txt = smart_decode(raw)
        txt = force_meta_utf8(txt)
        (OUT / f.name).write_text(txt, encoding="utf-8")
        count += 1
    
    print(f"OK: Converted {count} files to UTF-8 -> {OUT}")


if __name__ == "__main__":
    main()

