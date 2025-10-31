#!/usr/bin/env bash
"""
Concatenate deduplicated shards and generate summary report.

Combines all output shards into a single file and reports statistics
on documents kept vs. removed during deduplication.
"""
set -euo pipefail

# Import configuration
source config/pipeline_conf.sh || {
    # Default paths if config not found
    BASE="${BASE:-~/data}"
    OUTB="${OUTB:-${BASE}/minhash}"
}

CLEAN="${OUTB}/deduplicated_combined.jsonl"

echo "[Concat] -> $CLEAN"

# Handle both compressed and uncompressed outputs
if ls "$OUTB/deduplicated_output"/*.jsonl.gz >/dev/null 2>&1; then
    zcat "$OUTB/deduplicated_output"/*.jsonl.gz > "$CLEAN"
elif ls "$OUTB/deduplicated_output"/*.jsonl >/dev/null 2>&1; then
    cat "$OUTB/deduplicated_output"/*.jsonl > "$CLEAN"
else
    echo "No deduplicated output found!"
    exit 1
fi

echo "[Report]"
echo "[input ] $(wc -l < ${BASE}/jsonl_input/combined_exact_dedup.jsonl 2>/dev/null || echo 'N/A')"
echo "[kept  ] $(wc -l < $CLEAN)"

if ls "$OUTB/removed"/*.jsonl.gz >/dev/null 2>&1; then
    echo "[removed] $(zcat $OUTB/removed/*.jsonl.gz | wc -l)"
elif ls "$OUTB/removed"/*.jsonl >/dev/null 2>&1; then
    echo "[removed] $(cat $OUTB/removed/*.jsonl | wc -l)"
else
    echo "[removed] 0"
fi

