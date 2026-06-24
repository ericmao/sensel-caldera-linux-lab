#!/bin/bash
set -euo pipefail

CONF_DIR="/usr/src/app/conf"
TEMPLATE="${CONF_DIR}/local.yml.template"
LOCAL="${CONF_DIR}/local.yml"
SENSEL_BAKED="/opt/sensel-plugin-baked"
SENSEL_DST="/usr/src/app/plugins/sensel"

if [ ! -f "${SENSEL_DST}/hook.py" ]; then
  mkdir -p "${SENSEL_DST}"
  cp -a "${SENSEL_BAKED}/." "${SENSEL_DST}/"
else
  mkdir -p "${SENSEL_DST}/data/abilities/sensel-linux"
  cp -a "${SENSEL_BAKED}/data/abilities/sensel-linux/." "${SENSEL_DST}/data/abilities/sensel-linux/"
fi

if [ ! -f "${LOCAL}" ]; then
  cp "${TEMPLATE}" "${LOCAL}"
fi

if ! grep -q "sensel" "${LOCAL}"; then
  python3 - <<'PY'
from pathlib import Path
import yaml

path = Path("/usr/src/app/conf/local.yml")
data = yaml.safe_load(path.read_text()) or {}
plugins = data.get("plugins") or []
if "sensel" not in plugins:
    plugins.append("sensel")
    data["plugins"] = plugins
path.write_text(yaml.dump(data, default_flow_style=False, sort_keys=False))
PY
fi

exec python3 server.py -E local "$@"
