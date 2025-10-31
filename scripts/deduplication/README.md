# MinHash Deduplication Pipeline

DataTrove-based MinHash deduplication for Greek language datasets using the [DataTrove library](https://github.com/huggingface/datatrove).

## Overview

This pipeline uses MinHash LSH (Locality-Sensitive Hashing) to efficiently detect and remove near-duplicate documents from large Greek text datasets. The process runs in 4 stages:

1. **Signatures** - Generate MinHash signatures for each document
2. **Buckets** - Group similar signatures into buckets
3. **Clusters** - Identify duplicate document clusters
4. **Filter** - Remove duplicates while keeping one representative per cluster

## Installation

First install the required dependencies:

```bash
pip install datatrove[all] spacy transformers pandas
python -m spacy download el  # Greek language model
```

## Usage

### Quick Start - Full Pipeline

Run the complete pipeline with a single command:

```bash
python scripts/deduplication/run_full_pipeline.py
```

This will:
- Process input from `data/jsonl_input/combined_exact_dedup.jsonl`
- Create MinHash signatures
- Generate buckets and clusters
- Filter duplicates
- Create final output in `data/minhash/deduplicated_output/`
- Generate statistics

### Stage-by-Stage Execution

For more control, run each stage individually:

```bash
# Stage 1: Generate signatures
python scripts/deduplication/01_signatures.py

# Stage 2: Create buckets
python scripts/deduplication/02_buckets.py

# Stage 3: Cluster documents
python scripts/deduplication/03_cluster.py

# Stage 4: Filter duplicates
python scripts/dedu-platform/04_filter.py

# Stage 5: Concatenate and report
bash scripts/deduplication/05_concat_report.sh
```

### Configuration

Edit `config/pipeline_conf.py` to adjust settings:

```python
# MinHash parameters
CFG = MinhashConfig(
    hash_config=HashConfig(precision=32),  # Higher = more precision
    n_grams=4,                                  # Larger = longer phrases
    num_buckets=1,                          # 1 for single machine
    hashes_per_bucket=6,                    # More = better detection
)

# Language settings
SPACY_LANG = "el"  # Greek language tokenization
```

### Statistics

Generate detailed statistics by source:

```bash
python scripts/deduplication/stats_by_source.py \
    --pre data/jsonl_input \
    --post data/minhash/deduplicated_output \
    --outdir data/stats
```

## Output

After running the pipeline:

- `data/minhash/signatures/` - MinHash signatures
- `data/minhash/buckets/` - Bucket assignments
- `data/minhash/remove_ids/` - List of duplicate IDs to remove
- `data/minhash/deduplicated_output/` - Clean dataset (kept documents)
- `data/minhash/removed/` - Removed duplicates
- `data/minhash/deduplicated_combined.jsonl` - Single combined output file
- `data/stats/` - Detailed statistics

## Performance Tuning

- **precision**: 32-64 bit hash precision (higher = more accurate, slower)
- **n_grams**: 4-7 tokens per n-gram (larger = better for longer duplicates)
- **num_buckets**: Use 14+ for distributed processing
- **hashes_per_bucket**: 6-10 (more = better duplicate detection)

## References

- [DataTrove Documentation](https://github.com/huggingface/datatrove)
- [MinHash Algorithm](https://en.wikipedia.org/wiki/MinHash)

