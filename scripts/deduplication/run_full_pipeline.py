#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete MinHash Deduplication Pipeline for Greek Text

This script runs the entire 4-stage deduplication process:
1. Generate MinHash signatures
2. Create buckets from signatures  
3. Cluster documents and identify duplicates
4. Filter out duplicates and create final output

Includes token counting and statistics generation.
"""

import glob
import pathlib
import sys

from datatrove.executor.local import LocalPipelineExecutor
from datatrove.pipeline.dedup.minhash import (
    MinhashConfig,
    MinhashDedupBuckets,
    MinhashDedupCluster,
    MinhashDedupFilter,
    MinhashDedupSignature,
)
from datatrove.pipeline.readers import JsonlReader
from datatrove.pipeline.tokens import TokensCounter
from datatrove.pipeline.writers.jsonl import JsonlWriter
from datatrove.pipeline.stats import DocStats, LineStats, StatsMerger, TopKConfig, WordStats
from datatrove.utils.hashing import HashConfig

# Configuration
BASE = "./data"
INP_EXACT = f"{BASE}/jsonl_input/combined_exact_dedup.jsonl"
OUTB = f"{BASE}/minhash"
CLEAN_COMB = f"{OUTB}/deduplicated_combined.jsonl"
STATS_DIR = f"{BASE}/stats"
SPACY_LANG = "xx"  # spaCy multilingual tokenizer

cfg = MinhashConfig(
    hash_config=HashConfig(precision=64),
    n_grams=5,
    num_buckets=14,
    hashes_per_bucket=8,
)


def ensure_dirs():
    """Create output directories if they don't exist."""
    pathlib.Path(OUTB).mkdir(parents=True, exist_ok=True)
    pathlib.Path(STATS_DIR).mkdir(parents=True, exist_ok=True)


def assert_input():
    """Verify input file exists."""
    p = pathlib.Path(INP_EXACT)
    if not p.exists():
        raise FileNotFoundError(
            f"Input not found: {p}\n"
            "Change INP_EXACT in this script or create the input file."
        )


def run_dedup_pipeline():
    """Run the complete 4-stage deduplication pipeline."""
    print("[MinHash] Starting 4-stage pipeline...")
    pipeline = [
        # Stage 1: Generate signatures
        JsonlReader(INP_EXACT, text_key="text"),
        MinhashDedupSignature(
            output_folder=f"{OUTB}/signatures",
            config=cfg,
            language=SPACY_LANG,
        ),
        # Stage 2: Create buckets
        MinhashDedupBuckets(
            input_folder=f"{OUTB}/signatures",
            output_folder=f"{OUTB}/buckets",
            config=cfg,
        ),
        # Stage 3: Cluster documents
        MinhashDedupCluster(
            input_folder=f"{OUTB}/buckets",
            output_folder=f"{OUTB}/remove_ids",
            config=cfg,
        ),
        # Stage 4: Filter duplicates
        JsonlReader(INP_EXACT, text_key="text"),
        TokensCounter(),
        MinhashDedupFilter(
            input_folder=f"{OUTB}/remove_ids",
            exclusion_writer=JsonlWriter(f"{OUTB}/removed"),
        ),
        JsonlWriter(output_folder=f"{OUTB}/deduplicated_output"),
    ]
    LocalPipelineExecutor(pipeline=pipeline).run()
    print("[MinHash] Pipeline finished.")


def concat_kept_shards():
    """Concatenate all kept document shards into a single file."""
    print("[Concat] Building deduplicated_combined.jsonl...")
    shards = sorted(glob.glob(f"{OUTB}/deduplicated_output/*.jsonl"))
    if not shards:
        raise RuntimeError("No kept shards found in deduplicated_output/")
    with open(CLEAN_COMB, "w", encoding="utf-8") as out:
        for sh in shards:
            with open(sh, encoding="utf-8") as f:
                for line in f:
                    out.write(line)
    print(f"[Concat] Wrote: {CLEAN_COMB}")


def quick_summary():
    """Print quick summary of deduplication results."""
    kept = sum(sum(1 for _ in open(f, encoding="utf-8")) for f in glob.glob(f"{OUTB}/deduplicated_output/*.jsonl"))
    removed = sum(sum(1 for _ in open(f, encoding="utf-8")) for f in glob.glob(f"{OUTB}/removed/*.jsonl"))
    total = kept + removed
    pct_k = (kept / total * 100) if total else 0.0
    pct_r = (removed / total * 100) if total else 0.0
    print(f"[Report] Total={total} | Kept={kept} ({pct_k:.2f}%) | Removed={removed} ({pct_r:.2f}%)")


def run_stats():
    """Generate detailed statistics on the cleaned dataset."""
    print("[Stats] Starting summary stats on cleaned dataset...")
    top_k_config = TopKConfig(top_k_groups=[], top_k=10_000)
    stat_pipeline = [
        JsonlReader(CLEAN_COMB, doc_progress=True, limit=-1, text_key="text"),
        WordStats(output_folder=STATS_DIR, top_k_config=top_k_config),
        LineStats(output_folder=STATS_DIR, top_k_config=top_k_config),
        DocStats(output_folder=STATS_DIR, top_k_config=top_k_config),
        StatsMerger(
            input_folder=STATS_DIR,
            output_folder=STATS_DIR,
            remove_input=False,
            top_k_config=TopKConfig(top_k_groups=[], top_k=8_000),
        ),
    ]
    LocalPipelineExecutor(pipeline=stat_pipeline).run()
    print(f"[Stats] Merged outputs at: {STATS_DIR}")


def main():
    """Run the complete pipeline."""
    ensure_dirs()
    assert_input()
    run_dedup_pipeline()
    concat_kept_shards()
    quick_summary()
    run_stats()


if __name__ == "__main__":
    main()

