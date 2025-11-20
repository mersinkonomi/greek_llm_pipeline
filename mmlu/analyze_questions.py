#!/usr/bin/env python3
"""
Script to analyze MMLU schema JSON/JSONL files and count questions by number of answer choices.
"""

import json
import os
from collections import defaultdict
from pathlib import Path


def analyze_file(file_path):
    """Analyze a single JSON or JSONL file and count questions by number of choices."""
    choice_counts = defaultdict(int)
    total_questions = 0
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Determine if it's JSON or JSONL based on extension
            if file_path.suffix == '.jsonl':
                # JSONL: one JSON object per line
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        if 'choices' in data and isinstance(data['choices'], list):
                            num_choices = len(data['choices'])
                            choice_counts[num_choices] += 1
                            total_questions += 1
                    except json.JSONDecodeError as e:
                        print(f"  Warning: Could not parse line in {file_path.name}: {e}")
            else:
                # JSON: single JSON object or array
                try:
                    content = f.read()
                    # Try to parse as JSON object first
                    data = json.loads(content)
                    
                    # If it's a list, process each item
                    if isinstance(data, list):
                        for item in data:
                            if 'choices' in item and isinstance(item['choices'], list):
                                num_choices = len(item['choices'])
                                choice_counts[num_choices] += 1
                                total_questions += 1
                    # If it's a single object with choices
                    elif 'choices' in data and isinstance(data['choices'], list):
                        num_choices = len(data['choices'])
                        choice_counts[num_choices] += 1
                        total_questions += 1
                except json.JSONDecodeError:
                    # If not valid JSON, try reading line by line
                    f.seek(0)
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            data = json.loads(line)
                            if 'choices' in data and isinstance(data['choices'], list):
                                num_choices = len(data['choices'])
                                choice_counts[num_choices] += 1
                                total_questions += 1
                        except json.JSONDecodeError:
                            pass
    except Exception as e:
        print(f"  Error reading {file_path.name}: {e}")
    
    return choice_counts, total_questions


def main():
    # Get the directory where the script is located
    script_dir = Path(__file__).parent
    
    # Find all JSON and JSONL files in the directory
    json_files = list(script_dir.glob('*.json'))
    jsonl_files = list(script_dir.glob('*.jsonl'))
    all_files = json_files + jsonl_files
    
    if not all_files:
        print("No JSON or JSONL files found in the current directory.")
        return
    
    print(f"Found {len(all_files)} files to analyze:")
    print(f"  - {len(json_files)} JSON files")
    print(f"  - {len(jsonl_files)} JSONL files")
    print()
    
    # Overall statistics
    overall_choice_counts = defaultdict(int)
    overall_total = 0
    file_stats = []
    
    # Process each file
    for file_path in sorted(all_files):
        print(f"Analyzing: {file_path.name}")
        choice_counts, total = analyze_file(file_path)
        
        if total > 0:
            file_stats.append((file_path.name, choice_counts, total))
            for num_choices, count in choice_counts.items():
                overall_choice_counts[num_choices] += count
            overall_total += total
            
            # Print file statistics
            print(f"  Total questions: {total}")
            for num_choices in sorted(choice_counts.keys()):
                count = choice_counts[num_choices]
                percentage = (count / total) * 100
                print(f"    {num_choices} answer(s): {count} ({percentage:.1f}%)")
        else:
            print(f"  No questions found or invalid format")
        print()
    
    # Print overall summary
    print("=" * 80)
    print("OVERALL SUMMARY")
    print("=" * 80)
    print(f"Total files analyzed: {len(file_stats)}")
    print(f"Total questions: {overall_total}")
    print()
    print("Questions by number of answer choices:")
    print("-" * 80)
    
    # Print in order from 1 to 6 (or max found)
    max_choices = max(overall_choice_counts.keys()) if overall_choice_counts else 0
    for num_choices in range(1, max(7, max_choices + 1)):
        count = overall_choice_counts.get(num_choices, 0)
        if count > 0 or num_choices <= 6:  # Always show 1-6, even if 0
            percentage = (count / overall_total * 100) if overall_total > 0 else 0
            print(f"  {num_choices} answer(s): {count:6d} ({percentage:5.1f}%)")
    
    print("=" * 80)


if __name__ == "__main__":
    main()
