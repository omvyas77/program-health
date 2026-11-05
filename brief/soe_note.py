# The School of Education addendum: one chart and a one-page note, brief/soe_note.pdf, built from
# the two addendum marts in data/marts. Every number in the text is computed here from those marts,
# in the same style as the brief: UW-Madison in blue, peers in gray.
# `make soe-note` runs it after `make build` and `make export`.

from pathlib import Path

import duckdb
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402

from ingest.paths import MARTS  # noqa: E402

HERE = Path(__file__).parent
FIGURE = HERE / "figures" / "soe_index.png"
OUT = HERE / "soe_note.pdf"
EARLY, LATE = (2015, 2017), (2023, 2025)
PENN_STATE = 214777


def con():
    c = duckdb.connect()
    for name in ("mart_education_completions", "mart_soe_portfolio"):
        c.sql(f"create view {name} as select * from '{MARTS / name}.parquet'")
    return c


def one(c, sql):
    row = c.sql(sql).fetchone()
    assert row is not None and None not in row, f"no value for: {sql}"
    return row


def numbers(c):
    e0, e1, l0, l1 = *EARLY, *LATE
    out = {}
    for key, level in (("ba", "Bachelor''s"), ("ma", "Master''s"), ("doc", "Doctoral")):
        wi_early, wi_late = one(
            c,
            f"""
            select sum(completions) filter (where award_year_end between {e0} and {e1}) / 3,
                   sum(completions) filter (where award_year_end between {l0} and {l1}) / 3
            from mart_education_completions
            where is_wisconsin and is_education and degree_level = '{level}'""",
        )
        pe_early, pe_late = one(
            c,
            f"""
            select sum(completions) filter (where award_year_end between {e0} and {e1}) / 3,
                   sum(completions) filter (where award_year_end between {l0} and {l1}) / 3
            from mart_education_completions
            where not is_wisconsin and is_education and unitid <> {PENN_STATE}
              and degree_level = '{level}'""",
        )
        out[key] = dict(
            early=wi_early,
            late=wi_late,
            change=wi_late / wi_early - 1,
            peer_change=pe_late / pe_early - 1,
        )
    # How many of the other 17 grew master's degrees between the two windows, and Wisconsin's rank.
    growth = c.sql(f"""
        select school, is_wisconsin,
               sum(completions) filter (where award_year_end between {l0} and {l1})
             / sum(completions) filter (where award_year_end between {e0} and {e1}) - 1 as g
        from mart_education_completions
        where is_education and degree_level = 'Master''s'
        group by all order by g desc""").fetchall()
    out["ma_rank"] = [r[1] for r in growth].index(True) + 1
    out["ma_peers_grew"] = sum(1 for r in growth if not r[1] and r[2] > 0)
    out["ma_peak"] = one(
        c,
        """
        select award_year_end, academic_year, completions from (
            select award_year_end, academic_year, sum(completions) as completions
            from mart_education_completions
            where is_wisconsin and is_education and degree_level = 'Master''s' group by all)
        order by completions desc limit 1""",
    )
    out["ma_latest"] = one(
        c,
        """
        select sum(completions) from mart_education_completions
        where is_wisconsin and is_education and degree_level = 'Master''s'
          and award_year_end = 2025""",
    )[0]
    # Bachelor's growth by series, three-year totals.
    series = dict(
        c.sql(f"""
        select series,
               coalesce(sum(completions) filter (where award_year_end between {l0} and {l1}), 0)
             - coalesce(sum(completions) filter (where award_year_end between {e0} and {e1}), 0)
        from mart_education_completions
        where is_wisconsin and is_education and degree_level = 'Bachelor''s'
        group by all""").fetchall()
    )
    out["ba_series"] = series
    out["ba_total_change"] = sum(series.values())
    out["eps_first_year"], out["eps_latest"] = one(
        c,
        """
        select min(academic_year) filter (where completions >= 10),
               max(completions) filter (where award_year_end = 2025)
        from mart_education_completions
        where is_wisconsin and series = '13.09' and degree_level = 'Bachelor''s'""",
    )
    ma = dict(
        c.sql(f"""
        select series,
               coalesce(sum(completions) filter (where award_year_end between {e0} and {e1}), 0)
                    || ' to ' ||
               coalesce(sum(completions) filter (where award_year_end between {l0} and {l1}), 0)
        from mart_education_completions
        where is_wisconsin and is_education and degree_level = 'Master''s'
        group by all""").fetchall()
    )
    out["ma_series"] = ma
    # The portfolio, 2024-25.
    groups = dict(
        c.sql("""
        select field_group, sum(completions) from mart_soe_portfolio
        where award_year_end = 2025 group by all""").fetchall()
    )
    out["groups"] = groups
    out["mapped_total"] = sum(groups.values())
    out["medium"] = one(
        c,
        """
        select sum(completions) from mart_soe_portfolio
        where award_year_end = 2025 and confidence = 'medium'""",
    )[0]
    out["high_share"] = one(
        c,
        """
        select sum(completions) filter (where field_group = 'Education') / sum(completions)
        from mart_soe_portfolio
        where award_year_end = 2025 and confidence = 'high'""",
    )[0]
    return out


