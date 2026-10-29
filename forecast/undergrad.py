# Gies undergraduate headcount as stock and flow: H(t+1) = F(t+1) + T(t+1) + c * H(t). F is
# first-time freshmen, T new transfers, and c the share of last fall's undergraduates enrolled
# again, estimated from the totals, so it absorbs graduation, attrition, readmits, and nondegree
# students. Class levels come from credit hours, so the model never moves students between classes.

import duckdb
import numpy as np

from ingest.paths import WAREHOUSE

# Transitions left out of c, keyed by the later fall: 2019 to 2020 and 2020 to 2021. 2021 to 2022
# is typical and stays in.
COVID_FALLS = {2020, 2021}
C_WINDOW = 5
INTAKE_WINDOW = 3
# mean3 matched the naive forecast in the backtest; latest lost to it at every horizon.
INTAKE_RULE = "mean3"
F_SHIFT = 0.05
C_PERCENTILES = (10, 90)

HISTORY_SQL = """
with headcount as (
    select fall_year, sum(headcount) as h
    from mart_gies_enrollment
    where level = 'undergraduate'
    group by fall_year
),

intake as (
    select
        fall_year,
        sum(headcount) filter (where student_type = 'first_time_freshman') as f,
        sum(headcount) filter (where student_type = 'new_transfer') as t,
        sum(headcount) as all_types
    from mart_gies_new_students
    group by fall_year
)

select h.fall_year, h.h, i.f, i.t, i.all_types
from headcount as h
inner join intake as i on i.fall_year = h.fall_year
order by h.fall_year
"""


def history():
    con = duckdb.connect(str(WAREHOUSE), read_only=True)
    data = con.sql(HISTORY_SQL).df()
    years = data.fall_year.tolist()
    assert years == list(range(years[0], years[-1] + 1)), f"falls are not consecutive: {years}"
    mismatched = data[data.all_types != data.h]
    assert mismatched.empty, f"student types don't add up to headcount:\n{mismatched}"
    return data[["fall_year", "h", "f", "t"]].astype(int).reset_index(drop=True)


def continuing_shares(history):
    # c for the transition into each fall, keyed by that later fall.
    indexed = history.set_index("fall_year")
    shares = (indexed.h - indexed.f - indexed.t) / indexed.h.shift(1)
    return shares.dropna()


def usable_shares(shares):
    return shares[~shares.index.isin(COVID_FALLS)]


def base_share(shares):
    usable = usable_shares(shares)
    assert len(usable), "no non-covid transitions to estimate c from"
    return float(usable.tail(C_WINDOW).median())


def intake(history, rule):
    if rule == "mean3":
        recent = history.tail(INTAKE_WINDOW)
        return float(recent.f.mean()), float(recent.t.mean())
    assert rule == "latest", f"unknown intake rule {rule!r}"
    last = history.iloc[-1]
    return float(last.f), float(last.t)


def project(h0, f, t, c, years):
    values, h = [], float(h0)
    for _ in range(years):
        h = f + t + c * h
        values.append(h)
    return values


def scenario_inputs(history, rule):
    shares = continuing_shares(history)
    f, t = intake(history, rule)
    low_c, high_c = np.percentile(usable_shares(shares), C_PERCENTILES)
    return {
        "base": (f, t, base_share(shares)),
        "low": (f * (1 - F_SHIFT), t, float(low_c)),
        "high": (f * (1 + F_SHIFT), t, float(high_c)),
    }
