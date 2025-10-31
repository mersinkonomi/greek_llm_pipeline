set -euo pipefail

USER="mersinkonomi"
REPO="greek-llm-pipeline"
EMAIL="mersinkonomi@gmail.com"
REMOTE="https://github.com/$USER/$REPO.git"

# 1) Τοπικός φάκελος
mkdir -p "$HOME/projects/$REPO"
cd "$HOME/projects/$REPO"
git init
git config user.name "Mersin Konomi"
git config user.email "$EMAIL"

# 2) Δομή φακέλων
mkdir -p scraping data_processing evaluation whisper_pipeline samples

# 3) .gitignore
cat > .gitignore << 'EOF'
__pycache__/
*.py[cod]
.venv/
env/
.vscode/
.idea/
.ipynb_checkpoints/
data/
datasets/
outputs/
models/
*.log
.DS_Store
EOF

# 4) README
cat > README.md << 'EOF'
# Greek LLM Pipeline

Data engineering & evaluation pipelines for Greek Generative AI (scripts only).

## Structure
- scraping/ — web scrapers for public Greek sources
- data_processing/ — text normalization, cleaning, MinHash-LSH deduplication utilities
- evaluation/ — LM-Eval tasks & helpers (scripts only)
- whisper_pipeline/ — batch transcription utilities using Whisper
- samples/ — minimal examples (few lines for demos/tests)

> This repository contains scripts only (no datasets or confidential data).

## Highlights
- Large-scale data collection and normalization for Greek generative models
- Deduplication pipelines using MinHash + LSH
- Evaluation scripts compatible with LM-Eval v0.4.0
- Audio transcription utilities (Whisper batch inference)
- Reproducible, modular codebase designed for research environments

## Technologies
Python · PyTorch · Transformers · Pandas · NumPy · tqdm · Whisper · LM-Evaluation-Harness
EOF

# 5) LICENSE (MIT)
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2025 Mersin Konomi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

[...]
EOF

# 6) requirements.txt
printf "%s\n" "# Add libs: numpy, pandas, torch, transformers, tqdm" > requirements.txt

# 7) Commit & push (δημιούργησε πρώτα το public repo στο GitHub χωρίς README)
git add .
git commit -m "Initial ICCS-safe portfolio repo (scripts only)"
git branch -M main
git remote add origin "$REMOTE"
git push -u origin main
