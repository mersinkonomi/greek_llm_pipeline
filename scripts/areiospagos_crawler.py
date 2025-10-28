#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Areios Pagos (Greek Supreme Court) Web Crawler

Discovers and crawls legal decisions from areiospagos.gr using:
1. BFS to find referenced codes
2. Probe-based discovery to find active codes
3. Plateau detection to stop early
4. Coverage reporting
"""

import requests
import re
import time
import random
import json
from collections import deque
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

BASE = "https://www.areiospagos.gr"
LISTING_PATH = "/nomologia/apofaseis_result.asp"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; AP-Coverage/1.0) PythonRequests",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "el,en;q=0.8",
}


def get_html(url, timeout=25):
    """Fetch HTML with proper Greek encoding handling."""
    r = requests.get(url, headers=HEADERS, timeout=timeout)
    enc = (r.encoding or "").lower()
    if not enc or enc in ("utf-8", "iso-8859-1", "ascii"):
        try:
            r.encoding = (r.apparent_encoding or "cp1253")
        except Exception:
            r.encoding = "cp1253"
    return r.text if r.status_code == 200 else ""


def discover_referenced_codes_bfs(start=f"{BASE}/nomologia/", max_pages=4000, max_depth=3):
    """Discover codes referenced in the website using BFS."""
    seen = set([start])
    q = deque([(start, 0)])
    codes = set()
    pages = 0
    
    while q and pages < max_pages:
        url, depth = q.popleft()
        html = get_html(url)
        pages += 1
        
        if not html:
            continue
        
        soup = BeautifulSoup(html, "html.parser")
        
        # Collect all code= from anchors + raw regex
        for a in soup.find_all("a", href=True):
            m = re.search(r"apofaseis_result\.asp\?code=(\d+)", a["href"], flags=re.I)
            if m:
                codes.add(int(m.group(1)))
        
        for m in re.finditer(r"apofaseis_result\.asp\?code=(\d+)", html, flags=re.I):
            codes.add(int(m.group(1)))
        
        # BFS expansion (stay within /nomologia/)
        if depth < max_depth:
            for a in soup.find_all("a", href=True):
                nxt = urljoin(url, a["href"])
                u = urlparse(nxt)
                if (u.netloc.endswith("areiospagos.gr")
                    and "/nomologia/" in u.path
                    and nxt not in seen):
                    seen.add(nxt)
                    q.append((nxt, depth + 1))
        
        if pages % 200 == 0:
            print(f"[BFS] visited={pages}, codes_found={len(codes)}")
        
        time.sleep(0.4 + random.random() * 0.2)  # Polite delay
    
    print(f"[BFS] done. pages={pages}, referenced_codes={len(codes)}")
    return sorted(codes)


def parse_listing_for_links(html, base_url):
    """Parse listing page for decision links and pagination."""
    soup = BeautifulSoup(html, "html.parser")
    decs = set()
    more = set()
    
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "apofaseis_DISPLAY.asp" in href:
            decs.add(href)
        if "apofaseis_result.asp" in href or a.get_text(strip=True) in {"Επόμενη", "»", ">", "Next", "Επομενη"}:
            more.add(href)
    
    return decs, more


def discover_active_codes_until_plateau(stop=4000, window=400):
    """Discover active codes until finding a plateau."""
    active = set()
    no_new = 0
    last_count = 0
    
    for c in range(1, stop + 1):
        found = False
        for s in (2, 1):
            url = f"{BASE}{LISTING_PATH}?code={c}&s={s}"
            html = get_html(url)
            if not html:
                continue
            
            decs, _ = parse_listing_for_links(html, url)
            if decs:
                active.add(c)
                found = True
                break
        
        if found:
            no_new = 0
        else:
            no_new += 1
        
        if c % 50 == 0:
            print(f"[PROBE] up to {c} | active={len(active)}")
            if len(active) == last_count:
                # Stop if no new codes for large window
                if no_new >= window:
                    print(f"[STOP] plateau (no new codes for last {window} codes).")
                    break
            last_count = len(active)
        
        time.sleep(0.3 + random.random() * 0.2)  # Polite delay
    
    return sorted(active)


def generate_coverage_report(referenced_codes, active_codes, output_dir="./data/areiospagos"):
    """Generate a coverage report."""
    output_path = f"{output_dir}/coverage_report.json"
    
    ref_set = set(referenced_codes)
    act_set = set(active_codes)
    
    only_referenced = sorted(ref_set - act_set)
    only_active = sorted(act_set - ref_set)
    both = sorted(ref_set & act_set)
    
    report = {
        "referenced_codes": len(ref_set),
        "active_codes": len(act_set),
        "intersection": len(both),
        "referenced_only": only_referenced[:50],
        "active_only": only_active[:50],
        "coverage_ok": (len(ref_set) > 0 and ref_set.issubset(act_set)) or (ref_set == act_set),
    }
    
    print("=== COVERAGE REPORT ===")
    print(f"Referenced (BFS): {len(ref_set)}")
    print(f"Active (probe):   {len(act_set)}")
    print(f"Overlap:          {len(both)}")
    print(f"Referenced-only (sample): {only_referenced[:10]}")
    print(f"Active-only (sample):     {only_active[:10]}")
    print(f"Coverage OK?: {report['coverage_ok']}")
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"Saved -> {output_path}")
    
    return report


def main():
    """Main execution."""
    import sys
    
    # Stage 1: Discover referenced codes via BFS
    print("=== Stage 1: BFS Discovery ===")
    REFERENCED_CODES = discover_referenced_codes_bfs()
    print(f"Sample referenced codes: {REFERENCED_CODES[:40]}")
    
    # Stage 2: Discover active codes via probing
    print("\n=== Stage 2: Active Code Discovery ===")
    ACTIVE_CODES = discover_active_codes_until_plateau(stop=4000, window=400)
    print(f"Active codes found: {len(ACTIVE_CODES)}")
    
    # Stage 3: Generate coverage report
    print("\n=== Stage 3: Coverage Report ===")
    generate_coverage_report(REFERENCED_CODES, ACTIVE_CODES)
    
    print("\n✅ Discovery complete. Use the active codes to crawl decisions.")


if __name__ == "__main__":
    main()

