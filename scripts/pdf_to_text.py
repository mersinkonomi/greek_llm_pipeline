#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF to Text Converter using PyMuPDF (pymupdf4llm)

Converts PDF files to plain text (Markdown format) for processing in the Greek LLM pipeline.
Recursively scans source folders and extracts text from all PDF files.
"""

import os
import sys
from pathlib import Path

try:
    import pymupdf4llm  # pip install pymupdf4llm
except ImportError:
    print("Error: pymupdf4llm not installed. Run: pip install pymupdf4llm")
    sys.exit(1)

# --- Source PDF folders ---
PDF_FOLDERS = [
    "./data/sources/Ebooks4GreeksPDFs",
    "./data/sources/OpenBooksPDFs",
    "./data/sources/free-ebooks",
]

# --- Output root directory ---
OUTPUT_ROOT = Path("./data/pdf_outputs")
OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

VALID_EXTS = {".pdf"}  # File extensions to process
SKIP_EMPTY = True      # Skip if output file already exists and is non-empty


def convert_one_pdf(pdf_path: Path, source_name: str) -> bool:
    """
    Convert a single PDF file to markdown text.
    
    Args:
        pdf_path: Path to the PDF file
        source_name: Name of the source folder
    
    Returns:
        True if successful, False otherwise
    """
    out_dir = OUTPUT_ROOT / source_name
    out_dir.mkdir(parents=True, exist_ok=True)

    txt_path = out_dir / (pdf_path.stem + ".txt")
    tmp_path = txt_path.with_suffix(".txt.part")

    # Skip if output already exists and is non-empty
    if SKIP_EMPTY and txt_path.exists() and txt_path.stat().st_size > 0:
        print(f"⏩ Skipping (already processed): {pdf_path.name}")
        return False

    try:
        # Convert PDF to markdown
        md_text = pymupdf4llm.to_markdown(str(pdf_path))
        
        # Write to temporary file first, then rename (atomic operation)
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(md_text)
        os.replace(tmp_path, txt_path)
        
        print(f"✅ Saved: {txt_path}")
        return True
        
    except Exception as e:
        # Clean up temporary file on error
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass
        print(f"❌ Error reading {pdf_path}: {e}")
        return False


def walk_and_convert(root_folder: Path) -> tuple[int, int]:
    """
    Recursively scan a folder for PDFs and convert them.
    
    Args:
        root_folder: Root folder to scan
    
    Returns:
        Tuple of (total_found, total_saved)
    """
    source_name = root_folder.name
    found = saved = 0
    
    for dirpath, _, filenames in os.walk(root_folder):
        for name in filenames:
            if Path(name).suffix.lower() not in VALID_EXTS:
                continue
            
            pdf_path = Path(dirpath) / name
            found += 1
            
            if convert_one_pdf(pdf_path, source_name):
                saved += 1
    
    return found, saved


def main():
    """Main function to process all PDF folders."""
    folders = [Path(p) for p in PDF_FOLDERS]
    
    # Allow additional folders to be passed as command-line arguments
    if len(sys.argv) > 1:
        folders.extend(Path(p) for p in sys.argv[1:])

    total_found = total_saved = 0
    
    for folder in folders:
        if not folder.is_dir():
            print(f"⚠️ Skipping (not a directory): {folder}")
            continue
        
        print(f"\n📂 Scanning source: {folder}")
        found, saved = walk_and_convert(folder)
        total_found += found
        total_saved += saved
        print(f"— Source summary [{folder.name}]: PDFs found={found}, converted={saved}")

    print(f"\n🎯 All done! Total PDFs scanned={total_found}, converted={total_saved}")
    print(f"📁 Outputs are stored in: {OUTPUT_ROOT}")


if __name__ == "__main__":
    main()

