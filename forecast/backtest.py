# Rolling-origin backtest: from each origin fall, forecast 1 to 4 falls ahead using only data
# through the origin, and compare with the naive forecast (the last value) and drift (the last
# value plus the average yearly change since the series began). Writes reports/backtest.md.

import logging
import sys

import pandas as pd

from forecast import online_grad, undergrad
from ingest.paths import ROOT

log = logging.getLogger("backtest")

UNDERGRAD_ORIGINS = range(2016, 2026)
ONLINE_ORIGINS = range(2021, 2026)
HORIZONS = range(1, 5)
OUT = ROOT / "reports" / "backtest.md"


def baselines(known, column, horizon):
    first, last = known.iloc[0], known.iloc[-1]
    slope = (last[column] - first[column]) / (last.fall_year - first.fall_year)
    return {"naive": float(last[column]), "drift": float(last[column] + slope * horizon)}


def undergrad_forecasts(known, future, horizon):
    # known holds falls through the origin; future holds the actual intake for later falls and is
    # read only by the diagnostic row, which is told the intake the model would have to guess.
    c = undergrad.base_share(undergrad.continuing_shares(known))
    h0 = known.h.iloc[-1]
    forecasts = baselines(known, "h", horizon)
    for rule in ("mean3", "latest"):
        f, t = undergrad.intake(known, rule)
        forecasts[f"stock-flow, intake {rule}"] = undergrad.project(h0, f, t, c, horizon)[-1]
    h = float(h0)
    for row in future.head(horizon).itertuples():
        h = row.f + row.t + c * h
    forecasts["diagnostic: stock-flow given actual intake"] = h
    return forecasts


def undergrad_backtest(history):
    rows = []
    last_fall = history.fall_year.max()
    for origin in UNDERGRAD_ORIGINS:
        known = history[history.fall_year <= origin]
        future = history[history.fall_year > origin]
        for horizon in HORIZONS:
            target = origin + horizon
            if target > last_fall:
                break
            actual = history.loc[history.fall_year == target, "h"].item()
            for model, value in undergrad_forecasts(known, future, horizon).items():
                rows.append((model, origin, horizon, target, actual, value))
    return frame(rows)


def online_backtest(history):
    rows = []
    last_fall = history.fall_year.max()
    for origin in ONLINE_ORIGINS:
        known = history[history.fall_year <= origin]
        steps = min(max(HORIZONS), last_fall - origin)
        ets, _ = online_grad.forecast(known, steps, damped_trend=True)
        level_only, _ = online_grad.forecast(known, steps, damped_trend=False)
        for horizon in range(1, steps + 1):
            target = origin + horizon
            actual = history.loc[history.fall_year == target, "headcount"].item()
            forecasts = baselines(known, "headcount", horizon)
            forecasts["damped-trend ETS"] = ets.value.iloc[horizon - 1]
            forecasts["ETS without trend"] = level_only.value.iloc[horizon - 1]
            for model, value in forecasts.items():
                rows.append((model, origin, horizon, target, actual, value))
    return frame(rows)


def frame(rows):
    columns = ["model", "origin", "horizon", "target", "actual", "forecast"]
    data = pd.DataFrame(rows, columns=columns)
    data["pct_error"] = (data.forecast - data.actual) / data.actual
    return data


def summary(forecasts):
    grouped = forecasts.groupby(["model", "horizon"])
    table = grouped.agg(
        n=("pct_error", "size"),
        mape=("pct_error", lambda e: e.abs().mean()),
        mean_error=("pct_error", "mean"),
    ).reset_index()
    return table


def markdown(table, models):
    horizons = sorted(table.horizon.unique())
    header = "| Model | " + " | ".join(f"{h} year{'s' if h > 1 else ''} ahead" for h in horizons)
    lines = [header + " |", "|---|" + "---:|" * len(horizons)]
    for model in models:
        cells = []
        for h in horizons:
            row = table[(table.model == model) & (table.horizon == h)].iloc[0]
            cells.append(f"{100 * row.mape:.1f}% ({100 * row.mean_error:+.1f}%, n={row.n})")
        lines.append(f"| {model} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def detail(forecasts, models):
    wide = forecasts.pivot_table(
        index=["origin", "target", "actual"], columns="model", values="forecast"
    ).reset_index()
    lines = ["| Origin | Target | Actual | " + " | ".join(models) + " |"]
    lines.append("|---:|---:|---:|" + "---:|" * len(models))
    for row in wide.itertuples(index=False):
        values = dict(zip(wide.columns, row, strict=True))
        cells = [f"{values[m]:,.0f}" for m in models]
        lines.append(
            f"| Fall {values['origin']} | Fall {values['target']} | {values['actual']:,} | "
            + " | ".join(cells)
            + " |"
        )
    return "\n".join(lines)


UNDERGRAD_MODELS = [
    "stock-flow, intake mean3",
    "stock-flow, intake latest",
    "naive",
    "drift",
    "diagnostic: stock-flow given actual intake",
]
ONLINE_MODELS = ["damped-trend ETS", "ETS without trend", "naive", "drift"]


def report(undergrad_table, undergrad_detail, online_table, online_detail):
    return "\n".join(
        [
            "# Backtest",
            "",
            "Generated by `make forecast`. Each cell is the mean absolute percentage error, then "
            "the mean signed error (positive means the forecast ran high), then the number of "
            "forecasts. intake mean3 holds freshmen and transfers at their mean over the three "
            "falls through the origin; intake latest holds them at the origin's values.",
            "",
            "## Gies undergraduate headcount, origins Fall 2016 to Fall 2025",
            "",
            markdown(undergrad_table, UNDERGRAD_MODELS),
            "",
            "## Online graduate headcount, origins Fall 2021 to Fall 2025",
            "",
            markdown(online_table, ONLINE_MODELS),
            "",
            "## Every undergraduate forecast",
            "",
            undergrad_detail,
            "",
            "## Every online graduate forecast",
            "",
            online_detail,
            "",
        ]
    )


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    ug = undergrad_backtest(undergrad.history())
    ol = online_backtest(online_grad.history())
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(
        report(
            summary(ug),
            detail(ug, UNDERGRAD_MODELS),
            summary(ol),
            detail(ol, ONLINE_MODELS),
        )
    )
    log.info("undergraduate: %d forecasts; online: %d forecasts", len(ug), len(ol))
    log.info("wrote %s", OUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
