#!/usr/bin/env python3
"""
Script to reduce questions with 5 or 6 answer choices down to 4 choices.
Keeps the correct answer and randomly selects 3 other incorrect answers.
"""

import json
import random
from pathlib import Path
from collections import defaultdict


def reduce_choices(question):
    """
    Reduce a question's choices to 4 if it has 5 or 6.
    Keeps the correct answer and randomly selects 3 incorrect answers.
    Returns the modified question and whether it was changed.
    """
    if 'choices' not in question or 'answer' not in question:
        return question, False
    
    choices = question['choices']
    num_choices = len(choices)
    
    # Only process questions with 5 or 6 choices
    if num_choices not in [5, 6]:
        return question, False
    
    correct_index = question['answer']
    
    # Validate correct_index
    if not isinstance(correct_index, int) or correct_index < 0 or correct_index >= num_choices:
        print(f"  Warning: Invalid answer index {correct_index} for question with {num_choices} choices")
        return question, False
    
    # Get the correct answer
    correct_answer = choices[correct_index]
    
    # Get all incorrect answer indices
    incorrect_indices = [i for i in range(num_choices) if i != correct_index]
    
    # Randomly select 3 incorrect answers
    selected_incorrect_indices = random.sample(incorrect_indices, 3)
    
    # Create new choices list with correct answer and 3 incorrect ones
    new_choices = [choices[i] for i in selected_incorrect_indices]
    new_choices.append(correct_answer)
    
    # Shuffle to randomize position of correct answer
    random.shuffle(new_choices)
    
    # Find new index of correct answer
    new_correct_index = new_choices.index(correct_answer)
    
    # Update question
    modified_question = question.copy()
    modified_question['choices'] = new_choices
    modified_question['answer'] = new_correct_index
    
    return modified_question, True


def process_file(file_path, output_dir):
    """Process a single JSON or JSONL file."""
    questions = []
    modified_count = 0
    total_count = 0
    modified_by_original_count = defaultdict(int)
    
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
                        if 'choices' in data:
                            total_count += 1
                            original_count = len(data['choices'])
                            modified_data, was_modified = reduce_choices(data)
                            questions.append(modified_data)
                            if was_modified:
                                modified_count += 1
                                modified_by_original_count[original_count] += 1
                    except json.JSONDecodeError as e:
                        print(f"  Warning: Could not parse line {line_num}: {e}")
            else:
                # JSON: try different formats
                try:
                    content = f.read()
                    data = json.loads(content)
                    
                    # If it's a list, process each item
                    if isinstance(data, list):
                        for item in data:
                            if 'choices' in item:
                                total_count += 1
                                original_count = len(item['choices'])
                                modified_item, was_modified = reduce_choices(item)
                                questions.append(modified_item)
                                if was_modified:
                                    modified_count += 1
                                    modified_by_original_count[original_count] += 1
                    # If it's a single object with choices
                    elif 'choices' in data:
                        total_count += 1
                        original_count = len(data['choices'])
                        modified_data, was_modified = reduce_choices(data)
                        questions.append(modified_data)
                        if was_modified:
                            modified_count += 1
                            modified_by_original_count[original_count] += 1
                except json.JSONDecodeError:
                    # If not valid JSON, try reading line by line
                    f.seek(0)
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            data = json.loads(line)
                            if 'choices' in data:
                                total_count += 1
                                original_count = len(data['choices'])
                                modified_data, was_modified = reduce_choices(data)
                                questions.append(modified_data)
                                if was_modified:
                                    modified_count += 1
                                    modified_by_original_count[original_count] += 1
                        except json.JSONDecodeError:
                            pass
    except Exception as e:
        print(f"  Error reading {file_path.name}: {e}")
        return None
    
    # Save processed questions to output directory
    if questions:
        output_path = output_dir / file_path.name
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                if file_path.suffix == '.jsonl':
                    # Write as JSONL
                    for question in questions:
                        f.write(json.dumps(question, ensure_ascii=False) + '\n')
                else:
                    # Write as JSON (line by line format to match original)
                    for question in questions:
                        f.write(json.dumps(question, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"  Error writing {output_path.name}: {e}")
            return None
    
    return {
        'total': total_count,
        'modified': modified_count,
        'unchanged': total_count - modified_count,
        'modified_by_original': dict(modified_by_original_count)
    }


def main():
    # Set random seed for reproducibility
    random.seed(42)
    
    # Get the directory where the script is located
    script_dir = Path(__file__).parent
    
    # Create output directory for processed files
    output_dir = script_dir / 'normalized'
    output_dir.mkdir(exist_ok=True)
    
    # Find all JSON and JSONL files in the directory (excluding the script itself)
    json_files = [f for f in script_dir.glob('*.json')]
    jsonl_files = [f for f in script_dir.glob('*.jsonl')]
    all_files = json_files + jsonl_files
    
    if not all_files:
        print("No JSON or JSONL files found in the current directory.")
        return
    
    print(f"Found {len(all_files)} files to process:")
    print(f"  - {len(json_files)} JSON files")
    print(f"  - {len(jsonl_files)} JSONL files")
    print(f"\nProcessed files will be saved to: {output_dir}")
    print(f"\nReducing questions with 5 or 6 choices to 4 choices...")
    print(f"(Keeping correct answer + 3 randomly selected incorrect answers)")
    print()
    
    # Overall statistics
    total_questions = 0
    total_modified = 0
    total_unchanged = 0
    overall_modified_by_original = defaultdict(int)
    file_stats = []
    
    # Process each file
    for file_path in sorted(all_files):
        print(f"Processing: {file_path.name}")
        result = process_file(file_path, output_dir)
        
        if result:
            file_stats.append((file_path.name, result))
            total_questions += result['total']
            total_modified += result['modified']
            total_unchanged += result['unchanged']
            
            for original_count, count in result['modified_by_original'].items():
                overall_modified_by_original[original_count] += count
            
            print(f"  Total questions: {result['total']}")
            print(f"  Modified: {result['modified']}")
            print(f"  Unchanged: {result['unchanged']}")
            if result['modified_by_original']:
                print(f"  Modified breakdown:")
                for original_count in sorted(result['modified_by_original'].keys()):
                    count = result['modified_by_original'][original_count]
                    print(f"    {original_count} → 4 choices: {count}")
        else:
            print(f"  Failed to process file")
        print()
    
    # Print overall summary
    print("=" * 80)
    print("PROCESSING SUMMARY")
    print("=" * 80)
    print(f"Total files processed: {len(file_stats)}")
    print(f"Total questions: {total_questions}")
    print(f"Questions modified: {total_modified}")
    print(f"Questions unchanged: {total_unchanged}")
    print()
    
    if overall_modified_by_original:
        print("Questions modified by original choice count:")
        print("-" * 80)
        for original_count in sorted(overall_modified_by_original.keys()):
            count = overall_modified_by_original[original_count]
            percentage = (count / total_modified * 100) if total_modified > 0 else 0
            print(f"  {original_count} → 4 choices: {count:6d} ({percentage:5.1f}%)")
    
    print("=" * 80)
    print(f"\nProcessed files saved to: {output_dir}/")
    print("Original files remain unchanged.")


if __name__ == "__main__":
    main()
