# Appends this refresh to data/marts/mart_refresh_log: one row per mart, with what the change
# check found, how dbt's tests went, and whether the Sheet was published. Source versions live in
# data/extracts/manifest.csv, which the same run commits.

import argparse
import json
import logging
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from ingest.paths import MARTS, TRANSFORM

log = logging.getLogger("refresh_log")

LOG = "mart_refresh_log"
RUN_RESULTS = TRANSFORM / "target" / "run_results.json"
COLUMNS = {
    "run_utc": "str",
    "trigger": "str",
    "git_sha": "str",
    "mart": "str",
    "rows": "int64",
    "sources_changed": "str",
    "new_ipeds_files": "str",
    "new_catalog_terms": "str",
    "dbt_pass": "Int64",
    "dbt_warn": "Int64",
    "dbt_error": "Int64",
    "published": "bool",
}


def read_changes(path):
    # A missing summary means the change check itself failed.
    if not path.exists():
        return {
            "sources_changed": "change check failed",
            "new_ipeds_files": "",
            "new_catalog_terms": "",
        }
    summary = json.loads(path.read_text())
    changed = "; ".join(
        f"{source}: {len(files)} file{'s' if len(files) != 1 else ''}"
        for source, files in summary["changed"].items()
    )
    return {
        "sources_changed": changed or "none",
        "new_ipeds_files": ", ".join(summary["new_ipeds_files"]),
        "new_catalog_terms": ", ".join(summary["new_catalog_terms"]),
    }


def dbt_counts(started):
    # run_results.json from before this run started belongs to some other invocation.
    if not RUN_RESULTS.exists() or RUN_RESULTS.stat().st_mtime < started:
        return {"dbt_pass": pd.NA, "dbt_warn": pd.NA, "dbt_error": pd.NA}
    statuses = [r["status"] for r in json.loads(RUN_RESULTS.read_text())["results"]]
    return {
        "dbt_pass": sum(s in ("pass", "success") for s in statuses),
        "dbt_warn": statuses.count("warn"),
        "dbt_error": sum(s in ("error", "fail") for s in statuses),
    }


def git_sha():
    sha = os.environ.get("GITHUB_SHA")
    if sha:
        return sha
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()


def build_rows(changes, counts, trigger, published):
    run = {"run_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"), "trigger": trigger}
    run |= {"git_sha": git_sha()} | changes | counts | {"published": published}
    marts = sorted(p for p in MARTS.glob("mart_*.parquet") if p.stem != LOG)
    rows = [run | {"mart": p.stem, "rows": len(pd.read_parquet(p))} for p in marts]
    return pd.DataFrame(rows)[list(COLUMNS)].astype(COLUMNS)


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser()
    parser.add_argument("--changes", type=Path, required=True)
    parser.add_argument("--trigger", required=True)
    parser.add_argument("--published", choices=["true", "false"], required=True)
    parser.add_argument("--started", type=float, default=0, help="run start, as a Unix time")
    args = parser.parse_args()
    new = build_rows(
        read_changes(args.changes), dbt_counts(args.started), args.trigger, args.published == "true"
    )
    path = MARTS / f"{LOG}.parquet"
    log_frame = pd.concat([pd.read_parquet(path), new], ignore_index=True) if path.exists() else new
    log_frame = log_frame.astype(COLUMNS)
    log_frame.to_parquet(path, index=False)
    log_frame.to_csv(MARTS / f"{LOG}.csv", index=False)
    log.info("logged %d marts for this run; the log has %d rows", len(new), len(log_frame))
    return 0


if __name__ == "__main__":
    sys.exit(main())
