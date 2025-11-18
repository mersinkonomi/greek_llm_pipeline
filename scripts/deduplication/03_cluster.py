#!/usr/bin/env python3
"""
Stage 3: Cluster documents and identify duplicates.

Analyzes buckets to find duplicate document clusters. Creates a list of IDs
to remove, keeping one representative from each cluster.
"""
from datatrove.executor.local import LocalPipelineExecutor
from datatrove.pipeline.dedup.minhash import MinhashDedupCluster

# Import configuration
import sys
sys.path.append('..')
from config.pipeline_conf import OUTB, CFG

pipe = [
    MinhashDedupCluster(
        input_folder=f"{OUTB}/buckets",
        output_folder=f"{OUTB}/remove_ids",
        config=CFG,
    ),
]

LocalPipelineExecutor(pipeline=pipe).run()
print(f"[Stage3] remove_ids -> {OUTB}/remove_ids")

