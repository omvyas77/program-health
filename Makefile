.DEFAULT_GOAL := help
.PHONY: help snapshot ingest build docs findings forecast export app publish report

PYTHON := .venv/bin/python
DBT := .venv/bin/dbt

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

build: ## run every dbt model and test into warehouse/gph.duckdb
	mkdir -p warehouse
	$(DBT) build --project-dir transform --profiles-dir transform

docs: ## generate the dbt docs site
	$(DBT) docs generate --project-dir transform --profiles-dir transform

findings: ## write docs/findings.md from the dbt analyses
	$(DBT) compile --project-dir transform --profiles-dir transform --select "resource_type:analysis"
	$(PYTHON) -m publish.findings

forecast: ## backtest, then write data/marts/mart_projection
	$(PYTHON) -m forecast.backtest
	$(PYTHON) -m forecast.projection

export: ## write the dbt marts to data/marts
	$(PYTHON) -m publish.export

app: ## run the Streamlit app locally
	$(PYTHON) -m streamlit run app/streamlit_app.py

publish: ## write data/marts to the Google Sheet (needs SHEET_ID)
	$(PYTHON) -m publish.sheets

report: ## write the registration watch report
	$(PYTHON) -m publish.registration_report
