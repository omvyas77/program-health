# The brief's four figures, in one style: Illinois and Gies in blue, peers and comparisons in
# gray, no top or right spines, a title that states the finding, and a source line under each.
# Numbers in titles come from brief/numbers.py; the plotted data come from the same marts.
# Writes SVG files to brief/figures/.

import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
from fontTools.ttLib import TTFont  # noqa: E402
from fontTools.varLib import instancer  # noqa: E402
from matplotlib import font_manager  # noqa: E402

from brief import numbers as n  # noqa: E402
from ingest.paths import MARTS  # noqa: E402

HERE = Path(__file__).parent
OUT = HERE / "figures"
STATIC = HERE / "fonts" / "static"
BLUE = "#2A78D6"
GRAY = "#8C8C8C"
INK = "#333333"
MUTED = "#6B6A66"
GRID = "#E4E3DF"
SHADE = "#F0EFEC"
WIDTH = 6.5
GROUPS = {
    "Online MBA": "#2A78D6",
    "Other online graduate": "#EB6834",
    "Residential graduate": "#1BAF7A",
    "Undergraduate majors": "#EDA100",
    "Business Undeclared": "#E87BA4",
    "Undergraduate nondegree": "#008300",
}


def static_fonts():
    # matplotlib can't choose weights inside a variable font, so it gets fixed Regular and
    # Semibold instances cut from the bundled file. They are build output, kept out of the repo:
    # the font's license allows modified copies but not redistributing them under its name.
    STATIC.mkdir(exist_ok=True)
    paths = []
    for weight, style_name in ((400, "Regular"), (600, "Semibold")):
        path = STATIC / f"SourceSans3-{style_name}.ttf"
        if not path.exists():
            font = TTFont(HERE / "fonts" / "SourceSans3[wght].ttf")
            instancer.instantiateVariableFont(
                font, {"wght": weight}, inplace=True, updateFontNames=True
            )
            font.save(path)
        paths.append(path)
    return paths


def style():
    for path in static_fonts():
        font_manager.fontManager.addfont(str(path))
    plt.rcParams.update(
        {
            "font.family": "Source Sans 3",
            "font.size": 8.5,
            "text.color": INK,
            "axes.labelcolor": MUTED,
            "axes.edgecolor": GRID,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": False,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "xtick.major.size": 0,
            "ytick.major.size": 0,
            "svg.fonttype": "path",
        }
    )


def frame(sql):
    return n.con().sql(sql).df()


def finish(fig, title, source, name):
    # The title sits above the plot area and the source line below it; the saved bounds grow to
    # take both in, so neither can run into a legend or an axis.
    fig.text(
        0.0,
        1.0,
        textwrap.fill(title, 88),
        ha="left",
        va="bottom",
        fontsize=10.5,
        color=INK,
        fontweight="semibold",
        linespacing=1.3,
    )
    fig.text(0.0, -0.01, textwrap.fill(source, 130), ha="left", va="top", fontsize=7, color=MUTED)
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / f"{name}.svg", bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)


def enrollment():
    data = frame(f"""
        select
            fall_year,
            case
                when level = 'undergraduate' then
                    case
                        when program_family = 'Business Undeclared' then 'Business Undeclared'
                        when program_family = 'Nondegree' then 'Undergraduate nondegree'
                        else 'Undergraduate majors'
                    end
                when modality = 'online' then
                    case when program_family = 'MBA' then 'Online MBA'
                    else 'Other online graduate' end
                else 'Residential graduate'
            end as program_group,
            sum(headcount) as headcount
        from mart_gies_enrollment
        where fall_year >= {n.FIRST_CHART_FALL}
        group by all
    """)
    wide = data.pivot(index="fall_year", columns="program_group", values="headcount").fillna(0)
    fig, ax = plt.subplots(figsize=(WIDTH, 2.0))
    # Room above the axes for the two-row legend, so it can't run into a two-line title.
    fig.subplots_adjust(top=0.77, bottom=0.08)
    bottom = None
    for group, color in GROUPS.items():
        ax.bar(
            wide.index,
            wide[group],
            bottom=bottom,
            color=color,
            width=0.68,
            label=group,
            edgecolor="white",
            linewidth=0.8,
        )
        bottom = wide[group] if bottom is None else bottom + wide[group]
    for fall in (wide.index.min(), wide.index.max()):
        ax.text(fall, bottom[fall] + 150, f"{round(bottom[fall]):,}", ha="center", fontsize=8)
    ax.set_xticks(wide.index)
    ax.set_ylabel("Students, fall headcount")
    ax.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter("{x:,.0f}"))
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.legend(ncol=3, frameon=False, fontsize=7.5, loc="lower left", bbox_to_anchor=(0, 1.0))
    finish(
        fig,
        f"Online graduate programs account for {n.online_added} of the {n.gies_added} students "
        f"Gies added from Fall {n.FIRST_CHART_FALL} to Fall {n.LATEST_FALL}",
        "Source: DMI enrollment reports (Internet Archive), Fall 2017 to Fall 2025; DAIR "
        "Statistical Abstract, Fall 2026. Online programs have codes ending in U.",
        "enrollment",
    )