def figure(c):
    # brief.figures reads the warehouse when imported, so it is imported only when drawing.
    from brief.figures import BLUE, GRAY, GRID, INK, MUTED, style

    style()
    data = c.sql(f"""
        select degree_level, award_year_end,
               sum(completions) filter (where is_wisconsin) as wisconsin,
               sum(completions) filter (where not is_wisconsin and unitid <> {PENN_STATE}) as others
        from mart_education_completions
        where is_education and degree_level in ('Bachelor''s', 'Master''s')
        group by all order by all""").df()
    fig, axes = plt.subplots(1, 2, figsize=(6.5, 2.3), sharey=True)
    # The legend sits in its own band above the panel titles, so the two can't collide.
    fig.subplots_adjust(top=0.78, bottom=0.13, wspace=0.12)
    for ax, level in zip(axes, ("Bachelor's", "Master's"), strict=True):
        d = data[data.degree_level == level].sort_values("award_year_end")
        x = d.award_year_end
        for col, color, label, z in (
            ("others", GRAY, "Other 16 Big Ten schools, combined", 2),
            ("wisconsin", BLUE, "UW-Madison", 3),
        ):
            y = 100 * d[col] / d[col].iloc[0]
            ax.plot(x, y, color=color, linewidth=2, zorder=z, label=label, solid_capstyle="round")
            ax.scatter(
                x.iloc[-1],
                y.iloc[-1],
                s=22,
                color=color,
                zorder=z + 1,
                edgecolors="white",
                linewidths=1.5,
            )
            ax.annotate(
                f"{y.iloc[-1]:.0f}",
                (x.iloc[-1], y.iloc[-1]),
                xytext=(6, 0),
                textcoords="offset points",
                va="center",
                fontsize=8,
                color=INK,
            )
        ax.axhline(100, color=GRID, linewidth=0.8, zorder=1)
        ax.set_title(f"{level} degrees", loc="left", fontsize=9, color=INK, pad=4)
        ax.set_xticks([2015, 2020, 2025], ["2014-15", "2019-20", "2024-25"])
        ax.set_xlim(2014.6, 2025.9)
        ax.tick_params(axis="both", labelsize=7.5)
        ax.grid(axis="y", color=GRID, linewidth=0.5)
        ax.set_axisbelow(True)
    axes[0].set_ylabel("Index, 2014-15 = 100", fontsize=7.5)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(
        handles[::-1],
        labels[::-1],
        loc="lower left",
        bbox_to_anchor=(0.06, 0.88),
        ncol=2,
        frameon=False,
        fontsize=7.5,
        handlelength=1.6,
        borderaxespad=0,
    )
    fig.text(
        0.06,
        -0.02,
        "Education is CIP 13, first majors only. Penn State is left out of the "
        "combined line because its 2019-20 and 2020-21 files are excluded. 2024-25 is a "
        "provisional IPEDS release. Source: IPEDS completions, C2015_A to C2025_A.",
        ha="left",
        va="top",
        fontsize=6.5,
        color=MUTED,
        wrap=True,
    )
    FIGURE.parent.mkdir(exist_ok=True)
    fig.savefig(FIGURE, dpi=300, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)


def FIGURE_RATIO():  # noqa: N802
    from PIL import Image as PILImage

    with PILImage.open(FIGURE) as im:
        return im.height / im.width


def minus(text):
    return text.replace("-", "\u2212")


def pct(x):
    return minus(f"{x * 100:+.0f}%")


