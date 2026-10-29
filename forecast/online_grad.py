# Headcount in Gies's online graduate programs, fall to fall, forecast with exponential smoothing
# and no trend. The series starts in Fall 2017, when the first online code appears, and its first
# five falls are the launch ramp. A damped-trend model carried that ramp forward and lost to the
# naive forecast at every horizon in the backtest, so this uses no trend; the backtest still runs
# both.

import duckdb
import pandas as pd
from statsmodels.tsa.exponential_smoothing.ets import ETSModel

from ingest.paths import WAREHOUSE

INTERVAL = 0.80

HISTORY_SQL = """
select fall_year, sum(headcount) as headcount
from mart_gies_enrollment
where level = 'graduate' and modality = 'online'
group by fall_year
order by fall_year
"""


def history():
    con = duckdb.connect(str(WAREHOUSE), read_only=True)
    data = con.sql(HISTORY_SQL).df().astype(int)
    years = data.fall_year.tolist()
    assert years == list(range(years[0], years[-1] + 1)), f"falls are not consecutive: {years}"
    return data


def forecast(history, years, damped_trend=False):
    # A plain integer index: statsmodels needs a pandas series for prediction intervals. With
    # damped_trend False the model has no trend at all (simple exponential smoothing).
    series = pd.Series(history.headcount.astype(float).to_numpy())
    trend = "add" if damped_trend else None
    model = ETSModel(series, error="add", trend=trend, damped_trend=damped_trend)
    fit = model.fit(disp=False)
    frame = fit.get_prediction(start=len(series), end=len(series) + years - 1).summary_frame(
        alpha=1 - INTERVAL
    )
    last = int(history.fall_year.iloc[-1])
    return pd.DataFrame(
        {
            "fall_year": range(last + 1, last + years + 1),
            "value": frame["mean"].to_numpy(),
            "low": frame["pi_lower"].to_numpy(),
            "high": frame["pi_upper"].to_numpy(),
        }
    ), {
        "alpha": float(fit.smoothing_level),
        "beta": float(fit.smoothing_trend) if damped_trend else None,
        "phi": float(fit.damping_trend) if damped_trend else None,
    }
