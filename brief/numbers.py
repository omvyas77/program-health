# Every number in brief/brief.qmd comes from here. Facts come from the marts in
# warehouse/gph.duckdb; results that docs/findings.md already computes come from the same compiled
# query, read cell by cell, so the brief and the findings can't disagree. Values are formatted
# for prose: counts with commas, rates as percentages to one decimal, differences in points.
# Imported as brief.numbers, never as numbers, which would shadow the standard library module.

import re
from functools import cache

import duckdb
import yaml

from forecast import backtest, undergrad
from ingest.paths import MARTS, ROOT, TRANSFORM, WAREHOUSE
from publish.findings import ANALYSES, compiled_sql


@cache
def con():
    # The warehouse's views read data/extracts by relative path, and Quarto runs this from
    # brief/, so DuckDB resolves relative paths from the repo root instead.
    connection = duckdb.connect(str(WAREHOUSE), read_only=True)
    connection.execute(f"set file_search_path = '{ROOT}'")
    return connection


def one(sql):
    rows = con().sql(sql).fetchall()
    assert len(rows) == 1, f"expected one row, got {len(rows)}: {sql}"
    return rows[0] if len(rows[0]) > 1 else rows[0][0]


@cache
def finding(name):
    result = con().sql(compiled_sql(ANALYSES / f"{name}.sql"))
    return result.columns, result.fetchall()


def cell(name, column, **match):
    columns, rows = finding(name)
    hits = [
        r for r in rows if all(r[columns.index(k.replace("_", " "))] == v for k, v in match.items())
    ]
    assert len(hits) == 1, f"{name}: {len(hits)} rows match {match}"
    return hits[0][columns.index(column)]


def value(text):
    # Findings cells are formatted text such as "+17.5 pts", "80.0%", or "13,070".
    found = re.search(r"[+-]?[\d,]*\.?\d+", text)
    assert found, f"no number in {text!r}"
    return float(found.group().replace(",", ""))


def count(x):
    return f"{round(x):,}"


def pct(x, digits=1):
    return f"{100 * x:.{digits}f}%"


def points(x, digits=1):
    return f"{abs(100 * x):.{digits}f}"


def ordinal(k):
    suffix = "th" if 10 <= k % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(k % 10, "th")
    return f"{k}{suffix}"


def peer(metric, year=None):
    year = year or one(f"select max(data_year) from mart_peer_metrics where metric = '{metric}'")
    return one(f"""
        select value, peer_median_excl_il, rank_of_18, n_ranked, data_year_label, is_provisional
        from mart_peer_metrics
        where is_illinois and metric = '{metric}' and data_year = {year}
    """)


# Enrollment
LATEST_FALL = one("select max(fall_year) from mart_gies_enrollment")
FIRST_CHART_FALL = LATEST_FALL - 9
FIVE_FALLS_EARLIER = LATEST_FALL - 5


def headcount(fall, where="true"):
    return one(
        f"select sum(headcount) from mart_gies_enrollment where fall_year = {fall} and {where}"
    )


ONLINE = "level = 'graduate' and modality = 'online'"
total_latest = headcount(LATEST_FALL)
total_first = headcount(FIRST_CHART_FALL)
total_five_earlier = headcount(FIVE_FALLS_EARLIER)
online_latest = headcount(LATEST_FALL, ONLINE)
online_first = headcount(FIRST_CHART_FALL, ONLINE)
graduate_latest = headcount(LATEST_FALL, "level = 'graduate'")
graduate_five_earlier = headcount(FIVE_FALLS_EARLIER, "level = 'graduate'")
undergrad_latest = headcount(LATEST_FALL, "level = 'undergraduate'")
undergrad_five_earlier = headcount(FIVE_FALLS_EARLIER, "level = 'undergraduate'")
mba_online_latest = headcount(LATEST_FALL, f"{ONLINE} and program_family = 'MBA'")

