# Line charts for actuals, the base, and the user's scenario, with a shaded range. Colors are the
# first two slots of a validated categorical palette; the base is dashed so it doesn't rely on
# color alone.

import altair as alt
import streamlit as st

BLUE = "#2a78d6"
ORANGE = "#eb6834"
GRID = "#e4e3df"
LINES = ["Actual", "Base", "Your scenario"]
COLORS = {"Actual": BLUE, "Base": BLUE, "Your scenario": ORANGE}
DASHES = {"Actual": [1, 0], "Base": [6, 4], "Your scenario": [1, 0]}


def heading(title, subtitle=None):
    # Chart titles are written as text above the chart: a Vega title doesn't wrap, so a phone cut
    # it short, and under a subheader it was clipped.
    st.markdown(f"**{title}**")
    if subtitle:
        st.caption(subtitle)


def scenario_chart(long, band, y_title, band_label):
    # Only the lines present get a legend entry; the user's line appears once an input changes.
    shown = [line for line in LINES if line in set(long.line)]
    colors = [COLORS[line] for line in shown]
    dashes = [DASHES[line] for line in shown]
    legend = alt.Legend(title=None, orient="top", symbolType="stroke", symbolStrokeWidth=2)
    x = alt.X("fall_year:Q", title="Fall", axis=alt.Axis(format="d", tickMinStep=1))
    y_scale = alt.Scale(zero=False)
    shaded = (
        alt.Chart(band)
        .mark_area(color=BLUE, opacity=0.12)
        .encode(x=x, y=alt.Y("low:Q", scale=y_scale, title=y_title), y2="high:Q")
    )
    lines = (
        alt.Chart(long)
        .mark_line(strokeWidth=2, strokeCap="round", strokeJoin="round")
        .encode(
            x=x,
            y=alt.Y("value:Q", scale=y_scale),
            color=alt.Color("line:N", scale=alt.Scale(domain=shown, range=colors), legend=legend),
            strokeDash=alt.StrokeDash(
                "line:N", scale=alt.Scale(domain=shown, range=dashes), legend=legend
            ),
        )
    )
    hover = alt.selection_point(fields=["fall_year"], nearest=True, on="pointerover", empty=False)
    wide = long.pivot_table(index="fall_year", columns="line", values="value").reset_index()
    wide = wide.merge(band[["fall_year", "low", "high"]], on="fall_year", how="left")
    tooltip = [alt.Tooltip("fall_year:Q", title="Fall", format="d")]
    tooltip += [alt.Tooltip(f"{c}:Q", format=",.0f") for c in shown]
    tooltip += [
        alt.Tooltip("low:Q", title=f"{band_label}, low", format=",.0f"),
        alt.Tooltip("high:Q", title=f"{band_label}, high", format=",.0f"),
    ]
    rule = (
        alt.Chart(wide)
        .mark_rule(color="#8a8984", strokeWidth=1)
        .encode(x=x, opacity=alt.condition(hover, alt.value(1), alt.value(0)), tooltip=tooltip)
        .add_params(hover)
    )
    points = (
        alt.Chart(long)
        .mark_point(filled=True, size=64, stroke="white", strokeWidth=2)
        .encode(
            x=x,
            y=alt.Y("value:Q", scale=y_scale),
            color=alt.Color("line:N", scale=alt.Scale(domain=shown, range=colors), legend=None),
            opacity=alt.condition(hover, alt.value(1), alt.value(0)),
        )
        .transform_filter(hover)
    )
    return (
        (shaded + lines + points + rule)
        .properties(height=360)
        .configure_axis(gridColor=GRID, domainColor=GRID)
    )


def day_axis(span):
    # Both registration charts share one axis of whole days. With a single status pass, an
    # automatic scale would zoom to that one day and tick in half days.
    return alt.X(
        "days_since_registration_open:Q",
        title="Days since registration opened",
        scale=alt.Scale(domain=span),
        axis=alt.Axis(format="d", tickMinStep=1),
    )


def sections_chart(frame, span):
    x = day_axis(span)
    y = alt.Y("primary_sections:Q", title="Primary sections", scale=alt.Scale(zero=True))
    line = alt.Chart(frame).mark_line(color=BLUE, strokeWidth=2).encode(x=x, y=y)
    dots = (
        alt.Chart(frame)
        .mark_point(color=BLUE, filled=True, size=64, stroke="white", strokeWidth=2)
        .encode(
            x=x,
            y=y,
            tooltip=[
                alt.Tooltip("snapshot_date:T", title="Snapshot", format="%b %-d, %Y"),
                alt.Tooltip("days_since_registration_open:Q", title="Days since opening"),
                alt.Tooltip("primary_sections:Q", title="Primary sections"),
            ],
        )
    )
    opening = alt.Chart().mark_rule(color="#8a8984", strokeWidth=1).encode(x=alt.datum(0))
    return (
        (line + dots + opening)
        .properties(height=300)
        .configure_axis(gridColor=GRID, domainColor=GRID)
    )


def closed_share_chart(frame, span):
    x = day_axis(span)
    y = alt.Y(
        "closed_percent:Q", title="Primary sections closed (%)", scale=alt.Scale(domain=[0, 100])
    )
    data = frame.assign(closed_percent=100 * frame.closed_share)
    line = alt.Chart(data).mark_line(color=BLUE, strokeWidth=2).encode(x=x, y=y)
    dots = (
        alt.Chart(data)
        .mark_point(color=BLUE, filled=True, size=64, stroke="white", strokeWidth=2)
        .encode(
            x=x,
            y=y,
            tooltip=[
                alt.Tooltip("snapshot_date:T", title="Snapshot", format="%b %-d, %Y"),
                alt.Tooltip("closed_sections:Q", title="Closed"),
                alt.Tooltip("sections_with_status:Q", title="Primary sections with a status"),
                alt.Tooltip("restricted_sections:Q", title="Open (Restricted)"),
            ],
        )
    )
    opening = alt.Chart().mark_rule(color="#8a8984", strokeWidth=1).encode(x=alt.datum(0))
    return (
        (line + dots + opening)
        .properties(height=260)
        .configure_axis(gridColor=GRID, domainColor=GRID)
    )
