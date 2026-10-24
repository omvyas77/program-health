.DEFAULT_GOAL := help
.PHONY: help snapshot ingest

PYTHON := .venv/bin/python

help: ## list the targets
	@grep -E '^[a-z]+:.*## ' $(MAKEFILE_LIST) | awk -F ':.*## ' '{printf "  %-10s %s\n", $$1, $$2}'

snapshot: ## Spring 2027 registration snapshot
	$(PYTHON) -m ingest.cis_snapshot

ingest: ## download every source and rebuild data/extracts
	$(PYTHON) -m ingest.ipeds dictionaries
	$(PYTHON) -m ingest.ipeds data
	$(PYTHON) -m ingest.gpa
	$(PYTHON) -m ingest.catalog
	$(PYTHON) -m ingest.tre
	$(PYTHON) -m ingest.wiche
	$(PYTHON) -m ingest.dmi
	$(PYTHON) -m ingest.dair