gies_total = count(total_latest)
gies_total_first = count(total_first)
gies_added = count(total_latest - total_first)
online_added = count(online_latest - online_first)
online_share = pct(online_latest / graduate_latest)
online_count = count(online_latest)
graduate_count = count(graduate_latest)
mba_online = count(mba_online_latest)
total_change_five = pct(total_latest / total_five_earlier - 1)
graduate_decline_five = pct(1 - graduate_latest / graduate_five_earlier)
undergrad_change_five = pct(undergrad_latest / undergrad_five_earlier - 1)
undergrad_total = count(undergrad_latest)
undergrad_total_five_earlier = count(undergrad_five_earlier)
graduate_peak = count(
    one(
        "select max(h) from (select sum(headcount) h from mart_gies_enrollment "
        "where level = 'graduate' group by fall_year)"
    )
)


def freshmen(fall):
    return one(
        f"select headcount from mart_gies_new_students "
        f"where fall_year = {fall} and student_type = 'first_time_freshman'"
    )


freshmen_latest = count(freshmen(LATEST_FALL))
freshmen_range_low, freshmen_range_high = (
    count(x)
    for x in one(f"""
        select min(headcount), max(headcount) from mart_gies_new_students
        where student_type = 'first_time_freshman' and fall_year < {LATEST_FALL - 2}
    """)
)
first_new_students_fall = one("select min(fall_year) from mart_gies_new_students")


def juniors_seniors(fall, where="true"):
    return one(f"""
        select sum(juniors_seniors) from mart_gies_enrollment
        where level = 'undergraduate' and fall_year = {fall} and {where}
    """)


accy_js_now = count(juniors_seniors(LATEST_FALL, "program_family = 'BS Accountancy'"))
accy_js_then = count(juniors_seniors(FIVE_FALLS_EARLIER, "program_family = 'BS Accountancy'"))
fin_js_now = count(juniors_seniors(LATEST_FALL, "program_family = 'BS Finance'"))
fin_js_then = count(juniors_seniors(FIVE_FALLS_EARLIER, "program_family = 'BS Finance'"))
data_science_js = count(juniors_seniors(LATEST_FALL, "program_family like '%+ Data Science'"))
js_now = count(juniors_seniors(LATEST_FALL))
js_then = count(juniors_seniors(FIVE_FALLS_EARLIER))

# Peers
_ret = peer("ft_retention_rate")
retention, retention_median, retention_rank = pct(_ret[0]), pct(_ret[1]), ordinal(_ret[2])
retention_label = _ret[4]
_ret_then = peer(
    "ft_retention_rate",
    one("select max(data_year) from mart_peer_metrics where metric = 'ft_retention_rate'") - 5,
)
retention_gain = points(_ret[0] - _ret_then[0])
retention_median_change = points(_ret[1] - _ret_then[1])
retention_then_label = _ret_then[4]
_g6 = peer("grad_rate_6yr")
grad6, grad6_median, grad6_rank, grad6_label = pct(_g6[0]), pct(_g6[1]), ordinal(_g6[2]), _g6[4]
_g4 = peer("grad_rate_4yr")
grad4, grad4_median = pct(_g4[0]), pct(_g4[1])
_adm = peer("admit_rate")
admit, admit_median, admit_label = pct(_adm[0]), pct(_adm[1]), _adm[4]
_adm_then = peer(
    "admit_rate",
    one("select max(data_year) from mart_peer_metrics where metric = 'admit_rate'") - 5,
)
admit_then = pct(_adm_then[0])
admit_drop = points(_adm_then[0] - _adm[0])
admit_then_label = _adm_then[4]
_app = peer("applicants")
applicants = count(_app[0])
applicants_then = count(
    peer(
        "applicants",
        one("select max(data_year) from mart_peer_metrics where metric = 'applicants'") - 5,
    )[0]
)
_yield = peer("yield_rate")
yield_rate, yield_median = pct(_yield[0]), pct(_yield[1])
_share = peer("business_share_of_bachelors")
biz_share, biz_share_median, biz_share_rank = pct(_share[0]), pct(_share[1]), ordinal(_share[2])
biz_share_label = _share[4]
_masters = peer("business_masters")
biz_masters, biz_masters_median, biz_masters_rank = (
    count(_masters[0]),
    count(_masters[1]),
    _masters[2],
)
_pell = peer("pell_gap_6yr")
pell_gap, pell_gap_median, pell_label = points(_pell[0]), points(_pell[1]), _pell[4]