def note(v):
    # Imported here, not at the top, so numbers() and tests/test_soe_note.py need neither
    # reportlab nor the warehouse.
    from reportlab.lib.colors import HexColor
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont as RLFont
    from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer

    from brief.figures import INK, MUTED, static_fonts

    regular, semibold = static_fonts()
    pdfmetrics.registerFont(RLFont("SS3", str(regular)))
    pdfmetrics.registerFont(RLFont("SS3-Semibold", str(semibold)))
    ink, muted = HexColor(INK), HexColor(MUTED)
    body = ParagraphStyle(
        "body",
        fontName="SS3",
        fontSize=9.2,
        leading=12.2,
        textColor=ink,
        alignment=TA_LEFT,
        spaceAfter=5,
    )
    head = ParagraphStyle(
        "head",
        parent=body,
        fontName="SS3-Semibold",
        fontSize=10,
        leading=12.5,
        spaceBefore=4,
        spaceAfter=2,
        textColor=ink,
    )
    small = ParagraphStyle(
        "small", parent=body, fontSize=7.6, leading=9.8, textColor=muted, spaceAfter=3
    )
    title = ParagraphStyle(
        "title", parent=body, fontName="SS3-Semibold", fontSize=15, leading=18, spaceAfter=2
    )
    ba, ma, doc = v["ba"], v["ma"], v["doc"]
    s, g = v["ba_series"], v["groups"]
    peak_year, peak_label, peak_n = v["ma_peak"]

    if v["ma_rank"] == 1:
        ma_rank = "UW–Madison's master's growth is the largest of the 18"
    else:
        ma_rank = f"UW–Madison ranks {v['ma_rank']} of 18 on master's growth"
    special = minus(f"{s['13.10']:+d}")

    def share(part):
        return f"{100 * part / v['ba_total_change']:.0f}%"

    story = [
        Paragraph("The UW–Madison School of Education in public data: a first look", title),
        Paragraph(
            "An addendum to Gies Program Health · Om Hitesh Vyas · November 2026 · "
            "github.com/omvyas77/program-health · Not affiliated with or endorsed by "
            "UW–Madison",
            small,
        ),
        Spacer(1, 4),
        Paragraph("Education degrees grew at UW–Madison while they fell across the Big Ten", head),
        Paragraph(
            f"Comparing three-year averages, 2014-15 to 2016-17 against 2022-23 to 2024-25, "
            f"UW–Madison's education bachelor's degrees rose {pct(ba['change'])} "
            f"({ba['early']:.0f} to {ba['late']:.0f} a year) and its education master's degrees "
            f"rose {pct(ma['change'])} ({ma['early']:.0f} to {ma['late']:.0f}). Over the same "
            f"windows the other 16 schools combined fell {pct(ba['peer_change'])} at the "
            f"bachelor's level and {pct(ma['peer_change'])} at the master's level. "
            f"{ma_rank}, and only {v['ma_peers_grew']} of the other 17 grew at all. Doctoral "
            f"degrees held roughly level ({doc['early']:.0f} to {doc['late']:.0f} a year).",
            body,
        ),
        Image(str(FIGURE), width=6.5 * inch, height=6.5 * inch * FIGURE_RATIO()),
        Spacer(1, 3),
        Paragraph("New programs drove the bachelor's growth; two fields drove the master's", head),
        Paragraph(
            f"Three-year bachelor's totals rose by {v['ba_total_change']}. {s['13.09']} of them "
            f"({share(s['13.09'])}) are in CIP 13.09, Social and Philosophical Foundations of "
            f"Education, which first passes 10 bachelor's degrees in {v['eps_first_year']}, "
            f"reached {v['eps_latest']} in 2024-25, and matches the Educational Policy Studies "
            f"BS. Subject-area teacher education (13.13, including art and physical "
            f"education) added {s['13.13']} "
            f"and elementary teacher education (13.12) added {s['13.12']}, while special "
            f"education was about flat ({special}). At the master's level, curriculum and "
            f"instruction went from {v['ma_series']['13.03']} and special education from "
            f"{v['ma_series']['13.10']}, while educational administration went from "
            f"{v['ma_series']['13.04']}. Master's degrees peaked at {peak_n} in {peak_label} and "
            f"were {v['ma_latest']} in 2024-25, so the recent direction matters more than the "
            f"ten-year one.",
            body,
        ),
        Paragraph("Education is only about half of the degrees in the School's fields", head),
        Paragraph(
            f"IPEDS reports by field, not by school, so I mapped the CIP codes the School's ten "
            f"departments appear to confer, with a confidence for each code. In 2024-25 education "
            f"accounted for {g['Education']} of {v['mapped_total']} mapped degrees "
            f"({100 * g['Education'] / v['mapped_total']:.0f}%), kinesiology and health "
            f"{g['Kinesiology and health']}, psychology and counseling "
            f"{g['Psychology and counseling']}, and the arts {g['Arts']}. Medium-confidence codes "
            f"contribute {v['medium']} of those; counting only high-confidence codes, education "
            f"is {100 * v['high_share']:.0f}%. In either count the health, psychology, and arts "
            f"fields make up about half of the mapped degrees. These are a starting point, not "
            f"School totals.",
            body,
        ),
        Paragraph("What I would check first with internal access", head),
        Paragraph(
            "1. Reconcile the map against RADAR's Trends in Degrees, department by department, "
            "settle the medium-confidence codes, and confirm that every department's degrees were "
            "attributed to the School in every year shown. 2. Find which programs and delivery "
            "modes drove the 2021-22 master's peak and the decline since. 3. Add what public "
            "data can't show: retention and time "
            "to degree by entry program, licensure and post-graduation outcomes, scholarship "
            "awards against yield, and seat fill for high-demand courses.",
            body,
        ),
        Paragraph(
            "Limits: first majors only; certificates left out; 2024-25 is a provisional IPEDS "
            "release; Penn State is left out of the combined peer line. Every number is computed "
            "by brief/soe_note.py from data/marts, and the tables with their SQL are in "
            "docs/findings.md (F1 to F4).",
            small,
        ),
    ]
    doc_ = SimpleDocTemplate(
        str(OUT),
        pagesize=letter,
        leftMargin=inch,
        rightMargin=inch,
        topMargin=0.7 * inch,
        bottomMargin=0.6 * inch,
        title="UW-Madison School of Education in public data",
        author="Om Hitesh Vyas",
    )
    doc_.build(story)


def main():
    c = con()
    v = numbers(c)
    figure(c)
    note(v)
    print(f"wrote {OUT.relative_to(HERE.parent)} and {FIGURE.relative_to(HERE.parent)}")


if __name__ == "__main__":
    main()
