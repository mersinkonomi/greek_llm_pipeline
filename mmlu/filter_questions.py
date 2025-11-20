#!/usr/bin/env python3
"""
Script to filter out questions with 1, 7, 8, 9, or 10 answer choices from MMLU files.
Only keeps questions with 2, 3, 4, 5, or 6 answer choices.
"""

import json
import os
from pathlib import Path
from collections import defaultdict


def filter_file(file_path, output_dir):
    """Filter questions in a single JSON or JSONL file."""
    valid_choices = {2, 3, 4, 5, 6}  # Only keep questions with these numbers of choices
    
    kept_questions = []
    removed_questions = []
    removed_by_choice_count = defaultdict(int)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Determine if it's JSON or JSONL based on extension
            if file_path.suffix == '.jsonl':
                # JSONL: one JSON object per line
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        if 'choices' in data and isinstance(data['choices'], list):
                            num_choices = len(data['choices'])
                            if num_choices in valid_choices:
                                kept_questions.append(data)
                            else:
                                removed_questions.append(data)
                                removed_by_choice_count[num_choices] += 1
                    except json.JSONDecodeError as e:
                        print(f"  Warning: Could not parse line {line_num} in {file_path.name}: {e}")
            else:
                # JSON: try different formats
                try:
                    content = f.read()
                    data = json.loads(content)
                    
                    # If it's a list, process each item
                    if isinstance(data, list):
                        for item in data:
                            if 'choices' in item and isinstance(item['choices'], list):
                                num_choices = len(item['choices'])
                                if num_choices in valid_choices:
                                    kept_questions.append(item)
                                else:
                                    removed_questions.append(item)
                                    removed_by_choice_count[num_choices] += 1
                    # If it's a single object with choices
                    elif 'choices' in data and isinstance(data['choices'], list):
                        num_choices = len(data['choices'])
                        if num_choices in valid_choices:
                            kept_questions.append(data)
                        else:
                            removed_questions.append(data)
                            removed_by_choice_count[num_choices] += 1
                except json.JSONDecodeError:
                    # If not valid JSON, try reading line by line
                    f.seek(0)
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            data = json.loads(line)
                            if 'choices' in data and isinstance(data['choices'], list):
                                num_choices = len(data['choices'])
                                if num_choices in valid_choices:
                                    kept_questions.append(data)
                                else:
                                    removed_questions.append(data)
                                    removed_by_choice_count[num_choices] += 1
                        except json.JSONDecodeError:
                            pass
    except Exception as e:
        print(f"  Error reading {file_path.name}: {e}")
        return None
    
    # Save filtered questions to output directory
    if kept_questions:
        output_path = output_dir / file_path.name
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                if file_path.suffix == '.jsonl':
                    # Write as JSONL
                    for question in kept_questions:
                        f.write(json.dumps(question, ensure_ascii=False) + '\n')
                else:
                    # Write as JSON (line by line format to match original)
                    for question in kept_questions:
                        f.write(json.dumps(question, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"  Error writing {output_path.name}: {e}")
            return None
    
    return {
        'kept': len(kept_questions),
        'removed': len(removed_questions),
        'removed_by_choice': dict(removed_by_choice_count)
    }


def main():
    # Get the directory where the script is located
    script_dir = Path(__file__).parent
    
    # Create output directory for filtered files
    output_dir = script_dir / 'filtered'
    output_dir.mkdir(exist_ok=True)
    
    # Find all JSON and JSONL files in the directory
    json_files = list(script_dir.glob('*.json'))
    jsonl_files = list(script_dir.glob('*.jsonl'))
    all_files = json_files + jsonl_files
    
    if not all_files:
        print("No JSON or JSONL files found in the current directory.")
        return
    
    print(f"Found {len(all_files)} files to filter:")
    print(f"  - {len(json_files)} JSON files")
    print(f"  - {len(jsonl_files)} JSONL files")
    print(f"\nFiltered files will be saved to: {output_dir}")
    print(f"\nFiltering out questions with 1, 7, 8, 9, or 10 answer choices...")
    print(f"Keeping only questions with 2, 3, 4, 5, or 6 answer choices.")
    print()
    
    # Overall statistics
    total_kept = 0
    total_removed = 0
    overall_removed_by_choice = defaultdict(int)
    file_stats = []
    
    # Process each file
    for file_path in sorted(all_files):
        print(f"Processing: {file_path.name}")
        result = filter_file(file_path, output_dir)
        
        if result:
            file_stats.append((file_path.name, result))
            total_kept += result['kept']
            total_removed += result['removed']
            
            for num_choices, count in result['removed_by_choice'].items():
                overall_removed_by_choice[num_choices] += count
            
            print(f"  Kept: {result['kept']} questions")
            print(f"  Removed: {result['removed']} questions")
            if result['removed_by_choice']:
                print(f"  Removed breakdown:")
                for num_choices in sorted(result['removed_by_choice'].keys()):
                    count = result['removed_by_choice'][num_choices]
                    print(f"    {num_choices} choice(s): {count}")
        else:
            print(f"  Failed to process file")
        print()
    
    # Print overall summary
    print("=" * 80)
    print("FILTERING SUMMARY")
    print("=" * 80)
    print(f"Total files processed: {len(file_stats)}")
    print(f"Total questions kept: {total_kept}")
    print(f"Total questions removed: {total_removed}")
    print()
    
    if overall_removed_by_choice:
        print("Questions removed by choice count:")
        print("-" * 80)
        for num_choices in sorted(overall_removed_by_choice.keys()):
            count = overall_removed_by_choice[num_choices]
            percentage = (count / total_removed * 100) if total_removed > 0 else 0
            print(f"  {num_choices} choice(s): {count:6d} ({percentage:5.1f}%)")
    
    print("=" * 80)
    print(f"\nFiltered files saved to: {output_dir}/")
    print("Original files remain unchanged.")


if __name__ == "__main__":
    main()
