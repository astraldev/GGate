#!/usr/bin/env bash
#
# Turn a screen recording into the demo clip used in the README / gallery:
# trimmed, scaled to 1080p, 30fps, h264 (web-friendly, no audio).
#
# Usage:
#   build-aux/make_demo.sh INPUT [START] [DURATION] [OUTPUT]
#
# Defaults: START=25.7s, DURATION=30s, OUTPUT=gallery/ggate-demo.mp4
#
set -euo pipefail

SRC="${1:?usage: make_demo.sh INPUT [START] [DURATION] [OUTPUT]}"
START="${2:-25.7}"
DURATION="${3:-30}"
OUT="${4:-gallery/ggate-demo.mp4}"

ffmpeg -hide_banner -loglevel error \
  -ss "$START" -t "$DURATION" -i "$SRC" \
  -vf "fps=30,scale=-2:1080:flags=lanczos" \
  -c:v libx264 -crf 23 -preset slow -pix_fmt yuv420p \
  -movflags +faststart -an -y "$OUT"

echo "wrote $OUT"
