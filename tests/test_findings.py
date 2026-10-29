from ingest.paths import TRANSFORM
from publish.findings import ANALYSES, render_table, title

# Rows from D2 as the warehouse returns them; BDI had no graded sections in Fall 2016.
COLUMNS = ["Term", "ACCY", "BADM", "BDI"]
ROWS = [("2016-fa", "40.2", "61.1", None), ("2021-sp", "69.4", "99.3", "46.0")]


def test_render_table_right_aligns_numbers_and_blanks_nulls():
    lines = render_table(COLUMNS, ROWS).splitlines()
    assert lines[0] == "| Term | ACCY | BADM | BDI |"
    assert lines[1] == "|---|---:|---:|---:|"
    assert lines[2] == "| 2016-fa | 40.2 | 61.1 |  |"


def test_render_table_with_no_rows_keeps_the_header():
    lines = render_table(COLUMNS, []).splitlines()
    assert lines == ["| Term | ACCY | BADM | BDI |", "|---|---|---|---|"]


def test_every_analysis_has_a_numbered_title_matching_its_file():
    sources = sorted(ANALYSES.glob("*.sql"))
    assert sources, f"no analyses under {ANALYSES.relative_to(TRANSFORM)}"
    titles = [title(s) for s in sources]
    assert len(set(titles)) == len(titles)
    for source, text in zip(sources, titles, strict=True):
        # c5_watch_list.sql carries the title "C5 ...".
        label = source.stem.split("_")[0].upper()
        assert text.startswith(f"{label} "), f"{source.name}: {text}"
