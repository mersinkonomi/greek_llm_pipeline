"""
Pipeline configuration for MinHash deduplication.

Modify these settings to adjust the deduplication pipeline behavior.
"""

import pathlib

# Base paths
BASE = pathlib.Path("./data").resolve()
INP = BASE / "jsonl_input" / "combined_exact_dedup.jsonl"
OUTB = BASE / "minhash"

# spaCy language code for tokenization
SPACY_LANG = "el"  # Greek

# MinHash configuration
from datatrove.pipeline.dedup.minhash import MinhashConfig
from datatrove.utils.hashing import HashConfig

CFG = MinhashConfig(
    hash_config=HashConfig(precision=32),
    n_grams=4,
    num_buckets=1,  # 1 for single machine, increase for distributed
    hashes_per_bucket=6,
)

# Export for use in scripts
__all__ = ["BASE", "INP", "OUTB", "SPACY_LANG", "CFG"]

