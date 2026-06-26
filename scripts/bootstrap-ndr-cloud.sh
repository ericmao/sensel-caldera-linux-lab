#!/usr/bin/env bash
# Seed ndr-cloud agent data (platform.json, capture.env) before compose up.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EDGE_DIR="${SENSEL_OT_EDGE_DIR:-${ROOT}/vendor/sensel-ot-edge-sensor}"
DATA_DIR="${ROOT}/ndr-cloud/data"
AGENT_DIR="${DATA_DIR}/agent"

mkdir -p "${AGENT_DIR}" "${DATA_DIR}/assets" "${DATA_DIR}/pcap"

read_env() {
  local key="$1" default="${2:-}"
  local val=""
  for f in "${ROOT}/ndr/portal.env" "${ROOT}/.env"; do
    if [[ -f "${f}" ]]; then
      val="$(grep -E "^${key}=" "${f}" 2>/dev/null | head -1 | cut -d= -f2- || true)"
      if [[ -n "${val}" ]]; then
        echo "${val}"
        return 0
      fi
    fi
  done
  echo "${default}"
}

SITE_ID="$(read_env SITE_ID edge-site-001)"
SENSOR_ID="$(read_env SENSOR_ID "$(read_env NDR_SENSOR_ID caldera-lab-ndr-01)")"
MQTT_TID="$(read_env MQTT_TENANT_ID "$(read_env POLICY_SYNC_TENANT_ID default)")"
CAP_IF="$(read_env CAPTURE_INTERFACE lo)"

cat > "${AGENT_DIR}/capture.env" <<CAP
CAPTURE_INTERFACE=${CAP_IF}
CAPTURE_BPF_FILTER=
MQTT_TENANT_ID=${MQTT_TID}
SENSOR_ID=${SENSOR_ID}
CAP
chmod 600 "${AGENT_DIR}/capture.env" 2>/dev/null || true

python3 - <<'PY' "${ROOT}" "${AGENT_DIR}"
import json
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
agent_dir = Path(sys.argv[2])


def parse_env(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.is_file():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"([^=]+)=(.*)", line)
        if m:
            out[m.group(1)] = m.group(2)
    return out


merged: dict[str, str] = {}
merged.update(parse_env(root / ".env"))
merged.update(parse_env(root / "ndr" / "portal.env"))

def pick(key: str, default: str = "") -> str:
    return merged.get(key, default)


cfg = {
    "configured": False,
    "sensor_id": pick("SENSOR_ID") or pick("NDR_SENSOR_ID", "caldera-lab-ndr-01"),
    "site_id": pick("SITE_ID", "edge-site-001"),
    "sensor_type": pick("SENSOR_TYPE", "it-ndr-edge"),
    "ndr_profile": pick("NDR_PROFILE", "it_ndr"),
    "sensel_api_url": pick("SENSEL_API_URL", "https://academy.avocadolab.ai"),
    "sensel_api_key": pick("SENSEL_API_KEY", ""),
    "registration_token": pick("OT_REGISTRATION_TOKEN", ""),
    "sensel_verify_tls": pick("SENSEL_VERIFY_TLS", "true").lower() in ("1", "true", "yes"),
    "mqtt_enabled": pick("NORTHBOUND_MQTT_ENABLED", "true").lower() not in ("0", "false", "no"),
    "mqtt_host": pick("CONTROL_PLANE_MQTT_HOST", "mqtt.avocadolab.ai"),
    "mqtt_port": int(pick("CONTROL_PLANE_MQTT_PORT", "1833") or "1833"),
    "mqtt_tenant_id": pick("MQTT_TENANT_ID") or pick("POLICY_SYNC_TENANT_ID", "default"),
    "capture_interface": pick("CAPTURE_INTERFACE", "lo"),
    "capture_bpf_filter": pick("CAPTURE_BPF_FILTER", ""),
}
platform_path = agent_dir / "platform.json"
platform_path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
print(f"==> Wrote {platform_path}")
PY

if [[ -f "${EDGE_DIR}/config/policy/baseline.example.json" ]] \
  && [[ ! -f "${EDGE_DIR}/config/policy/baseline.json" ]]; then
  cp "${EDGE_DIR}/config/policy/baseline.example.json" "${EDGE_DIR}/config/policy/baseline.json"
  echo "==> Seeded ${EDGE_DIR}/config/policy/baseline.json"
fi

echo "==> NDR cloud bootstrap complete (sensor_id=${SENSOR_ID})"
