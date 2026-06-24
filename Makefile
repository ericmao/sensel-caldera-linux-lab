.PHONY: up down status test wazuh-test validate clean config hexstrike-check hexstrike-mcp

COMPOSE ?= docker compose

up:
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

status:
	$(COMPOSE) ps
	@python3 scripts/trainingctl.py status || true

test:
	python3 -m pytest -q

wazuh-test:
	bash scripts/test-wazuh-rules.sh

validate:
	python3 scripts/trainingctl.py validate
	$(COMPOSE) config

clean:
	python3 scripts/trainingctl.py cleanup || true
	$(COMPOSE) down -v

config:
	$(COMPOSE) config

hexstrike-check:
	bash scripts/hexstrike-check.sh

hexstrike-mcp:
	bash scripts/setup-hexstrike-mcp.sh
