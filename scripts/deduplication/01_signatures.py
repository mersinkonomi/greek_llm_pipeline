#!/usr/bin/env python3
"""
Stage 1: Generate MinHash signatures for deduplication.

This script reads JSONL files and creates MinHash signatures for each document.
Signatures are used to detect near-duplicate documents efficiently.
"""
import pathlib
from datatrove.executor.local import LocalPipelineExecutor
from datatrove.pipeline.readers import JsonlReader
from datatrove.pipeline.dedup.minhash import MinhashDedupSignature

# Import configuration
import sys
sys.path.append('..')
from config.pipeline_conf import INP, OUTB, CFG, SPACY_LANG

pathlib.Path(f"{OUTB}/signatures").mkdir(parents=True, exist_ok=True)

pipe = [
    JsonlReader(INP, text_key="text", doc_progress=True),
    MinhashDedupSignature(output_folder=f"{OUTB}/signatures", config=CFG, language=SPACY_LANG),
]

LocalPipelineExecutor(pipeline=pipe).run()
print(f"[Stage1] signatures -> {OUTB}/signatures")

