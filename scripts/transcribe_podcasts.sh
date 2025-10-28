#!/usr/bin/env bash
IN="./data/podcasts"
OUT="./data/transcriptions"
LOG="./data/logs/run_$(date +%F_%H-%M-%S).log"
DEVICE=$(command -v nvidia-smi >/dev/null 2>&1 && echo cuda || echo cpu)
mkdir -p "$OUT" "$(dirname "$LOG")"

find "$IN" -type f \( -iname '*.mp3' -o -iname '*.m4a' -o -iname '*.wav' -o -iname '*.flac' -o -iname '*.ogg' -o -iname '*.webm' -o -iname '*.wma' -o -iname '*.aac' \) -print0 \
| sort -z | while IFS= read -r -d '' f; do
  stem="$(basename "${f%.*}")"
  if [ -s "$OUT/$stem.srt" ] || [ -s "$OUT/$stem.json" ]; then
    echo "⏩ Skip: $f" | tee -a "$LOG"; continue; fi
  echo "▶️  Transcribe: $f" | tee -a "$LOG"
  conda run -n whisper whisper "$f" \
    --model large-v3 \
    --device "$DEVICE" \
    --output_dir "$OUT" \
    --output_format all \
    --task transcribe \
    --language el \
    --temperature 0 \
    --beam_size 5 \
    --best_of 5 \
    --condition_on_previous_text True \
    --word_timestamps True \
    --highlight_words True \
    --threads 0 \
    --verbose True 2>&1 | tee -a "$LOG"
done