def outcome(college, name, cohort):
    return one(f"""
        select numerator, denominator, rate from mart_gies_outcomes
        where entry_college = '{college}' and outcome = '{name}' and cohort_year = {cohort}
    """)


GRAD_COHORT = int(_g6[4].split()[0])
gies_grad6 = pct(outcome("Gies College of Business", "grad_6yr", GRAD_COHORT)[2])
campus_grad6 = pct(outcome("All colleges", "grad_6yr", GRAD_COHORT)[2])
gies_grad4 = pct(outcome("Gies College of Business", "grad_4yr", GRAD_COHORT)[2])
campus_grad4 = pct(outcome("All colleges", "grad_4yr", GRAD_COHORT)[2])
RETENTION_COHORT = one(
    "select max(cohort_year) from mart_gies_outcomes where outcome = 'first_year_retention'"
)
_gies_ret = outcome("Gies College of Business", "first_year_retention", RETENTION_COHORT)
gies_retention, gies_retained, gies_cohort = (
    pct(_gies_ret[2]),
    count(_gies_ret[0]),
    count(_gies_ret[1]),
)
campus_retention = pct(outcome("All colleges", "first_year_retention", RETENTION_COHORT)[2])

# Grades: the first and last falls in the GPA data, and the shift-share's two falls, which
# transform/analyses/f6c_3_shift_share.sql fixes.
GRADES = "f6c_1_grades_by_term"
GRADES_FIRST_FALL, GRADES_LAST_FALL = one(
    "select min(year), max(year) from mart_course_terms where term = 'Fall'"
)
SHIFT_FROM_FALL, SHIFT_TO_FALL = 2015, 2025
_first, _last = f"{GRADES_FIRST_FALL}-fa", f"{GRADES_LAST_FALL}-fa"
a_range_2010 = cell(GRADES, "Gies A-range", Term=_first)
a_range_2025 = cell(GRADES, "Gies A-range", Term=_last)
campus_a_2010 = cell(GRADES, "Campus A-range", Term=_first)
campus_a_2025 = cell(GRADES, "Campus A-range", Term=_last)
gpa_2010 = cell(GRADES, "Gies GPA", Term=_first)
gpa_2025 = cell(GRADES, "Gies GPA", Term=_last)
campus_gpa_2010 = cell(GRADES, "Campus GPA", Term=_first)
campus_gpa_2025 = cell(GRADES, "Campus GPA", Term=_last)
dfw_2025 = cell(GRADES, "Gies DFW", Term=_last)
graded_2025 = cell(GRADES, "Gies graded", Term=_last)
TRENDS = "f6c_2_grade_trends"
gies_trend = f"{value(cell(TRENDS, 'A-range per year', Courses='Gies', Terms='Fall')):.1f}"
campus_trend = f"{value(cell(TRENDS, 'A-range per year', Courses='Campus', Terms='Fall')):.1f}"
SHIFT = "f6c_3_shift_share"
shift_total = f"{value(cell(SHIFT, 'Value', Row=3)):.1f}"
shift_within = f"{value(cell(SHIFT, 'Value', Row=7)):.1f}"
shift_mix = f"{value(cell(SHIFT, 'Value', Row=8)):.1f}"
shift_interaction = f"{value(cell(SHIFT, 'Value', Row=9)):.1f}"
shift_entering = f"{value(cell(SHIFT, 'Value', Row=10)):.1f}"
shift_courses = cell(SHIFT, "Value", Row=4).split(" in ")[1].split()[0]
watch = finding("f6c_5_watch_list")[1]
watch_count = len(watch)
watch_courses = ", ".join(r[0] for r in watch[:-1]) + f", and {watch[-1][0]}"
watch_top = max(watch, key=lambda r: value(r[6]))
watch_top_course, watch_top_rate = watch_top[0], watch_top[6]
spread_max = f"{max(value(r[6]) for r in finding('f6c_6_section_spread')[1]):.2f}"
_online = "f6c_8_online_in_person_summary"
online_pairs = cell(_online, "Course-terms", Terms="Other terms")
online_courses = cell(_online, "Courses", Terms="Other terms")
online_a_gap = f"{value(cell(_online, 'Median A-range difference', Terms='Other terms')):.1f}"

