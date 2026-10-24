# Fixtures: Nebraska's 2025-26 CDS Applications page as published, and the CDS-C sheet copied
# out of Illinois's 2024-25 workbook (section A, which names the person who filled it in, is
# left out).

from pathlib import Path

from ingest.cds import html_rows, read_c1, summarize, xlsx_rows

FIXTURES = Path(__file__).parent / "fixtures" / "cds"


def test_web_page_reads_gender_rows_and_residency_columns():
    found = read_c1(list(html_rows(FIXTURES / "nebraska_2025-26.html")), tolerance=0)
    values, _, _ = summarize(found)
    assert (values["applicants_total"], values["admits_total"], values["enrolled_total"]) == (
        18648,
        16372,
        4734,
    )
    assert (values["applicants_in_state"], values["applicants_out_of_state"]) == (9229, 8413)
    assert values["enrolled_international"] == 64


def test_workbook_residency_blocks_are_read_by_item_code():
    found = read_c1(list(xlsx_rows(FIXTURES / "illinois_2024-25_cds_c.xlsx")), tolerance=0)
    values, wheres, _ = summarize(found)
    assert (values["applicants_total"], values["admits_total"], values["enrolled_total"]) == (
        73742,
        31247,
        9008,
    )
    assert [values[f"applicants_{p}"] for p in ("in_state", "out_of_state", "international")] == [
        27730,
        27575,
        18437,
    ]
    assert all(w.startswith("CDS-C!") for w in wheres)
