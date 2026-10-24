# Line charts for actuals, the base, and the user's scenario, with a shaded range. Colors are the
# first two slots of a validated categorical palette; the base is dashed so it doesn't rely on
# color alone.

import altair as alt

BLUE = "#2a78d6"
ORANGE = "#eb6834"
GRID = "#e4e3df"
LINES = ["Actual", "Base", "Your scenario"]
COLORS = {"Actual": BLUE, "Base": BLUE, "Your scenario": ORANGE}
DASHES = {"Actual": [1, 0], "Base": [6, 4], "Your scenario": [1, 0]}


def scenario_chart(long, band, title, subtitle, y_title, band_label):
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
        .properties(title=alt.TitleParams(title, subtitle=subtitle), height=360)
        .configure_axis(gridColor=GRID, domainColor=GRID)
        .configure_title(anchor="start", fontSize=15)
    )


def sections_chart(frame, title):
    x = alt.X("days_since_registration_open:Q", title="Days since registration opened")
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
        .properties(title=title, height=300)
        .configure_axis(gridColor=GRID, domainColor=GRID)
        .configure_title(anchor="start", fontSize=15)
    )
