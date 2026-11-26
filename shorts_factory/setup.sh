#!/usr/bin/env bash
# One-time setup: Python deps + Kokoro TTS model files (~120 MB, from GitHub releases).
set -euo pipefail
pip install -r "$(dirname "$0")/requirements.txt"
DIR="${KOKORO_DIR:-/home/user/models}"
mkdir -p "$DIR"
BASE=https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0
[ -f "$DIR/kokoro-v1.0.int8.onnx" ] || curl -L -o "$DIR/kokoro-v1.0.int8.onnx" "$BASE/kokoro-v1.0.int8.onnx"
[ -f "$DIR/voices-v1.0.bin" ] || curl -L -o "$DIR/voices-v1.0.bin" "$BASE/voices-v1.0.bin"
command -v ffmpeg >/dev/null || { echo "ffmpeg (with libass) is required"; exit 1; }
echo "Ready. Try: python make_short.py scripts/illusions_01.json"
