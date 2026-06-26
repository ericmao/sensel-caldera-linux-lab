.PHONY: up down up-ndr down-ndr up-ndr-cloud down-ndr-cloud status status-ndr status-ndr-cloud test wazuh-test validate clean config hexstrike-check hexstrike-mcp ndr-config ndr-cloud-config

COMPOSE ?= docker compose
COMPOSE_NDR ?= docker compose -f compose.yml -f compose.ndr.yml
COMPOSE_NDR_CLOUD ?= docker compose -f compose.yml -f compose.ndr.yml -f compose.ndr.cloud.yml

up:
	$(COMPOSE) up -d --build

up-ndr:
	$(COMPOSE_NDR) up -d --build

up-ndr-cloud:
	bash scripts/ensure-edge-sensor.sh
	bash scripts/bootstrap-ndr-cloud.sh
	$(COMPOSE_NDR_CLOUD) up -d --build
	@echo ""
	@echo "Caldera UI:     http://127.0.0.1:8888"
	@echo "Edge Console:   http://127.0.0.1:8090  (Setup wizard — paste Portal invite code)"

down:
	$(COMPOSE) down

down-ndr:
	$(COMPOSE_NDR) down

down-ndr-cloud:
	$(COMPOSE_NDR_CLOUD) down

status:
	$(COMPOSE) ps
	@python3 scripts/trainingctl.py status || true

status-ndr:
	$(COMPOSE_NDR) ps
	@ENABLE_NDR=true python3 scripts/trainingctl.py status --ndr || true

status-ndr-cloud:
	$(COMPOSE_NDR_CLOUD) ps
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

ndr-cloud-config:
	bash scripts/ensure-edge-sensor.sh
	bash scripts/bootstrap-ndr-cloud.sh
	$(COMPOSE_NDR_CLOUD) config

clean:
	python3 scripts/trainingctl.py cleanup || true
	$(COMPOSE) down -v
	$(COMPOSE_NDR) down -v 2>/dev/null || true
	$(COMPOSE_NDR_CLOUD) down -v 2>/dev/null || true

config:
	$(COMPOSE) config

hexstrike-check:
	bash scripts/hexstrike-check.sh

hexstrike-mcp:
	bash scripts/setup-hexstrike-mcp.sh
