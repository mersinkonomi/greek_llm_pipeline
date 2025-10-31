#!/usr/bin/env python3
"""
normalize_stats_cli.py
Counts BEFORE stats on text files (bytes, lines, words, chars, optional Meltemi tokens) →
normalizes files (mirror or in-place, with ENOSPC fallback) → counts AFTER stats and writes CSV reports.

Examples:
  python normalize_stats_cli.py --root "/Users/nino/Documents/txt_outputs" --out "/Users/nino/Documents/txt_outputs_normalized" --write-mode auto --ext .txt --tokenizer-path "/Users/nino/models/meltemi-7b-v1.5-tokenizer" --chunks 1000000
  # In-place (low disk):
  python normalize_stats_cli.py --root "/Users/nino/Documents/txt_outputs" --write-mode inplace --ext .txt
"""
from __future__ import annotations
from pathlib import Path
from datetime import datetime
import argparse, os, re, unicodedata, errno, shutil, sys
import pandas as pd

# ---------- tokenizer (optional) ----------
def try_load_tokenizer(tokenizer_path: str | None, hf_model_id: str | None, hf_token: str | None):
    try:
        from transformers import AutoTokenizer  # type: ignore
    except Exception:
        print("⚠️  transformers not installed; token counting will be NA.", file=sys.stderr)
        return None, None
    candidates: list[tuple[str, bool, str | None]] = []
    if tokenizer_path:
        candidates.append((tokenizer_path, True, None))
    if hf_model_id:
        candidates.append((hf_model_id, False, hf_token))
    last_err = None
    for src, local_only, token in candidates:
        try:
            tok = AutoTokenizer.from_pretrained(
                src, use_fast=True, local_files_only=local_only, token=token
            )
            tok.pad_token = tok.pad_token or tok.eos_token
            return tok, src
        except Exception as e:
            last_err = e
            continue
    if tokenizer_path or hf_model_id:
        print(f"⚠️  Could not load tokenizer (last error: {last_err}); tokens will be NA.", file=sys.stderr)
    return None, None

# ---------- normalization helpers ----------
DASH_MAP  = {"\u2012":"-","\u2013":"-","\u2014":"-","\u2015":"-","\u2212":"-"}
QUOTE_MAP = {"“":'"',"”":'"',"„":'"',"«":'"',"»":'"',"’":"'", "‘":"'", "`":"'"}
ZERO_WIDTH_RE = re.compile(r"[\u200B\u200C\u200D\u2060\uFEFF]")
SAFE_EXTS = {".json", ".jsonl", ".csv", ".tsv", ".xml", ".html", ".htm"}

def normalization_mode_for_suffix(suffix: str) -> str:
    return "safe" if suffix.lower() in SAFE_EXTS else "loose"

def normalize_line(line: str, mode: str) -> str:
    line = ZERO_WIDTH_RE.sub("", line.replace("\xa0", " ").replace("\t", " "))
    for k, v in QUOTE_MAP.items(): line = line.replace(k, v)
    for k, v in DASH_MAP.items():  line = line.replace(k, v)
    if mode == "loose":  # collapse internal spaces
        line = re.sub(r"[ ]+", " ", line.strip())
    else:                # keep internal spacing
        line = line.strip()
    return line

def human_bytes(n: int | float | None) -> str:
    if n is None: return ""
    units = ["B","KB","MB","GB","TB"]; i=0; f=float(n)
    while f>=1024 and i<len(units)-1: f/=1024; i+=1
    return f"{f:.2f} {units[i]}"

def free_bytes(path: Path) -> int:
    usage = shutil.disk_usage(path)
    return usage.free

# ---------- streaming counters ----------
def count_tokens_chunked(tokenizer, text_piece: str) -> int:
    if tokenizer is None: return 0
    enc = tokenizer(text_piece, add_special_tokens=False, return_attention_mask=False, return_token_type_ids=False)
    return len(enc["input_ids"])

