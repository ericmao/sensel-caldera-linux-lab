#!/bin/bash
cat <<'EOF'
Caldera Sandcat deploy command (manual fallback)
==================================================

1. Open Caldera UI: http://127.0.0.1:8888
2. Login (default red/admin unless changed)
3. Navigate: Agents -> Deploy Agent -> Sandcat -> Linux
4. Ensure app.contact.http shows http://caldera:8888 for in-lab agents
5. Copy the Linux deploy command

Paste into .env as SANDCAT_DEPLOY_COMMAND, for example:

SANDCAT_DEPLOY_COMMAND=server="http://caldera:8888"; curl -sk -X POST -H "file:sandcat.go" -H "platform:linux" -H "server:http://caldera:8888" -H "group:castle-train-01" $server/file/download > /opt/sensel/sandcat; chmod +x /opt/sensel/sandcat; runuser -u sensel-svc -- /opt/sensel/sandcat -server $server -group castle-train-01 -v

Then restart target-linux or run:
  docker compose exec target-linux /opt/sensel/scripts/bootstrap-sandcat.sh

Reference: Caldera v5.3.0 Sandcat /file/download headers (file, platform, server, group)
EOF