def peers():
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH, 2.45))
    fig.subplots_adjust(top=0.9, bottom=0.08, wspace=0.55)
    panels = [
        ("ft_retention_rate", f"First-year retention, {n.retention_label}"),
        (
            "business_share_of_bachelors",
            f"Business share of bachelor's degrees, {n.biz_share_label}",
        ),
    ]
    for ax, (metric, label) in zip(axes, panels, strict=True):
        data = frame(f"""
            select school, is_illinois, value, peer_median_excl_il, is_provisional
            from mart_peer_metrics
            where metric = '{metric}'
                and data_year = (select max(data_year) from mart_peer_metrics
                                 where metric = '{metric}')
            order by value
        """)
        colors = [BLUE if il else GRAY for il in data.is_illinois]
        hollow = data.is_provisional.iloc[0]
        ax.scatter(
            100 * data.value,
            data.school,
            s=26,
            zorder=3,
            facecolors="white" if hollow else colors,
            edgecolors=colors,
            linewidths=1.2,
        )
        median = 100 * data.peer_median_excl_il.iloc[0]
        ax.axvline(median, color=GRAY, linewidth=0.8, zorder=1)
        ax.set_ylim(-1.6, len(data) - 0.4)
        ax.text(median, -1.3, "peer median", fontsize=7, color=MUTED, ha="center", va="center")
        illinois = data[data.is_illinois].iloc[0]
        ax.annotate(
            f"{100 * illinois.value:.1f}%",
            (100 * illinois.value, illinois.school),
            xytext=(7, 0),
            textcoords="offset points",
            color=BLUE,
            va="center",
            fontsize=8,
        )
        for tick in ax.get_yticklabels():
            if tick.get_text() == "Illinois":
                tick.set_color(BLUE)
        ax.set_title(label, fontsize=8.5, loc="left", color=INK)
        ax.xaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter("{x:.0f}%"))
        ax.grid(axis="x", color=GRID, linewidth=0.6)
        ax.set_axisbelow(True)
        ax.spines["left"].set_visible(False)
    finish(
        fig,
        f"Illinois ranks {n.retention_rank} of 18 Big Ten schools in first-year retention and "
        f"{n.biz_share_rank} in the business share of its bachelor's degrees",
        "Source: IPEDS. Whole-university figures, not Gies. Peer median leaves Illinois out. "
        "Hollow marks are provisional data.",
        "peers",
    )


