#!/usr/bin/env python3
"""
Script to find and display questions with invalid answer formats.
"""

import json
from pathlib import Path


def find_problematic_questions(file_path):
    """Find questions with invalid answer formats."""
    problematic = []
    line_num = 0
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line_num += 1
                line = line.strip()
                if not line:
                    continue
                
                try:
                    data = json.loads(line)
                    
                    # Check if it has choices and answer fields
                    if 'choices' in data and 'answer' in data:
                        num_choices = len(data['choices'])
                        answer = data['answer']
                        
                        # Check if answer is not a single integer
                        if not isinstance(answer, int):
                            problematic.append({
                                'line': line_num,
                                'question': data.get('question', 'N/A')[:100],  # First 100 chars
                                'choices_count': num_choices,
                                'answer': answer,
                                'answer_type': type(answer).__name__,
                                'full_data': data
                            })
                        # Check if answer index is out of range
                        elif answer < 0 or answer >= num_choices:
                            problematic.append({
                                'line': line_num,
                                'question': data.get('question', 'N/A')[:100],
                                'choices_count': num_choices,
                                'answer': answer,
                                'answer_type': 'int (out of range)',
                                'full_data': data
                            })
                            
                except json.JSONDecodeError as e:
                    # Skip lines that can't be parsed
                    pass
                    
    except Exception as e:
        print(f"Error reading file: {e}")
        return []
    
    return problematic


def main():
    # Path to the problematic file
    file_path = Path('/Users/nino/Desktop/mmlu_final/MMLU/filtered/questions_eclass.jsonl')
    
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return
    
    print(f"Analyzing: {file_path.name}")
    print("=" * 80)
    
    problems = find_problematic_questions(file_path)
    
    if not problems:
        print("No problematic questions found!")
        return
    
    print(f"\nFound {len(problems)} questions with issues:\n")
    
    for i, problem in enumerate(problems, 1):
        print(f"\n{'=' * 80}")
        print(f"PROBLEM #{i}")
        print(f"{'=' * 80}")
        print(f"Line number: {problem['line']}")
        print(f"Question: {problem['question']}...")
        print(f"Number of choices: {problem['choices_count']}")
        print(f"Answer value: {problem['answer']}")
        print(f"Answer type: {problem['answer_type']}")
        print(f"\nFull question data:")
        print("-" * 80)
        print(json.dumps(problem['full_data'], indent=2, ensure_ascii=False))
    
    print(f"\n{'=' * 80}")
    print(f"Total problematic questions: {len(problems)}")
    print(f"{'=' * 80}")


if __name__ == "__main__":
    main()
