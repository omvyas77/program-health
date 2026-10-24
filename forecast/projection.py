# Writes data/marts/mart_projection: history and projections for three series, one row per
# series, fall, and scenario. low and high hold the 80% interval where the model gives one.
#   gies_undergraduate_headcount: stock and flow, base, low, and high scenarios
#   gies_online_graduate_headcount: exponential smoothing without trend, with an 80% interval
#   uiuc_in_state_admit_rate_what_if: the WICHE what-if, once Illinois's CDS rows are verified

import logging
import sys

import pandas as pd

from forecast import online_grad, undergrad, what_if
from ingest.paths import MARTS, ROOT

log = logging.getLogger("projection")

YEARS = 4
COLUMNS = ["series", "fall_term", "fall_year", "scenario", "value", "low", "high"]


def undergrad_rows(history):
    rows = [("actual", r.fall_year, r.h) for r in history.itertuples()]
    last = history.iloc[-1]
    for scenario, (f, t, c) in undergrad.scenario_inputs(history, undergrad.INTAKE_RULE).items():
        log.info("undergraduate %s: F %.1f, T %.1f, c %.4f", scenario, f, t, c)
        values = undergrad.project(last.h, f, t, c, YEARS)
        rows += [(scenario, last.fall_year + i, v) for i, v in enumerate(values, start=1)]
    data = pd.DataFrame(rows, columns=["scenario", "fall_year", "value"])
    return data.assign(series="gies_undergraduate_headcount")


def online_rows(history):
    projected, params = online_grad.forecast(history, YEARS)
    log.info("online graduate: alpha %.4f", params["alpha"])
    actual = history.rename(columns={"headcount": "value"}).assign(scenario="actual")
    return pd.concat([actual, projected.assign(scenario="base")], ignore_index=True).assign(
        series="gies_online_graduate_headcount"
    )


def what_if_rows():
    return what_if.admit_rates(*what_if.inputs()).assign(series="uiuc_in_state_admit_rate_what_if")


def build():
    parts = [
        undergrad_rows(undergrad.history()),
        online_rows(online_grad.history()),
        what_if_rows(),
    ]
    data = pd.concat([p for p in parts if not p.empty], ignore_index=True)
    for column in ("low", "high"):
        if column not in data:
            data[column] = float("nan")
    data["fall_year"] = data.fall_year.astype("int32")
    data["fall_term"] = "Fall " + data.fall_year.astype(str)
    data[["value", "low", "high"]] = data[["value", "low", "high"]].astype("float64")
    data = data[COLUMNS].sort_values(["series", "scenario", "fall_year"], ignore_index=True)
    keys = ["series", "fall_year", "scenario"]
    assert not data.duplicated(keys).any(), "duplicate series, fall, and scenario rows"
    return data


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    data = build()
    MARTS.mkdir(parents=True, exist_ok=True)
    data.to_parquet(MARTS / "mart_projection.parquet", index=False)
    data.to_csv(MARTS / "mart_projection.csv", index=False)
    for series, rows in data.groupby("series"):
        log.info("%s: %d rows", series, len(rows))
    log.info("wrote %s", (MARTS / "mart_projection.parquet").relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
