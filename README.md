# MMLU Final Dataset - Combined JSON Files

This repository contains a combined dataset from the MMLU (Massive Multitask Language Understanding) final collection, with questions in Greek language.

## Contents

- **combined_data.json** - Combined dataset with 488 items from multiple subject areas
- **process_data.py** - Python script to combine individual JSON files
- **data/** - Source JSON files from different subjects

## Dataset Structure

Each item in the dataset contains:
- `question` - The question text (in Greek)
- `choices` - Array of answer choices
- `answer` - Index of the correct answer (0-based)
- `group` - Subject group (e.g., "STEM", "Social Sciences")
- `subject` - Specific subject (e.g., "Agroculture", "Education", "Computer Science", "Medicine")
- `level` - Difficulty level (e.g., "professional", "university")
- `source` - URL source of the question

## Statistics

- **Total Items**: 488
- **Subjects**: Agriculture, Computer Science, Education Methodology, Medicine
- **Language**: Greek
- **Format**: JSON

## Source Files

The combined dataset was created from the following files:
1. `agro_final.json` - Agriculture questions
2. `compsci.json` - Computer Science questions
3. `education_methodology.json` - Education questions
4. `medicine_final.json` - Medicine questions

## Usage

To combine the JSON files yourself:

```bash
python3 process_data.py
```

This will read all JSON files from the `data/` directory and create `combined_data.json`.

## Requirements

- Python 3.x
- No external dependencies required

## License

Please refer to the original MMLU dataset license and source URLs provided in each question.