# Scheduling: Fall 2019, the last fall before covid, against the last fall with grades, the
# comparison transform/analyses/f6d_3_sections_against_students.sql makes.
SECTIONS_FROM_FALL, SECTIONS_TO_FALL = 2019, GRADES_LAST_FALL
_from, _to = f"{SECTIONS_FROM_FALL}-fa", f"{SECTIONS_TO_FALL}-fa"
SECTIONS = "f6d_1_primary_sections"
sections_2019 = cell(SECTIONS, "All Gies", Term=_from)
sections_2025 = cell(SECTIONS, "All Gies", Term=_to)
PER = "f6d_2_students_per_section"
per_section_2019 = cell(PER, "All Gies", Term=_from)
per_section_2025 = cell(PER, "All Gies", Term=_to)
students_2019 = count(
    one(f"select sum(students_graded) from mart_course_sections where yearterm = '{_from}'")
)
students_2025 = count(
    one(f"select sum(students_graded) from mart_course_sections where yearterm = '{_to}'")
)
fewer_sections_more_students = [
    r[1] for r in finding("f6d_3_sections_against_students")[1] if r[0].startswith("Fewer")
]
SNAPSHOT_DATE, SNAPSHOT_DAYS = one("""
    select snapshot_date, max(days_since_registration_open) from mart_registration_watch
    where snapshot_date = (select max(snapshot_date) from mart_registration_watch)
    group by snapshot_date
""")
snapshot_date = f"{SNAPSHOT_DATE:%b} {SNAPSHOT_DATE.day}, {SNAPSHOT_DATE.year}"
if SNAPSHOT_DAYS < 0:
    registration_status = f"registration opens in {-SNAPSHOT_DAYS} days, on Nov 2, 2026"
elif SNAPSHOT_DAYS == 0:
    registration_status = "registration opens that day"
else:
    registration_status = f"registration had been open {SNAPSHOT_DAYS} days"
registration_sections = count(
    one(f"""
    select sum(primary_sections) from mart_registration_watch
    where snapshot_date = '{SNAPSHOT_DATE}'
""")
)
registration_courses = count(
    one(f"""
    select count(*) from mart_registration_watch
    where snapshot_date = '{SNAPSHOT_DATE}' and primary_sections > 0
""")
)
snapshot_count = one("select count(distinct snapshot_date) from mart_registration_watch")
sections_added_since_open = count(
    one(f"""
    select coalesce(sum(sections_added_since_open), 0) from mart_registration_watch
    where snapshot_date = '{SNAPSHOT_DATE}'
""")
)

# Outlook
FRESHMEN_LEVER = 50
WICHE_FROM, WICHE_TO = 2025, 2035
_history = undergrad.history()
_inputs = undergrad.scenario_inputs(_history, undergrad.INTAKE_RULE)
base_f, base_t, base_c = _inputs["base"]
low_c, high_c = _inputs["low"][2], _inputs["high"][2]
_last = _history.iloc[-1]


def projected(f, t, c, years=4):
    return undergrad.project(_last.h, f, t, c, years)[-1]


LAST_PROJECTED_FALL = int(_last.fall_year) + 4
base_freshmen, base_transfers = count(base_f), count(base_t)
base_c_pct = pct(base_c)
low_c_pct, high_c_pct = pct(low_c), pct(high_c)
base_2030 = count(projected(*_inputs["base"]))
low_2030 = count(projected(*_inputs["low"]))
high_2030 = count(projected(*_inputs["high"]))
plus_50_freshmen = count(
    projected(base_f + FRESHMEN_LEVER, base_t, base_c) - projected(*_inputs["base"])
)
plus_point_c = count(projected(base_f, base_t, base_c + 0.01) - projected(*_inputs["base"]))
freshmen_hold = count(projected(_last.f, base_t, base_c))
steady_state = count(round((base_f + base_t) / (1 - base_c), -1))

