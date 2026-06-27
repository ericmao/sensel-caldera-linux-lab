#!/usr/bin/env bash
# Export TRAINING-GUIDE-2.1.md to PDF (requires pandoc + xelatex for CJK).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="${ROOT}/training/TRAINING-GUIDE-2.1.md"
OUT_DIR="${ROOT}/training/pdf"
OUT="${OUT_DIR}/SenseL_Caldera_Linux_Lab_教學指南_v2.1.pdf"

if ! command -v pandoc >/dev/null 2>&1; then
  echo "ERROR: pandoc not found. Install: brew install pandoc  OR  apt install pandoc texlive-xetex" >&2
  echo "See training/pdf/README.md for alternatives." >&2
  exit 1
fi

mkdir -p "${OUT_DIR}"

# CJK: xelatex + Noto or system fonts; fallback to pdflatex if xelatex missing.
if command -v xelatex >/dev/null 2>&1; then
  pandoc "${SRC}" \
    -o "${OUT}" \
    --pdf-engine=xelatex \
    -V CJKmainfont="PingFang TC" \
    -V geometry:margin=2.5cm \
    -V documentclass=article \
    --toc \
    --metadata title="SenseL Caldera Linux Lab 教學指南 2.1"
else
  echo "WARN: xelatex not found; PDF may not render CJK correctly." >&2
  pandoc "${SRC}" -o "${OUT}" --toc \
    --metadata title="SenseL Caldera Linux Lab Training Guide 2.1"
fi

echo "==> Wrote ${OUT}"
