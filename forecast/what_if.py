# A what-if, not a forecast: if UIUC's in-state applicants rise and fall with Illinois high school
# graduates from Fall 2025 on, and in-state yield holds at its Fall 2025 level, what in-state admit
# rate keeps in-state enrollment flat through Fall 2035? Flat enrollment at a fixed yield needs a
# fixed number of admits, so the rate is Fall 2025's admits over each year's applicants.
# Institution-level, from the verified Common Data Set rows; nothing here is Gies-specific.

import logging

import duckdb
import pandas as pd

from ingest.paths import WAREHOUSE

log = logging.getLogger("what_if")

ILLINOIS = 145637
BASE_FALL = 2025
LAST_FALL = 2035

CDS_SQL = f"""
select fall_year, applicants, admits, enrolled
from mart_funnel
where unitid = {ILLINOIS} and source = 'cds' and residency = 'in_state'
order by fall_year
"""

# WICHE's public plus private total for Illinois; the class of Y enters college in Fall Y.
WICHE_SQL = f"""
select class_of as fall_year, graduates
from stg_wiche
where geography_code = 'IL'
    and school_sector = 'Grand Total (public+private)'
    and race_ethnicity = 'Total/any'
    and class_of between {BASE_FALL} and {LAST_FALL}
order by class_of
"""


def inputs():
    con = duckdb.connect(str(WAREHOUSE), read_only=True)
    return con.sql(CDS_SQL).df(), con.sql(WICHE_SQL).df()


def admit_rates(cds, graduates):
    base = cds[cds.fall_year == BASE_FALL]
    if base.empty:
        log.warning("no verified in-state CDS row for Fall %d; what-if skipped", BASE_FALL)
        return pd.DataFrame(columns=["fall_year", "scenario", "value"])
    expected = list(range(BASE_FALL, LAST_FALL + 1))
    assert graduates.fall_year.tolist() == expected, "WICHE is missing a class year"
    base = base.iloc[0]
    graduates_base = graduates.graduates.iloc[0]
    future = graduates[graduates.fall_year > BASE_FALL]
    applicants = base.applicants * future.graduates / graduates_base
    what_if = pd.DataFrame(
        {"fall_year": future.fall_year, "scenario": "what_if", "value": base.admits / applicants}
    )
    actual = pd.DataFrame(
        {"fall_year": cds.fall_year, "scenario": "actual", "value": cds.admits / cds.applicants}
    )
    return pd.concat([actual, what_if], ignore_index=True)
