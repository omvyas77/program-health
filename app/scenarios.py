# Enrollment scenarios: the base projection from data/marts next to the user's own inputs.

import charts
import marts
import model
import pandas as pd
import streamlit as st

projection = marts.read("mart_projection")
base = marts.read("mart_projection_assumptions").set_index("scenario").loc["base"]
undergrad = projection[projection.series == "gies_undergraduate_headcount"]
online = projection[projection.series == "gies_online_graduate_headcount"]


def rows(series, scenario):
    return series[series.scenario == scenario].set_index("fall_year").value


def chart_frames(series, yours, changed, band_scenarios):
    actual = rows(series, "actual")
    last_fall, last_value = actual.index.max(), actual.iloc[-1]
    base_values = rows(series, "base")
    start = pd.Series({last_fall: last_value})
    long = pd.concat(
        [
            pd.DataFrame({"fall_year": actual.index, "value": actual.values, "line": "Actual"}),
            pd.DataFrame(
                {
                    "fall_year": [last_fall, *base_values.index],
                    "value": pd.concat([start, base_values]).values,
                    "line": "Base",
                }
            ),
        ],
        ignore_index=True,
    )
    if changed:
        mine = pd.DataFrame(
            {
                "fall_year": [last_fall, *base_values.index],
                "value": [last_value, *yours],
                "line": "Your scenario",
            }
        )
        long = pd.concat([long, mine], ignore_index=True)
    if band_scenarios:
        low, high = rows(series, "low"), rows(series, "high")
    else:
        projected = series[series.scenario == "base"].set_index("fall_year")
        low, high = projected.low, projected.high
    band = pd.DataFrame(
        {
            "fall_year": [last_fall, *low.index],
            "low": [last_value, *low.values],
            "high": [last_value, *high.values],
        }
    )
    return long, band


def table(series, yours, band_scenarios):
    frame = pd.DataFrame({"Actual": rows(series, "actual"), "Base": rows(series, "base")})
    if band_scenarios:
        frame["Low"], frame["High"] = rows(series, "low"), rows(series, "high")
    else:
        projected = series[series.scenario == "base"].set_index("fall_year")
        frame["80% low"], frame["80% high"] = projected.low, projected.high
    frame["Your scenario"] = pd.Series(yours, index=rows(series, "base").index)
    frame = frame.round().astype("Int64")
    frame.index = "Fall " + frame.index.astype(str)
    return frame.rename_axis("Fall")


def shown(frame):
    # Commas and blanks for display; the CSV download keeps the numbers.
    return frame.astype(object).map(lambda v: "" if pd.isna(v) else f"{v:,}")


st.title("Enrollment scenarios")
st.write(
    "How many undergraduates and online graduate students could Gies have by Fall 2030? The "
    "inputs start at the base scenario; change one to see your own next to it."
)
st.caption(
    "Undergraduates are projected as a stock and flow: next fall's are the first-time freshmen "
    "and new transfers who arrive plus the share of this fall's who continue. Online graduate "
    "headcount is projected with exponential smoothing."
)

left, middle, right, last = st.columns(4)
freshmen = left.number_input(
    "First-time freshmen per year",
    min_value=0.0,
    value=round(float(base.first_time_freshmen), 1),
    step=10.0,
    format="%.0f",
)
transfers = middle.number_input(
    "New transfers per year",
    min_value=0.0,
    value=round(float(base.new_transfers), 1),
    step=1.0,
    format="%.0f",
)
continuing = right.number_input(
    "Continuing share (%)",
    min_value=0.0,
    max_value=100.0,
    value=round(100 * float(base.continuing_share), 1),
    step=0.1,
    format="%.1f",
)
growth = last.number_input(
    "Online graduate growth (% per year)",
    min_value=-50.0,
    max_value=50.0,
    value=0.0,
    step=0.5,
    format="%.1f",
)

