#!/usr/bin/env bash
# Run on Kali VM (Phase 3). Installs HexStrike server and prints start command.
set -euo pipefail

HEXSTRIKE_REPO="${HEXSTRIKE_REPO:-$HOME/hexstrike-ai}"
HEXSTRIKE_PORT="${HEXSTRIKE_PORT:-8888}"
HEXSTRIKE_BIND="${HEXSTRIKE_BIND:-0.0.0.0}"

echo "[phase3] HexStrike server setup on Kali"
echo "[phase3] repo=${HEXSTRIKE_REPO} port=${HEXSTRIKE_PORT} bind=${HEXSTRIKE_BIND}"

if ! command -v git >/dev/null 2>&1; then
  sudo apt-get update -qq
  sudo apt-get install -y git python3-venv python3-pip
fi

if [[ ! -d "${HEXSTRIKE_REPO}/.git" ]]; then
  git clone https://github.com/0x4m4/hexstrike-ai.git "${HEXSTRIKE_REPO}"
fi

cd "${HEXSTRIKE_REPO}"
python3 -m venv hexstrike-env
# shellcheck disable=SC1091
source hexstrike-env/bin/activate
pip3 install -q -r requirements.txt

echo ""
echo "[phase3] Start server (keep running in tmux/screen):"
echo "  cd ${HEXSTRIKE_REPO} && source hexstrike-env/bin/activate"
echo "  python3 hexstrike_server.py --host ${HEXSTRIKE_BIND} --port ${HEXSTRIKE_PORT}"
echo ""
echo "[phase3] From Mac, verify:"
echo "  curl http://<kali-ip>:${HEXSTRIKE_PORT}/health"
