import pandas as pd
import pytest

from forecast import backtest, undergrad
from ingest.paths import ROOT

# Gies undergraduate headcount, first-time freshmen, and new transfers, Fall 2012 to Fall 2026,
# from mart_gies_enrollment and mart_gies_new_students.
HISTORY = pd.read_csv(ROOT / "tests" / "fixtures" / "undergrad_history.csv")


def test_project_reproduces_fall_2026_from_fall_2025():
    c = undergrad.continuing_shares(HISTORY).loc[2026]
    assert c == pytest.approx((3652 - 901 - 85) / 3329)
    assert undergrad.project(3329, 901, 85, c, 1) == [pytest.approx(3652)]


def test_base_share_is_the_median_of_the_last_five_non_covid_transitions():
    shares = undergrad.continuing_shares(HISTORY)
    expected = shares.loc[[2022, 2023, 2024, 2025, 2026]].median()
    assert undergrad.base_share(shares) == pytest.approx(expected)
    # Through Fall 2021 the last five usable transitions skip 2020 and 2021.
    through_2021 = shares[shares.index <= 2021]
    expected = shares.loc[[2015, 2016, 2017, 2018, 2019]].median()
    assert undergrad.base_share(through_2021) == pytest.approx(expected)


def test_intake_rules():
    assert undergrad.intake(HISTORY, "mean3") == (pytest.approx(783), pytest.approx(248 / 3))
    assert undergrad.intake(HISTORY, "latest") == (901, 85)


def test_backtest_never_reads_past_its_target():
    # Forecasts that end by Fall 2021 must not change when later falls are dropped.
    full = backtest.undergrad_backtest(HISTORY)
    cut = backtest.undergrad_backtest(HISTORY[HISTORY.fall_year <= 2021])
    keys = ["model", "origin", "horizon"]
    merged = full[full.target <= 2021].merge(cut, on=keys, suffixes=("_full", "_cut"))
    assert len(merged) == len(cut) > 0
    assert (merged.forecast_full == merged.forecast_cut).all()