_bt = backtest.summary(backtest.undergrad_backtest(_history)).set_index(["model", "horizon"])


def mape(model, horizon):
    return f"{100 * _bt.loc[(model, horizon), 'mape']:.1f}%"


model_1yr, naive_1yr = mape("stock-flow, intake mean3", 1), mape("naive", 1)
model_4yr, naive_4yr = mape("stock-flow, intake mean3", 4), mape("naive", 4)
actual_intake_1yr = mape("diagnostic: stock-flow given actual intake", 1)

_online_projection = (
    con()
    .sql(f"""
    select low, high from read_parquet('{MARTS / "mart_projection.parquet"}')
    where series = 'gies_online_graduate_headcount' and scenario = 'base'
    order by fall_year desc limit 1
""")
    .fetchone()
)
online_low_2030, online_high_2030 = count(_online_projection[0]), count(_online_projection[1])

_wiche = dict(
    con()
    .sql(f"""
    select class_of, graduates from stg_wiche
    where geography_code = 'IL' and school_sector = 'Grand Total (public+private)'
        and race_ethnicity = 'Total/any' and class_of in ({WICHE_FROM}, {WICHE_TO})
""")
    .fetchall()
)
il_grads_2025, il_grads_2035 = count(_wiche[WICHE_FROM]), count(_wiche[WICHE_TO])
il_grads_decline = pct(1 - _wiche[WICHE_TO] / _wiche[WICHE_FROM])
_cds = (
    con()
    .sql(f"""
    select applicants, admits, enrolled from mart_funnel
    where unitid = 145637 and source = 'cds' and residency = 'in_state'
        and fall_year = {WICHE_FROM}
""")
    .fetchall()
)
what_if_ready = bool(_cds)
if what_if_ready:
    _applicants, _admits, _enrolled = _cds[0]
    in_state_admit_2025 = pct(_admits / _applicants)
    in_state_yield_2025 = pct(_enrolled / _admits)
    in_state_admit_2035 = pct(_admits / (_applicants * _wiche[WICHE_TO] / _wiche[WICHE_FROM]))


# Words and small facts the prose needs, computed so a refresh can't leave them wrong.
def rose_fell(delta):
    return "rose" if delta > 0 else "fell"


graduate_peak_fall = one("""
    select fall_year from (
        select fall_year, sum(headcount) as h from mart_gies_enrollment
        where level = 'graduate' group by fall_year
    ) order by h desc limit 1
""")
freshmen_range_last_fall = LATEST_FALL - 3
intake_first_fall = LATEST_FALL - undergrad.INTAKE_WINDOW + 1
data_science_first_fall = one("""
    select min(fall_year) from mart_gies_enrollment
    where program_family like '%+ Data Science' and headcount > 0
""")
retention_median_direction = rose_fell(_ret[1] - _ret_then[1])
retention_direction = rose_fell(_ret[0] - _ret_then[0])
admit_direction = rose_fell(_adm[0] - _adm_then[0])
biz_masters_ratio = f"{_masters[0] / _masters[1]:.1f}"
pell_wider_or_narrower = "wider" if abs(_pell[0]) > abs(_pell[1]) else "narrower"
assert campus_grad6 == grad6, "DAIR's campus six-year rate no longer matches IPEDS"
grads_matching_cohort = GRAD_COHORT
_vars = yaml.safe_load((TRANSFORM / "dbt_project.yml").read_text())["vars"]
watch_min_graded = count(_vars["watch_min_graded"])
watch_min_rate = pct(_vars["watch_min_rate"], 0)
watch_min_terms = _vars["watch_min_terms"]
fewer_sections_count = len(fewer_sections_more_students)
fewer_sections_list = (
    ", ".join(fewer_sections_more_students[:-1]) + f", and {fewer_sections_more_students[-1]}"
)
BACKTEST_FIRST_ORIGIN = backtest.UNDERGRAD_ORIGINS.start
