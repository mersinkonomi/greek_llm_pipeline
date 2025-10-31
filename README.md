# Greek MMLU Schema

This repository contains Greek-language MMLU-style datasets in JSONL format under `mmlu_final/`.

## File format (JSONL)
Each line is a JSON object with:
- `question` (string): The prompt in Greek.
- `choices` (array of strings): Multiple-choice options in order.
- `answer` (integer): Zero-based index into `choices`. Use `-1` if unknown/invalid.
- `group` (string): High-level group (e.g., `STEM`, `Humanities`).
- `subject` (string): Subject name (e.g., `Computer Science`).
- `level` (string): Difficulty level (e.g., `university`, `high_school`).
- `source` (string): Provenance, e.g., `user_provided_text`.

Example:
```json
{"question": "Παράδειγμα ερώτησης?", "choices": ["Α", "Β", "Γ", "Δ"], "answer": 1, "group": "STEM", "subject": "Computer Science", "level": "university", "source": "user_provided_text"}
```

## JSON Schema
See `mmlu_schema.json` for machine validation of JSONL rows.

Validate a file (requires `ajv`):
```bash
npx ajv validate -s mmlu_schema.json -d mmlu_final/compsci.txt --spec=draft2020 --errors=text --allow-union-types -c ajv-formats
```

## Directory layout
- `mmlu_final/` — dataset splits (`agro_final.txt`, `compsci.txt`, `education_methodology.txt`, `medicine_final.txt`, ...)

## Notes
- `answer` must be `-1` or a valid index in `choices`.
- All strings are UTF-8; files are newline-delimited JSON (JSONL).


