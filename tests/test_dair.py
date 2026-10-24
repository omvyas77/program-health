# Fixtures are three crosstabs downloaded from DAIR's dashboards on Oct 23, 2026: the Fall 2025
# curriculum table in its wide layout, Fall 2024 student types, and retention by entry college.

from pathlib import Path

from ingest.dair import parse_class_type, parse_curriculum, parse_retention, read_crosstab

FIXTURES = Path(__file__).parent / "fixtures" / "dair"


def value(rows, **match):
    hits = [r for r in rows if all(r[k] == v for k, v in match.items())]
    assert len(hits) == 1, f"{len(hits)} rows match {match}"
    return hits[0]


def test_wide_curriculum_export_becomes_long_and_matches_dmi():
    rows = parse_curriculum(read_crosstab(FIXTURES / "curriculum_level_fa2025.csv"))
    totals = [
        int(r["Measure Values"].replace(",", "")) for r in rows if r["Measure Names"] == "Total "
    ]
    assert sum(totals) == 9640
    mba = value(rows, **{"Academic Program Code": "10KS9875MBAU", "Measure Names": "Total "})
    assert mba["Measure Values"] == "3,572"


def test_class_type_reads_both_header_rows_and_drops_totals():
    rows = parse_class_type(read_crosstab(FIXTURES / "college_class_type_fa2024.csv"))
    assert {r["Student Type"] for r in rows} == {
        "First Year Student",
        "New Transfer",
        "Readmit & Returning",
        "Continuing & Nondegree",
    }
    first_year = value(rows, **{"Student Type": "First Year Student", "Class": "Total"})
    assert (first_year["Semester"], first_year["Count"]) == ("Fall 2024", "661")


def test_retention_keeps_counts_by_entry_college_and_cohort():
    rows = parse_retention(read_crosstab(FIXTURES / "retention_by_entry_college.csv"))
    gies = {"Entry College": "Gies College of Business", "Fall Cohort": "2025 Cohort"}
    assert value(rows, **gies, Measure="Number Retained")["Value"] == "766"
    assert value(rows, **gies, Measure="Size of Adjusted Cohort")["Value"] == "787"
