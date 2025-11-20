#!/usr/bin/env python3
"""
Script to remove questions with invalid answer formats (multi-select questions).
Only keeps questions where 'answer' is a single integer.
"""

import json
from pathlib import Path


def filter_valid_questions(file_path, output_path):
    """Filter out questions with invalid answer formats."""
    valid_questions = []
    removed_count = 0
    total_count = 0
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    data = json.loads(line)
                    total_count += 1
                    
                    # Check if answer is a valid single integer
                    if 'answer' in data:
                        answer = data['answer']
                        
                        # Only keep if answer is a single integer
                        if isinstance(answer, int):
                            # Also validate it's within range if choices exist
                            if 'choices' in data:
                                num_choices = len(data['choices'])
                                if 0 <= answer < num_choices:
                                    valid_questions.append(data)
                                else:
                                    removed_count += 1
                                    print(f"  Removed line {line_num}: answer {answer} out of range for {num_choices} choices")
                            else:
                                valid_questions.append(data)
                        else:
                            removed_count += 1
                            print(f"  Removed line {line_num}: answer is {type(answer).__name__}, not int")
                    else:
                        # Keep questions without answer field
                        valid_questions.append(data)
                        
                except json.JSONDecodeError as e:
                    print(f"  Warning: Could not parse line {line_num}: {e}")
                    
    except Exception as e:
        print(f"Error reading file: {e}")
        return None
    
    # Write valid questions to output file
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            for question in valid_questions:
                f.write(json.dumps(question, ensure_ascii=False) + '\n')
    except Exception as e:
        print(f"Error writing file: {e}")
        return None
    
    return {
        'total': total_count,
        'kept': len(valid_questions),
        'removed': removed_count
    }


def main():
    # Process the filtered directory
    input_dir = Path('/Users/nino/Desktop/mmlu_final/MMLU/filtered')
    output_dir = input_dir / 'cleaned'
    output_dir.mkdir(exist_ok=True)
    
    # Find all JSON and JSONL files
    json_files = list(input_dir.glob('*.json'))
    jsonl_files = list(input_dir.glob('*.jsonl'))
    all_files = json_files + jsonl_files
    
    if not all_files:
        print("No files found to process.")
        return
    
    print(f"Found {len(all_files)} files to clean")
    print(f"Output directory: {output_dir}")
    print(f"\nRemoving questions with multi-select answers (answer as list/array)...\n")
    
    total_kept = 0
    total_removed = 0
    total_questions = 0
    
    for file_path in sorted(all_files):
        print(f"Processing: {file_path.name}")
        output_path = output_dir / file_path.name
        
        result = filter_valid_questions(file_path, output_path)
        
        if result:
            total_questions += result['total']
            total_kept += result['kept']
            total_removed += result['removed']
            
            print(f"  Total: {result['total']}, Kept: {result['kept']}, Removed: {result['removed']}")
        else:
            print(f"  Failed to process")
        print()
    
    print("=" * 80)
    print("CLEANING SUMMARY")
    print("=" * 80)
    print(f"Total files processed: {len(all_files)}")
    print(f"Total questions: {total_questions}")
    print(f"Questions kept: {total_kept}")
    print(f"Questions removed: {total_removed}")
    print("=" * 80)
    print(f"\nCleaned files saved to: {output_dir}/")


if __name__ == "__main__":
    main()
