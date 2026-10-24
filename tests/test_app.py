import sys

import pandas as pd
from streamlit.testing.v1 import AppTest

from forecast import undergrad
from ingest.paths import MARTS, ROOT

# The app's modules import each other by bare name, as Streamlit runs them.
sys.path.insert(0, str(ROOT / "app"))
import model  # noqa: E402

APP = str(ROOT / "app" / "streamlit_app.py")
HISTORY = pd.read_csv(ROOT / "tests" / "fixtures" / "undergrad_history.csv")


def test_app_recurrence_matches_the_forecast():
    for f, t, c in undergrad.scenario_inputs(HISTORY, "mean3").values():
        assert model.project(3652, f, t, c, 4) == undergrad.project(3652, f, t, c, 4)


def test_change_line_reports_the_difference_from_base():
    line = model.change_line("undergraduates", 2030, 4032.6, 3841.4, ["first-time freshmen"])
    assert line.startswith("Your scenario has 4,033 undergraduates in Fall 2030, 192 more than")
    assert model.change_line("undergraduates", 2030, 3841.4, 3841.4, []).endswith(
        "3,841 undergraduates in Fall 2030."
    )


def test_scenarios_page_renders_the_base_and_reacts_to_an_input():
    app = AppTest.from_file(APP, default_timeout=60).run()
    assert not app.exception
    base = pd.read_parquet(MARTS / "mart_projection.parquet")
    last = base[(base.series == "gies_undergraduate_headcount") & (base.scenario == "base")]
    expected = f"{last.value.iloc[-1]:,.0f} undergraduates"
    assert any(expected in m.value for m in app.markdown)
    app.number_input[0].set_value(850.0).run()
    assert not app.exception
    assert any(m.value.startswith("Your scenario has") for m in app.markdown)


def test_registration_page_renders():
    app = AppTest.from_file(APP, default_timeout=60).run()
    app.switch_page("registration.py").run()
    assert not app.exception
    assert app.title[0].value == "Spring 2027 registration watch"
