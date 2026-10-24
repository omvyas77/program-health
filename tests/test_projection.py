import pandas as pd
import pytest

from forecast import what_if
from ingest.paths import MARTS

PROJECTION = MARTS / "mart_projection.parquet"
COLUMNS = {
    "series": "str",
    "fall_term": "str",
    "fall_year": "int32",
    "scenario": "str",
    "value": "float64",
    "low": "float64",
    "high": "float64",
}
SCENARIOS = {"actual", "base", "low", "high", "what_if"}

# Illinois's Fall 2025 in-state row as read from its 2025-26 CDS workbook (CDS-C!F37:F39), and
# WICHE's Illinois public plus private graduates, classes of 2025 to 2030 and 2035.
CDS = pd.DataFrame(
    {"fall_year": [2025], "applicants": [29419], "admits": [14509], "enrolled": [6587]}
)


def wiche(classes):
    graduates = {2025: 144561, 2030: 124210, 2035: 119005}
    return pd.DataFrame({"fall_year": classes, "graduates": [graduates[c] for c in classes]})


def test_mart_projection_schema():
    data = pd.read_parquet(PROJECTION)
    assert dict(data.dtypes.astype(str)) == COLUMNS
    assert not data.duplicated(["series", "fall_year", "scenario"]).any()
    assert set(data.scenario) <= SCENARIOS
    assert (data.fall_term == "Fall " + data.fall_year.astype(str)).all()
    assert data.value.notna().all()
    bounded = data.dropna(subset=["low", "high"])
    assert ((bounded.low <= bounded.value) & (bounded.value <= bounded.high)).all()


def test_projection_starts_after_the_last_actual_fall():
    data = pd.read_parquet(PROJECTION)
    for series, rows in data.groupby("series"):
        last_actual = rows[rows.scenario == "actual"].fall_year.max()
        projected = rows[rows.scenario != "actual"].fall_year
        assert projected.min() == last_actual + 1, series


def test_what_if_admit_rate_holds_admits_fixed(monkeypatch):
    monkeypatch.setattr(what_if, "LAST_FALL", 2030)
    classes = list(range(2025, 2031))
    graduates = pd.DataFrame(
        {"fall_year": classes, "graduates": [144561, 138905, 135221, 129922, 127932, 124210]}
    )
    rates = what_if.admit_rates(CDS, graduates).set_index(["scenario", "fall_year"]).value
    assert rates["actual", 2025] == pytest.approx(14509 / 29419)
    assert rates["what_if", 2030] == pytest.approx(14509 / (29419 * 124210 / 144561))


def test_what_if_is_skipped_without_a_verified_row():
    empty = CDS.iloc[0:0]
    assert what_if.admit_rates(empty, wiche([2025, 2030, 2035])).empty