def grades():
    data = frame("""
        select
            year,
            sum(a_range) filter (where is_gies) / sum(students_graded) filter (where is_gies)
                as gies,
            sum(a_range) / sum(students_graded) as campus
        from int_course_terms
        where is_undergraduate and term = 'Fall'
        group by year
        order by year
    """)
    fig, (left, right) = plt.subplots(
        1, 2, figsize=(WIDTH, 2.3), gridspec_kw={"width_ratios": [1.45, 1]}
    )
    fig.subplots_adjust(top=0.88, bottom=0.12, wspace=0.75)
    left.axvspan(2019.5, 2020.5, color=SHADE, zorder=0)
    left.text(
        2020,
        100 * data.gies.max() + 1,
        "covid\ngrading",
        ha="center",
        va="bottom",
        fontsize=7,
        color=MUTED,
    )
    left.set_ylim(100 * data.campus.min() - 3, 100 * data.gies.max() + 7)
    left.plot(data.year, 100 * data.gies, color=BLUE, linewidth=2, marker="o", markersize=3)
    left.plot(data.year, 100 * data.campus, color=GRAY, linewidth=2, marker="o", markersize=3)
    last = data.iloc[-1]
    left.text(last.year + 0.4, 100 * last.gies, "Gies", color=BLUE, va="center", fontsize=8)
    left.text(last.year + 0.4, 100 * last.campus, "Campus", color=MUTED, va="center", fontsize=8)
    left.set_xlim(data.year.min() - 0.5, data.year.max() + 3)
    left.set_xticks(range(int(data.year.min()), int(data.year.max()) + 1, 5))
    left.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter("{x:.0f}%"))
    left.grid(axis="y", color=GRID, linewidth=0.6)
    left.set_axisbelow(True)
    left.set_title("A-range share of undergraduate grades, fall terms", fontsize=8.5, loc="left")
    parts = [
        ("Within courses", float(n.shift_within)),
        ("Both together", float(n.shift_interaction)),
        ("Course mix", float(n.shift_mix)),
        ("Added or dropped", float(n.shift_entering)),
    ][::-1]
    labels, values = [p[0] for p in parts], [p[1] for p in parts]
    right.barh(labels, values, color=[GRAY, GRAY, GRAY, BLUE], height=0.55)
    for label, v in zip(labels, values, strict=True):
        right.text(v + 0.4, label, f"{v:.1f}", va="center", fontsize=8)
    right.set_xlim(0, max(values) * 1.2)
    right.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(5))
    right.spines["left"].set_visible(False)
    right.set_title(
        f"Points of the rise, Fall {n.SHIFT_FROM_FALL} to {n.SHIFT_TO_FALL}",
        fontsize=8.5,
        loc="left",
    )
    finish(
        fig,
        f"{n.a_range_2025} of grades in Gies undergraduate courses were in the A range in Fall "
        f"{n.GRADES_LAST_FALL}, against {n.campus_a_2025} campus-wide; {n.shift_within} of the "
        f"{n.shift_total}-point rise since Fall {n.SHIFT_FROM_FALL} happened inside the same "
        "courses",
        "Source: UIUC GPA dataset (wadefagen/datasets), sections with 21 or more graded "
        "students. A range is A+, A, and A-. The split uses the "
        f"{n.shift_courses} Gies courses taught in both terms, weighted by graded students.",
        "grades",
    )


def projection():
    data = frame(f"""
        select fall_year, scenario, value
        from read_parquet('{MARTS / "mart_projection.parquet"}')
        where series = 'gies_undergraduate_headcount'
    """)
    wide = data.pivot(index="fall_year", columns="scenario", values="value")
    actual = wide.actual.dropna()
    last_fall, last_value = actual.index.max(), actual.iloc[-1]
    projected = wide.loc[wide.index > last_fall]
    years = [last_fall, *projected.index]
    fig, ax = plt.subplots(figsize=(WIDTH, 1.8))
    fig.subplots_adjust(top=0.95, bottom=0.08)
    ax.fill_between(
        years,
        [last_value, *projected.low],
        [last_value, *projected.high],
        color=BLUE,
        alpha=0.12,
        linewidth=0,
    )
    ax.plot(actual.index, actual.values, color=BLUE, linewidth=2)
    ax.plot(years, [last_value, *projected.base], color=BLUE, linewidth=2, linestyle=(0, (4, 3)))
    for scenario in ("low", "base", "high"):
        ax.text(
            projected.index.max() + 0.25,
            projected[scenario].iloc[-1],
            f"{scenario} {round(projected[scenario].iloc[-1]):,}",
            va="center",
            fontsize=8,
            color=BLUE if scenario == "base" else MUTED,
        )
    ax.set_xlim(actual.index.min() - 0.5, projected.index.max() + 2.5)
    ax.set_xticks(range(actual.index.min(), projected.index.max() + 1, 3))
    ax.set_ylabel("Undergraduates, fall headcount")
    ax.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter("{x:,.0f}"))
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    finish(
        fig,
        f"The base scenario has {n.base_2030} Gies undergraduates in Fall {n.LAST_PROJECTED_FALL}, "
        f"from {n.undergrad_total} in Fall {n.LATEST_FALL}",
        "Source: DMI and DAIR headcounts; projection in docs/projection_method.md. Shaded: low "
        "and high scenarios. In a backtest the model matched the naive forecast.",
        "projection",
    )


def main():
    style()
    for draw in (enrollment, peers, grades, projection):
        draw()


if __name__ == "__main__":
    main()
