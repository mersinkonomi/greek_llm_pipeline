#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Token Counter

Counts tokens in text files using the Meltemi tokenizer.
Handles multiple encodings and provides detailed statistics.
"""

import os
import argparse
from transformers import AutoTokenizer


def count_tokens_in_file(filepath, tokenizer):
    """Count tokens in a single file with encoding fallback."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
    except UnicodeDecodeError:
        try:
            with open(filepath, "r", encoding="ISO-8859-7") as f:
                text = f.read()
        except UnicodeDecodeError:
            print(f"❌ Skipped (encoding error): {filepath}")
            return None, None
    
    tokens = tokenizer.encode(text, add_special_tokens=False)
    return text, tokens


def count_tokens_in_folder(folder, tokenizer, model_name="ilsp/Meltemi-7B-v1.5"):
    """Count tokens in all text files within a folder and subfolders."""
    total_tokens = 0
    total_chars = 0
    file_count = 0
    failed_count = 0
    
    print(f"📊 Counting tokens with {model_name}")
    print(f"📁 Scanning: {folder or 'current directory'}\n")
    
    for root, dirs, files in os.walk(folder):
        for filename in files:
            if filename.endswith(".txt"):
                filepath = os.path.join(root, filename)
                
                text, tokens = count_tokens_in_file(filepath, tokenizer)
                
                if tokens is not None:
                    chars = len(text)
                    print(f"{filepath} — Chars: {chars:,}, Tokens: {len(tokens):,}")
                    total_tokens += len(tokens)
                    total_chars += chars
                    file_count += 1
                else:
                    failed_count += 1
    
    print(f"\n{'='*60}")
    print(f"✅ Total files processed: {file_count}")
    print(f"❌ Failed files: {failed_count}")
    print(f"📊 Total characters: {total_chars:,}")
    print(f"🪙 Total tokens: {total_tokens:,}")
    
    if file_count > 0:
        avg_chars = total_chars / file_count
        avg_tokens = total_tokens / file_count
        print(f"📈 Average chars per file: {avg_chars:,.0f}")
        print(f"📈 Average tokens per file: {avg_tokens:,.0f}")
    
    return total_tokens


def main():
    parser = argparse.ArgumentParser(description="Count tokens in text files")
    parser.add_argument(
        "folder",
        nargs="?",
        default="",
        help="Folder to scan for .txt files (default: current directory)"
    )
    parser.add_argument(
        "--model",
        default="ilsp/Meltemi-7B-v1.5",
        help="Tokenizer model to use (default: ilsp/Meltemi-7B-v1.5)"
    )
    
    args = parser.parse_args()
    
    # Load tokenizer
    print(f"🔄 Loading tokenizer: {args.model}...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(args.model)
    except Exception as e:
        print(f"❌ Error loading tokenizer: {e}")
        return
    
    # Count tokens
    count_tokens_in_folder(args.folder, tokenizer, args.model)


if __name__ == "__main__":
    main()

