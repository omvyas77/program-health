# Fixtures are two IPEDS dictionaries as downloaded from NCES on Oct 23, 2026. ADM2024 uses
# the newer sheet and header capitalization; GR2017_PELL_SSL misspells its Introduction sheet.

from pathlib import Path

import pytest

from ingest.ipeds import choose_csv, read_dictionary

FIXTURES = Path(__file__).parent / "fixtures" / "ipeds"


def test_reads_title_release_and_variables():
    d = read_dictionary(FIXTURES / "ADM2024_Dict.zip")
    assert d["title"] == "File Documentation for the Admissions Data File, 2024-25"
    assert d["release"] == "(Provisional release)"
    assert d["variables"]["APPLCN"]["title"] == "Applicants total"
    assert d["variables"]["ADMSSN"]["description"].startswith("Please provide the number")


def test_reads_codes_from_frequencies():
    d = read_dictionary(FIXTURES / "GR2017_PELL_SSL_Dict.zip")
    assert "2011 cohort" in d["codes"]["PSGRTYPE"]["2"]


def test_finds_misspelled_introduction_sheet():
    d = read_dictionary(FIXTURES / "GR2017_PELL_SSL_Dict.zip")
    assert "Pell grant recipients" in d["title"]
    assert d["release"] == "(Final/revised release)"


def test_choose_csv_prefers_the_revised_file():
    # Zip listings as downloaded: ADM2022 uses _rv, ADM2023 uses _RV, GR2024 has no revision.
    assert choose_csv(["adm2022.csv", "adm2022_rv.csv"]) == "adm2022_rv.csv"
    assert choose_csv(["adm2023.csv", "adm2023_RV.csv"]) == "adm2023_RV.csv"
    assert choose_csv(["gr2024.csv"]) == "gr2024.csv"


def test_choose_csv_fails_on_an_unexpected_layout():
    with pytest.raises(AssertionError, match="unexpected CSVs"):
        choose_csv(["gr2023.csv", "gr2024.csv"])