def process_file(
    src: Path,
    dst_final: Path,
    mode: str,
    tokenizer,
    chunk_chars: int,
) -> tuple[dict, dict, bool]:
    """
    Stream-read src, compute BEFORE stats, normalize, write to dst_final, compute AFTER stats.
    Returns (before_row, after_row, changed)
    """
    dst_tmp = dst_final.with_suffix(dst_final.suffix + ".part")
    dst_tmp.parent.mkdir(parents=True, exist_ok=True)

    before_lines = before_words = before_chars = 0
    after_lines = after_words = after_chars = 0
    before_tokens = after_tokens = 0

    with src.open("r", encoding="utf-8", errors="ignore") as fin:
        raw = fin.read()
    # file-level normalizations: EOL, BOM, NFKC
    raw = raw.replace("\r\n", "\n").replace("\r", "\n")
    if raw.startswith("\ufeff"): raw = raw.lstrip("\ufeff")
    raw = unicodedata.normalize("NFKC", raw)

    # BEFORE counts
    buf_b = []
    for ln in raw.split("\n"):
        before_lines += 1
        before_words += len(ln.split())
        before_chars += len(ln)
        buf_b.append(ln + "\n")
        if tokenizer is not None and sum(len(x) for x in buf_b) >= chunk_chars:
            before_tokens += count_tokens_chunked(tokenizer, "".join(buf_b)); buf_b.clear()
    if buf_b:
        before_tokens += count_tokens_chunked(tokenizer, "".join(buf_b))

    # NORMALIZE
    out_lines = []
    blank_prev = False
    for ln in raw.split("\n"):
        nln = normalize_line(ln, mode=mode)
        if nln == "":
            if not blank_prev:
                out_lines.append(""); blank_prev = True
        else:
            out_lines.append(nln); blank_prev = False
    norm_text = "\n".join(out_lines).strip() + "\n"
    changed_any = (norm_text != (raw if raw.endswith("\n") else raw + "\n"))

    # write normalized
    with dst_tmp.open("w", encoding="utf-8", newline="\n") as fout:
        fout.write(norm_text)
    dst_tmp.replace(dst_final)

    # AFTER counts
    for ln in norm_text.split("\n"):
        after_lines += 1
        after_words += len(ln.split())
        after_chars += len(ln)
    if tokenizer is not None:
        for i in range(0, len(norm_text), chunk_chars):
            after_tokens += count_tokens_chunked(tokenizer, norm_text[i:i+chunk_chars])

    st_src = src.stat()
    st_dst = dst_final.stat()
    before_row = {
        "path": str(src), "folder": src.parent.name or ".", "name": src.name, "ext": src.suffix.lower() or "(noext)",
        "size_bytes": st_src.st_size, "size_h": human_bytes(st_src.st_size),
        "modified": datetime.fromtimestamp(st_src.st_mtime), "created": datetime.fromtimestamp(st_src.st_ctime),
        "lines": before_lines, "words": before_words, "chars": before_chars,
        "tokens_meltemi": int(before_tokens) if tokenizer is not None else None,
    }
    after_row = {
        "path": str(dst_final), "folder": dst_final.parent.name or ".", "name": dst_final.name, "ext": dst_final.suffix.lower() or "(noext)",
        "size_bytes": st_dst.st_size, "size_h": human_bytes(st_dst.st_size),
        "modified": datetime.fromtimestamp(st_dst.st_mtime), "created": datetime.fromtimestamp(st_dst.st_ctime),
        "lines": after_lines, "words": after_words, "chars": after_chars,
        "tokens_meltemi": int(after_tokens) if tokenizer is not None else None,
    }
    return before_row, after_row, changed_any

