#!/usr/bin/env python3
"""
Stage 4: Filter out duplicates and create deduplicated output.

Removes duplicate documents based on the cluster analysis and writes
both kept and removed documents to separate outputs.
"""
from datatrove.executor.local import LocalPipelineExecutor
from datatrove.pipeline.readers import JsonlReader
from datatrove.pipeline.dedup.minhash import MinhashDedupFilter
from datatrove.pipeline.writers.jsonl import JsonlWriter

# Import configuration
import sys
sys.path.append('..')
from config.pipeline_conf import INP, OUTB

def make_writer(folder: str):
    """Create a JsonlWriter with compression handling."""
    try:
        return JsonlWriter(output_folder=folder, compression=None)
    except TypeError:
        return JsonlWriter(output_folder=folder)

pipe = [
    JsonlReader(INP, text_key="text", doc_progress=True),
    MinhashDedupFilter(
        input_folder=f"{OUTB}/remove_ids",
        exclusion_writer=make_writer(f"{OUTB}/removed"),
    ),
    make_writer(f"{OUTB}/deduplicated_output"),
]

LocalPipelineExecutor(pipeline=pipe).run()
print(f"[Stage4] written -> {OUTB}/deduplicated_output and {OUTB}/removed")

