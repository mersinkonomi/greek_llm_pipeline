import json
import re
import glob
import os

# Manual corrections for broken words found in the dataset
CORRECTIONS = {
    # Broken words with spaces
    'ετ ών': 'ετών',
    'κ αι': 'και',
    'Λ ευχαιμία': 'Λευχαιμία',
    'θ υρεοειδίτιδα': 'θυρεοειδίτιδα',
    'β ρογχοκήλη': 'βρογχοκήλη',
    'θυρ εοειδούς': 'θυρεοειδούς',
    'ό τ': 'ότι',
    'ά π': 'άλλο',
    'ή σ': 'ήδη',
    'ί ε': 'ίδιο',
    'ώ κ': 'ώστε',
}

def fix_text(text):
    """Apply manual corrections to text"""
    if not isinstance(text, str):
        return text
    
    # Apply all corrections
    for broken, fixed in CORRECTIONS.items():
        text = text.replace(broken, fixed)
    
    return text

def fix_item(item):
    """Recursively fix text in a JSON item"""
    if isinstance(item, dict):
        return {key: fix_item(value) for key, value in item.items()}
    elif isinstance(item, list):
        return [fix_item(element) for element in item]
    elif isinstance(item, str):
        return fix_text(item)
    else:
        return item

def process_file(input_file):
    """Process a single JSON file"""
    print(f"Processing {input_file}...")
    
    data = []
    with open(input_file, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            if not isinstance(data, list):
                data = [data]
        except json.JSONDecodeError:
            # Try JSON Lines format
            f.seek(0)
            for line in f:
                if line.strip():
                    try:
                        data.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    
    # Fix text in all items
    fixed_data = [fix_item(item) for item in data]
    
    print(f"  Processed {len(fixed_data)} items")
    return fixed_data

def main():
    data_dir = "data"
    
    # Process all JSON files and combine
    all_data = []
    files = sorted(glob.glob(os.path.join(data_dir, "*.json")))
    
    for file_path in files:
        basename = os.path.basename(file_path)
        if basename == "combined_data.json":
            continue
        
        fixed_data = process_file(file_path)
        all_data.extend(fixed_data)
    
    # Save combined file
    output_file = "combined_data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Combined {len(all_data)} items into {output_file}")
    
    # Show statistics
    subjects = {}
    for item in all_data:
        subject = item.get('subject', 'Unknown')
        subjects[subject] = subjects.get(subject, 0) + 1
    
    print("\nDataset statistics:")
    for subject, count in sorted(subjects.items()):
        print(f"  {subject}: {count} items")

if __name__ == "__main__":
    main()
