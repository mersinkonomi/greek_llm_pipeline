# MMLU Dataset Processing Scripts

This directory contains Python scripts for cleaning and normalizing the Greek MMLU dataset.

## Scripts Overview

### 1. `analyze_questions.py`
Analyzes MMLU JSON/JSONL files and provides statistics on:
- Number of questions per file
- Distribution of answer choices (1-10)
- Overall dataset summary

**Usage:**
```bash
python3 analyze_questions.py
```

### 2. `filter_questions.py`
Filters out questions with invalid number of choices (1, 7, 8, 9, or 10).
Keeps only questions with 2-6 answer choices.

**Usage:**
```bash
python3 filter_questions.py
```
**Output:** `filtered/` directory

### 3. `remove_multiselect.py`
Removes questions with multiple correct answers (where `answer` is a list/array instead of a single integer).

**Usage:**
```bash
python3 remove_multiselect.py
```
**Output:** `filtered/cleaned/` directory

### 4. `reduce_to_4_choices.py`
Reduces questions with 5 or 6 answer choices down to 4 choices.
- Keeps the correct answer
- Randomly selects 3 incorrect answers
- Updates answer index accordingly

**Usage:**
```bash
python3 reduce_to_4_choices.py
```
**Output:** `normalized/` directory (relative to input)

### 5. `show_problematic_questions.py`
Identifies and displays questions with invalid answer formats (multi-select questions).

**Usage:**
```bash
python3 show_problematic_questions.py
```

### 6. `analyze_by_group.py`
Analyzes questions by metadata fields:
- Group (STEM, Humanities, Social Sciences, Other)
- Subject
- Level (primary_school, secondary_school, university, professional)

**Usage:**
```bash
python3 analyze_by_group.py
```

## Processing Pipeline

Follow these steps in order to clean and normalize the dataset:

```bash
# Step 1: Analyze original dataset
python3 analyze_questions.py

# Step 2: Filter invalid questions (1, 7-10 choices)
python3 filter_questions.py

# Step 3: Remove multi-select questions
cd filtered/
python3 remove_multiselect.py

# Step 4: Normalize to 2-4 choices
cd cleaned/
python3 reduce_to_4_choices.py

# Step 5: Verify final dataset
cd normalized/
python3 analyze_questions.py
python3 analyze_by_group.py
```

## Final Dataset Statistics

- **Total Questions:** 12,982
- **Questions Removed:** 40
- **Questions Modified:** 361 (5-6 choices → 4 choices)

### Distribution by Answer Choices:
- 2 choices: 1,009 (7.8%)
- 3 choices: 2,735 (21.1%)
- 4 choices: 9,238 (71.2%)

### Distribution by Group:
- Social Sciences: 4,727 (36.4%)
- STEM: 3,468 (26.7%)
- Other: 2,398 (18.5%)
- Humanities: 2,389 (18.4%)

## Requirements

- Python 3.6+
- No external dependencies (uses only standard library)

## File Format

All scripts work with JSON and JSONL files following the MMLU schema:

```json
{
  "question": "Question text",
  "choices": ["Choice A", "Choice B", "Choice C", "Choice D"],
  "answer": 0,
  "group": "STEM",
  "subject": "Mathematics",
  "level": "university",
  "source": "https://example.com"
}
```
