.PHONY: up down up-ndr down-ndr status status-ndr test wazuh-test validate clean config hexstrike-check hexstrike-mcp ndr-config

COMPOSE ?= docker compose
COMPOSE_NDR ?= docker compose -f compose.yml -f compose.ndr.yml

up:
	$(COMPOSE) up -d --build

up-ndr:
	$(COMPOSE_NDR) up -d --build

down:
	$(COMPOSE) down

down-ndr:
	$(COMPOSE_NDR) down

status:
	$(COMPOSE) ps
	@python3 scripts/trainingctl.py status || true

status-ndr:
	$(COMPOSE_NDR) ps
	@ENABLE_NDR=true python3 scripts/trainingctl.py status --ndr || true

test:
	python3 -m pytest -q

wazuh-test:
	bash scripts/test-wazuh-rules.sh

validate:
	python3 scripts/trainingctl.py validate
	$(COMPOSE) config

ndr-config:
	$(COMPOSE_NDR) config

clean:
	python3 scripts/trainingctl.py cleanup || true
	$(COMPOSE) down -v
	$(COMPOSE_NDR) down -v 2>/dev/null || true

config:
	$(COMPOSE) config

hexstrike-check:
	bash scripts/hexstrike-check.sh

hexstrike-mcp:
	bash scripts/setup-hexstrike-mcp.sh
