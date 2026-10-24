# Fixtures are real DMI pages from the Internet Archive: the Gies table cut from the Fall 2025
# and Fall 2012 class reports (28 and 20 columns), and the full Fall 2025 ten-day abstract.

from pathlib import Path

import pytest

from ingest.dmi import parse_abstract, parse_class_report

FIXTURES = Path(__file__).parent / "fixtures" / "dmi"


def total(rows, column, **match):
    return sum(int(r[column]) for r in rows if all(r[k] == v for k, v in match.items()))


def test_fall_2025_report_reproduces_the_college_totals():
    rows = parse_class_report((FIXTURES / "enrfa25_gies_table.html").read_bytes())
    assert len(rows) == 61
    assert total(rows, "TOTAL STUDENTS") == 9640
    assert total(rows, "TOTAL UGRAD") == 3329
    assert total(rows, "TOTAL STUDENTS", Degr="MBA") == 3572
    assert total(rows, "TOTAL STUDENTS", **{"Major Name": "Business Undeclared"}) == 1030


def test_fall_2012_report_uses_the_older_20_column_layout():
    rows = parse_class_report((FIXTURES / "enrfa12_gies_table.html").read_bytes())
    assert len(rows[0]) == 20
    assert "FULL-TIME UGRAD" not in rows[0]
    assert total(rows, "TOTAL STUDENTS") == 4042


def test_abstract_reads_the_business_block():
    rows = {r["Student Type"]: r for r in parse_abstract((FIXTURES / "FA25_ten2.htm").read_bytes())}
    freshmen = rows["First time Freshman"]
    assert [freshmen[c] for c in ("Fresh", "Soph", "Junior", "Senior", "Total")] == [
        "442",
        "312",
        "31",
        "2",
        "787",
    ]
    assert rows["New Transfer"]["Total"] == "84"
    assert rows["Total"]["Total"] == "3329"


def test_class_report_without_a_gies_table_fails():
    with pytest.raises(AssertionError, match="expected one table"):
        parse_class_report((FIXTURES / "FA25_ten2.htm").read_bytes())