defaults = {
    "first-time freshmen": (round(float(base.first_time_freshmen), 1), freshmen, "{:,.0f}"),
    "new transfers": (round(float(base.new_transfers), 1), transfers, "{:,.0f}"),
    "continuing share": (round(100 * float(base.continuing_share), 1), continuing, "{:.1f}%"),
}
undergrad_changes = [
    f"{name} {fmt.format(old)} to {fmt.format(new)}"
    for name, (old, new, fmt) in defaults.items()
    if new != old
]
online_changes = [f"online growth 0.0% to {growth:.1f}% a year"] if growth != 0 else []

undergrad_base = rows(undergrad, "base")
undergrad_actual = rows(undergrad, "actual")
years = len(undergrad_base)
if undergrad_changes:
    undergrad_yours = model.project(
        undergrad_actual.iloc[-1], freshmen, transfers, continuing / 100, years
    )
else:
    undergrad_yours = list(undergrad_base.values)

online_base = rows(online, "base")
online_actual = rows(online, "actual")
if online_changes:
    online_yours = model.grow(online_actual.iloc[-1], growth / 100, len(online_base))
else:
    online_yours = list(online_base.values)

last_fall = undergrad_base.index.max()
direction = "up" if undergrad_base.iloc[-1] > undergrad_actual.iloc[-1] else "down"
charts.heading(
    f"Base scenario: {undergrad_base.iloc[-1]:,.0f} undergraduates in Fall {last_fall}",
    f"{direction.capitalize()} from {undergrad_actual.iloc[-1]:,.0f} in Fall "
    f"{undergrad_actual.index.max()}",
)
# The chart title already gives the base, so the comparison line appears once an input changes.
if undergrad_changes:
    st.markdown(
        model.change_line(
            "undergraduates",
            last_fall,
            undergrad_yours[-1],
            undergrad_base.iloc[-1],
            undergrad_changes,
        )
    )
long, band = chart_frames(undergrad, undergrad_yours, bool(undergrad_changes), band_scenarios=True)
st.altair_chart(
    charts.scenario_chart(long, band, "Undergraduates", "Low to high scenarios"), width="stretch"
)
st.caption(
    "Shaded: the low and high scenarios, with the continuing share at its 10th and 90th "
    "percentiles since 2013 and freshmen 5% below or above base. In a backtest from 2016 on, "
    "this model matched the naive forecast (next fall equals this fall) rather than beating it. "
    f"[How the projection works]({marts.METHOD})."
)

projected = online[online.scenario == "base"].set_index("fall_year")
charts.heading(
    f"Base: online graduate headcount holds at {online_base.iloc[-1]:,.0f}",
    f"80% range by Fall {online_base.index.max()}: {projected.low.iloc[-1]:,.0f} to "
    f"{projected.high.iloc[-1]:,.0f}",
)
if online_changes:
    st.markdown(
        model.change_line(
            "online graduate students",
            online_base.index.max(),
            online_yours[-1],
            online_base.iloc[-1],
            online_changes,
        )
    )
long, band = chart_frames(online, online_yours, bool(online_changes), band_scenarios=False)
st.altair_chart(
    charts.scenario_chart(long, band, "Graduate students in online programs", "80% interval"),
    width="stretch",
)
st.caption(
    "Shaded: the 80% prediction interval. The base model has no trend, because a damped-trend "
    "model carried the 2017 to 2021 launch ramp forward and lost to the naive forecast in the "
    "backtest."
)

undergrad_table = table(undergrad, undergrad_yours, band_scenarios=True)
online_table = table(online, online_yours, band_scenarios=False)
with st.expander("Show the numbers"):
    st.markdown("**Undergraduate headcount**")
    st.table(shown(undergrad_table))
    st.markdown("**Online graduate headcount**")
    st.table(shown(online_table))
download = pd.concat(
    [
        undergrad_table.reset_index().assign(Series="Gies undergraduate headcount"),
        online_table.reset_index().assign(Series="Gies online graduate headcount"),
    ],
    ignore_index=True,
)
st.download_button(
    "Download both tables (CSV)",
    download.to_csv(index=False).encode(),
    file_name="gies_enrollment_scenarios.csv",
    mime="text/csv",
)
