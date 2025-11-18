#!/usr/bin/env python3
"""
Stage 2: Create buckets from signatures.

Groups documents with similar MinHash signatures into buckets for efficient
comparison in the clustering stage.
"""
from datatrove.executor.local import LocalPipelineExecutor
from datatrove.pipeline.dedup.minhash import MinhashDedupBuckets

# Import configuration
import sys
sys.path.append('..')
from config.pipeline_conf import OUTB, CFG

pipe = [
    MinhashDedupBuckets(
        input_folder=f"{OUTB}/signatures",
        output_folder=f"{OUTB}/buckets",
        config=CFG,
    ),
]

LocalPipelineExecutor(pipeline=pipe).run()
print(f"[Stage2] buckets -> {OUTB}/buckets")

