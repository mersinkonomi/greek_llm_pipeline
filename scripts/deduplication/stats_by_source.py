#!/usr/bin/env python3
"""
Generate statistics by source from JSONL files.

Computes document counts, character/word/token statistics grouped by source
for both pre-deduplication and post-deduplication datasets.
"""

import argparse
import glob
import json
import os
import re
import gzip
from collections import defaultdict

SOURCE_KEYS = {
    "openbookspdfs": "OpenBooksPDFs",
    "free-ebooks": "free-ebooks",
    "ebooksedupdfs": "EbooksEduPDFs",
    "ebooks4greekspdfs": "Ebooks4GreeksPDFs",
    "all_books": "all_books",
}

WORD_RE = re.compile(r"\w+", re.UNICODE)


def infer_source(path: str) -> str:
    """Extract source label from file path."""
    s = (path or "").lower()
    for k, v in SOURCE_KEYS.items():
        if k in s:
            return v
    return "unknown"


def iter_jsonl(src):
    """Iterate over JSONL files (handles both .jsonl and .jsonl.gz)."""
    if os.path.isfile(src):
        opener = gzip.open if src.endswith(".gz") else open
        with opener(src, "rt", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except Exception:
                    continue
        return

    patterns = [
        os.path.join(src, "*.jsonl"),
        os.path.join(src, "**/*.jsonl"),
        os.path.join(src, "*.jsonl.gz"),
        os.path.join(src, "**/*.jsonl.gz"),
    ]
    seen = set()
    for pat in patterns:
        for fp in glob.iglob(pat, recursive=True):
            if fp in seen:
                continue
            seen.add(fp)
            opener = gzip.open if fp.endswith(".gz") else open
            try:
                with opener(fp, "rt", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            yield json.loads(line)
                        except Exception:
                            pass
            except Exception as e:
                print(f"[WARN] Cannot open {fp}: {e}")


def compute(src, out_csv):
    """Compute statistics by source."""
    agg = defaultdict(lambda: {"docs": 0, "chars": 0, "words": 0})

    for rec in iter_jsonl(src):
        txt = rec.get("text") or rec.get("content") or ""
        sp = rec.get("source_path") or rec.get("path") or rec.get("source") or ""
        if not txt:
            continue
        lab = infer_source(sp)
        agg[lab]["docs"] += 1
        agg[lab]["chars"] += len(txt)
        agg[lab]["words"] += len(WORD_RE.findall(txt))

    rows = []
    total = {"docs": 0, "chars": 0, "words": 0}
    for lab in sorted(agg.keys()):
        m = agg[lab]
        d = max(m["docs"], 1)
        rows.append([
            lab, m["docs"], m["chars"], m["words"],
            round(m["words"] / d, 2), round(m["chars"] / d, 2)
        ])
        total["docs"] += m["docs"]
        total["chars"] += m["chars"]
        total["words"] += m["words"]

    if total["docs"] > 0:
        d = total["docs"]
        rows.append(["TOTAL", total["docs"], total["chars"], total["words"],
                     round(total["words"] / d, 2), round(total["chars"] / d, 2)])

    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    with open(out_csv, "w", encoding="utf-8") as f:
        f.write("source,docs,chars,words,avg_words_per_doc,avg_chars_per_doc\n")
        for r in rows:
            f.write(",".join(map(str, r)) + "\n")
    print(f"[OK] Wrote {out_csv}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pre", default="jsonl_input")
    ap.add_argument("--post", default="minhash/deduplicated_output")
    ap.add_argument("--combined", default="minhash/deduplicated_combined.jsonl")
    ap.add_argument("--outdir", default="stats")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    compute(args.pre, os.path.join(args.outdir, "stats_pre_dedup.csv"))

    post_src = args.post if (
        os.path.isdir(args.post) and
        any(glob.glob(os.path.join(args.post, "*.jsonl")))
    ) else args.combined
    compute(post_src, os.path.join(args.outdir, "stats_post_dedup.csv"))