# ---------- main ----------
def main():
    ap = argparse.ArgumentParser(description="Count stats → normalize → count stats again (with optional tokens)")
    ap.add_argument("--root", required=True, type=Path, help="Root folder with input text files")
    ap.add_argument("--out",  required=False, type=Path, default=None, help="Output folder (mirror). If omitted and write-mode=inplace, edits in place.")
    ap.add_argument("--write-mode", choices=["auto","mirror","inplace"], default="auto",
                    help="auto: try mirror if enough disk, else in-place; mirror: write OUT; inplace: overwrite files")
    ap.add_argument("--ext", action="append", default=[".txt"], help="Text extension to include (repeatable). Default: .txt")
    ap.add_argument("--skip-unchanged", action="store_true", default=True, help="If mirror and file unchanged, keep original (no new file)")
    ap.add_argument("--tokenizer-path", type=str, default=None, help="Local tokenizer folder (tokenizer.json, etc.)")
    ap.add_argument("--hf-model-id",   type=str, default=None, help="HF model id (e.g., ilsp/Meltemi-7B-v1.5)")
    ap.add_argument("--hf-token",      type=str, default=os.getenv("HF_TOKEN", None), help="HF token if repo is private")
    ap.add_argument("--chunks", type=int, default=1_000_000, help="Chars per tokenization chunk")
    ap.add_argument("--max-file-bytes", type=int, default=2_000_000_000)
    ap.add_argument("--max-norm-bytes", type=int, default=1_000_000_000)
    ap.add_argument("--exclude", action="append", default=[".git","__pycache__",".ipynb_checkpoints"],
                    help="Dir names to skip (repeatable)")
    args = ap.parse_args()

    root = args.root
    if not root.exists() or not root.is_dir():
        ap.error(f"Root not found or not a directory: {root}")

    text_exts = set(e.lower() if e.startswith(".") else "."+e.lower() for e in args.ext)
    exclude_names = set(args.exclude)

    # Decide OUT/WRITE mode
    write_mode = args.write_mode
    if write_mode == "inplace":
        out_dir = root
    else:
        out_dir = args.out or Path(str(root) + "_normalized")
        out_dir.mkdir(parents=True, exist_ok=True)

    # Tokenizer
    tokenizer, tokenizer_src = try_load_tokenizer(args.tokenizer_path, args.hf_model_id, args.hf_token)

    # Collect files + estimate size
    files: list[Path] = []
    total_bytes = 0
    for p in root.rglob("*"):
        if p.is_dir():
            if p.name in exclude_names:
                continue
            else:
                continue
        if p.suffix.lower() in text_exts:
            try:
                st = p.stat()
                total_bytes += st.st_size
                files.append(p)
            except Exception:
                continue
    files.sort()

    # Choose mode if auto
    chosen_mode = write_mode
    if write_mode == "auto":
        probe = out_dir if out_dir.exists() else root
        if free_bytes(probe) < total_bytes * 1.05:
            chosen_mode = "inplace"
        else:
            chosen_mode = "mirror"

    print(f"🗂  Files: {len(files)} | Estimated size: {human_bytes(total_bytes)}")
    print(f"✍️  Write mode: {chosen_mode.upper()}")
    print(f"🔤 Tokenizer: {tokenizer_src if tokenizer is not None else '— (not loaded)'}")
    print(f"📁 Root: {root}\n📤 Out:  {out_dir if chosen_mode!='inplace' else '(in-place)'}")

    rows_before, rows_after = [], []
    for src in files:
        try:
            st = src.stat()
            if st.st_size > args.max_file_bytes:
                # record error and skip
                for target in ("before","after"):
                    row = {
                        "path": str(src), "folder": src.parent.name or ".", "name": src.name,
                        "ext": src.suffix.lower() or "(noext)", "size_bytes": None, "size_h": "",
                        "modified": None, "created": None, "lines": None, "words": None,
                        "chars": None, "tokens_meltemi": None, "error": f"too large ({human_bytes(st.st_size)})"
                    }
                    (rows_before if target=="before" else rows_after).append(row)
                continue

            # Decide destination path
            if chosen_mode == "mirror":
                rel = src.relative_to(root)
                dst_final = (out_dir / rel)
            else:
                dst_final = src  # in-place

            mode = normalization_mode_for_suffix(src.suffix)
            try:
                b_row, a_row, changed = process_file(
                    src=src, dst_final=dst_final, mode=mode,
                    tokenizer=tokenizer, chunk_chars=args.chunks
                )
            except OSError as e:
                if e.errno == errno.ENOSPC and chosen_mode == "mirror":
                    print("⚠️  ENOSPC — switching to IN-PLACE for the rest.", file=sys.stderr)
                    chosen_mode = "inplace"
                    b_row, a_row, changed = process_file(
                        src=src, dst_final=src, mode=mode,
                        tokenizer=tokenizer, chunk_chars=args.chunks
                    )
                else:
                    raise

            # If mirror + skip unchanged, remove duplicate and keep original stats
            if (chosen_mode == "mirror") and args.skip_unchanged and not changed:
                try:
                    Path(a_row["path"]).unlink(missing_ok=True)
                except Exception:
                    pass
                a_row = {
                    **a_row,
                    "path": str(src),
                    "size_bytes": b_row["size_bytes"],
                    "size_h": b_row["size_h"],
                    "lines": b_row["lines"],
                    "words": b_row["words"],
                    "chars": b_row["chars"],
                    "tokens_meltemi": b_row["tokens_meltemi"],
                }

            rows_before.append(b_row)
            rows_after.append(a_row)

        except Exception as e:
            # hard error row
            for target in ("before","after"):
                row = {
                    "path": str(src), "folder": src.parent.name or ".", "name": src.name,
                    "ext": src.suffix.lower() or "(noext)", "size_bytes": None, "size_h": "",
                    "modified": None, "created": None, "lines": None, "words": None,
                    "chars": None, "tokens_meltemi": None, "error": f"{type(e).__name__}: {e}"
                }
                (rows_before if target=="before" else rows_after).append(row)

    # --- dataframes ---
    df_before = pd.DataFrame(rows_before).sort_values("path").reset_index(drop=True)
    df_after  = pd.DataFrame(rows_after ).sort_values("path").reset_index(drop=True)

    for col in ["lines","words","chars","tokens_meltemi","error","size_bytes","size_h","modified","created"]:
        if col not in df_before.columns: df_before[col] = pd.NA
        if col not in df_after.columns:  df_after[col]  = pd.NA

    # deltas
    delta_cols = ["size_bytes","lines","words","chars","tokens_meltemi"]
    df_delta = df_after[["path"] + delta_cols].merge(
        df_before[["path"] + delta_cols], on="path", suffixes=("_after","_before"), how="outer"
    )
    for c in delta_cols:
        df_delta[c + "_Δ"] = df_delta[c + "_after"].fillna(0) - df_delta[c + "_before"].fillna(0)

    def totals(df: pd.DataFrame):
        return {
            "files": int(len(df)),
            "bytes": int(df["size_bytes"].fillna(0).sum()),
            "lines": int(df["lines"].fillna(0).sum()),
            "words": int(df["words"].fillna(0).sum()),
            "chars": int(df["chars"].fillna(0).sum()),
            "tokens": int(df["tokens_meltemi"].fillna(0).sum())
        }

    def summarize(df: pd.DataFrame, key: str):
        agg = (df.groupby(key, dropna=False)[["size_bytes","lines","words","chars","tokens_meltemi"]]
               .sum(min_count=1)
               .rename(columns={"size_bytes":"total_bytes","tokens_meltemi":"total_tokens"})
               .sort_values("total_bytes", ascending=False)
               .reset_index())
        agg["total_size"] = agg["total_bytes"].fillna(0).apply(human_bytes)
        return agg

    sum_ext_before    = summarize(df_before, "ext")
    sum_ext_after     = summarize(df_after,  "ext")
    sum_folder_before = summarize(df_before, "folder")
    sum_folder_after  = summarize(df_after,  "folder")

    T_before = totals(df_before)
    T_after  = totals(df_after)
    T_delta  = {k: T_after[k] - T_before[k] for k in T_before}

    # --- save CSVs ---
    save_dir = out_dir if chosen_mode == "mirror" else root
    save_dir.mkdir(parents=True, exist_ok=True)
    df_before.to_csv(save_dir / "per_file_before.csv", index=False)
    df_after .to_csv(save_dir / "per_file_after.csv",  index=False)
    df_delta .to_csv(save_dir / "per_file_delta.csv",  index=False)
    summarize(df_after, "ext").to_csv(save_dir / "summary_by_extension.csv", index=False)
    summarize(df_after, "folder").to_csv(save_dir / "summary_by_folder.csv",  index=False)

    # --- console summary ---
    def fmt(T):
        return (f"Files: {T['files']:,} | Size: {human_bytes(T['bytes'])} | "
                f"Lines: {T['lines']:,} | Words: {T['words']:,} | Chars: {T['chars']:,} | Tokens: {T['tokens']:,}")
    print("\n# === NORMALIZATION REPORT ===")
    print("— BEFORE —", fmt(T_before))
    print("— AFTER  —", fmt(T_after))
    print(f"— Δ      — Size {human_bytes(T_delta['bytes'])}, Lines {T_delta['lines']:,}, "
          f"Words {T_delta['words']:,}, Chars {T_delta['chars']:,}, Tokens {T_delta['tokens']:,}")
    print("\nSaved CSVs in:", save_dir.resolve())

if __name__ == "__main__":
    main()
