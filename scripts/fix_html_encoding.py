#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML Encoding Fixer

Batch fix for HTML files with wrong encoding:
- If HTML is in cp1253/iso-8859-7 → creates .utf8.html with correct meta
- If HTML is already utf-8 but has wrong meta → fixes in-place
- Optionally updates JSON with saved_html_utf8 field
"""

import re
import json
from pathlib import Path

ROOT = Path("./data/ap_decisions_all")  # Change to your folder
H = ROOT / "html"
J = ROOT / "jsonl"

fixed_meta = 0
made_utf8 = 0
json_patched = 0


def looks_utf8(b: bytes) -> bool:
    """Check if bytes can be decoded as UTF-8."""
    try:
        b.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return False


def main():
    global fixed_meta, made_utf8, json_patched
    
    for hp in H.glob("*.html"):
        stem = hp.stem
        b = hp.read_bytes()
        
        # If already clean UTF-8
        if looks_utf8(b):
            s = b.decode("utf-8", errors="replace")
            s2 = re.sub(
                r'(?i)charset\s*=\s*(windows-1253|iso-8859-7|iso8859-7|cp1253)',
                'charset=utf-8',
                s
            )
            if s2 != s:
                hp.write_text(s2, encoding="utf-8")
                fixed_meta += 1
            
            u8p = hp.with_suffix(".utf8.html")
            if not u8p.exists():
                u8p.write_text(s2, encoding="utf-8")
                made_utf8 += 1
            utf8_path = str(u8p)
        else:
            # Non-UTF8: decode as Greek single-byte
            try:
                s = b.decode("cp1253", errors="replace")
            except Exception:
                s = b.decode("iso-8859-7", errors="replace")
            
            s2 = re.sub(
                r'(?i)charset\s*=\s*(windows-1253|iso-8859-7|iso8859-7|cp1253)',
                'charset=utf-8',
                s
            )
            u8p = hp.with_suffix(".utf8.html")
            u8p.write_text(s2, encoding="utf-8")
            made_utf8 += 1
            utf8_path = str(u8p)
        
        # Optionally patch corresponding JSON
        jp = J / f"{stem}.json"
        if jp.exists():
            try:
                o = json.loads(jp.read_text(encoding="utf-8"))
                if o.get("saved_html_utf8") != utf8_path:
                    o["saved_html_utf8"] = utf8_path
                    jp.write_text(
                        json.dumps(o, ensure_ascii=False, indent=0),
                        encoding="utf-8"
                    )
                    json_patched += 1
            except Exception:
                pass
    
    print(f"Meta fixed in-place: {fixed_meta}")
    print(f"UTF-8 versions created: {made_utf8}")
    print(f"JSON patched: {json_patched}")
    print("✅ Done")


if __name__ == "__main__":
    main()
