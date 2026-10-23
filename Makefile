.DEFAULT_GOAL := help
.PHONY: help snapshot

PYTHON := .venv/bin/python

help: ## list the targets
	@grep -E '^[a-z]+:.*## ' $(MAKEFILE_LIST) | awk -F ':.*## ' '{printf "  %-10s %s\n", $$1, $$2}'

snapshot: ## Spring 2027 registration snapshot
	$(PYTHON) -m ingest.cis_snapshot
