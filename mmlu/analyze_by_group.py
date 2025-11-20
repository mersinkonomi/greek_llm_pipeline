#!/usr/bin/env python3
"""
Script to analyze MMLU questions by group, subject, and level.
"""

import json
from pathlib import Path
from collections import defaultdict


def analyze_by_metadata(file_path):
    """Analyze questions by group, subject, and level."""
    by_group = defaultdict(int)
    by_subject = defaultdict(int)
    by_level = defaultdict(int)
    total = 0
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    data = json.loads(line)
                    total += 1
                    
                    # Count by group
                    group = data.get('group', 'Unknown')
                    by_group[group] += 1
                    
                    # Count by subject
                    subject = data.get('subject', 'Unknown')
                    by_subject[subject] += 1
                    
                    # Count by level
                    level = data.get('level', 'Unknown')
                    by_level[level] += 1
                    
                except json.JSONDecodeError:
                    pass
                    
    except Exception as e:
        print(f"Error reading {file_path.name}: {e}")
        return None
    
    return {
        'total': total,
        'by_group': dict(by_group),
        'by_subject': dict(by_subject),
        'by_level': dict(by_level)
    }


def main():
    # Path to the final dataset
    data_dir = Path('/Users/nino/Desktop/mmlu_final/MMLU/filtered/cleaned/normalized')
    
    # Find all JSON and JSONL files
    json_files = list(data_dir.glob('*.json'))
    jsonl_files = list(data_dir.glob('*.jsonl'))
    all_files = json_files + jsonl_files
    
    if not all_files:
        print("No files found!")
        return
    
    # Overall statistics
    overall_by_group = defaultdict(int)
    overall_by_subject = defaultdict(int)
    overall_by_level = defaultdict(int)
    overall_total = 0
    
    # Process each file
    for file_path in sorted(all_files):
        result = analyze_by_metadata(file_path)
        
        if result:
            overall_total += result['total']
            
            for group, count in result['by_group'].items():
                overall_by_group[group] += count
            
            for subject, count in result['by_subject'].items():
                overall_by_subject[subject] += count
            
            for level, count in result['by_level'].items():
                overall_by_level[level] += count
    
    # Print results
    print("=" * 80)
    print("MMLU DATASET ANALYSIS BY METADATA")
    print("=" * 80)
    print(f"Total questions: {overall_total}")
    print()
    
    # By Group
    print("QUESTIONS BY GROUP:")
    print("-" * 80)
    for group in sorted(overall_by_group.keys()):
        count = overall_by_group[group]
        percentage = (count / overall_total * 100) if overall_total > 0 else 0
        print(f"  {group:30s}: {count:6d} ({percentage:5.1f}%)")
    print()
    
    # By Subject
    print("QUESTIONS BY SUBJECT:")
    print("-" * 80)
    for subject in sorted(overall_by_subject.keys()):
        count = overall_by_subject[subject]
        percentage = (count / overall_total * 100) if overall_total > 0 else 0
        print(f"  {subject:40s}: {count:6d} ({percentage:5.1f}%)")
    print()
    
    # By Level
    print("QUESTIONS BY LEVEL:")
    print("-" * 80)
    for level in sorted(overall_by_level.keys()):
        count = overall_by_level[level]
        percentage = (count / overall_total * 100) if overall_total > 0 else 0
        print(f"  {level:30s}: {count:6d} ({percentage:5.1f}%)")
    
    print("=" * 80)


if __name__ == "__main__":
    main()
