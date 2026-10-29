# Spring 2027 registration watch: primary sections per Gies course in each daily snapshot,
# and the closed share once the course-page status pass has run.

import charts
import marts
import pandas as pd
import streamlit as st

watch = marts.read("mart_registration_watch").copy()
watch["snapshot_date"] = pd.to_datetime(watch.snapshot_date)
watch["course"] = watch.subject + " " + watch.number
as_of = watch.snapshot_date.max()
latest = watch[watch.snapshot_date == as_of]
days = int(latest.days_since_registration_open.iloc[0])
opens = as_of - pd.Timedelta(days=days)
span = [int(watch.days_since_registration_open.min()), max(0, days)]

st.title("Spring 2027 registration watch")
if days < 0:
    status = f"registration opens in {-days} days, on {opens:%b %-d}"
elif days == 0:
    status = "registration opens today"
else:
    status = f"registration opened {days} days ago, on {opens:%b %-d}"
st.write(
    f"As of the {as_of:%b %-d, %Y} snapshot, {status}. Gies lists "
    f"{int(latest.primary_sections.sum()):,} primary sections across "
    f"{int((latest.primary_sections > 0).sum()):,} courses."
)

# The page opens on all of Gies, the view that answers how the schedule is filling; a course is
# one pick away.
ALL = "All Gies courses"
COUNTS = ["primary_sections", "sections_with_status", "closed_sections", "restricted_sections"]
course = st.selectbox("Course", [ALL, *sorted(watch.course.unique())])
if course == ALL:
    one = watch.groupby(["snapshot_date", "days_since_registration_open"], as_index=False)[
        COUNTS
    ].sum(min_count=1)
    one["closed_share"] = one.closed_sections / one.sections_with_status
else:
    one = watch[watch.course == course]
one = one.sort_values("snapshot_date")
now = int(one.primary_sections.iloc[-1])
charts.heading(f"{course}: {now:,} primary section{'s' if now != 1 else ''} as of {as_of:%b %-d}")
st.altair_chart(charts.sections_chart(one, span), width="stretch")

st.subheader("Enrollment status")
if watch.sections_with_status.fillna(0).sum() == 0:
    st.info(
        "Enrollment status from the Gies course pages starts with the Oct 28, 2026 pass, "
        "read at 8:14 am Central."
    )
else:
    known = one[one.sections_with_status > 0]
    if known.empty:
        st.info(f"No enrollment status is recorded for {course} yet.")
    else:
        last = known.iloc[-1]
        closed, total = int(last.closed_sections), int(last.sections_with_status)
        charts.heading(
            f"{course}: {closed:,} of {total:,} primary sections closed as of "
            f"{last.snapshot_date:%b %-d} ({100 * closed / total:.1f}%)"
        )
        st.altair_chart(charts.closed_share_chart(known, span), width="stretch")
    full = watch[
        (watch.sections_with_status > 0) & (watch.closed_sections == watch.sections_with_status)
    ]
    if full.empty:
        st.write("No Gies course has had every primary section closed yet.")
    else:
        first = full.groupby("course").snapshot_date.min().rename("first_day")
        now_closed = latest.set_index("course")[["sections_with_status", "closed_share"]]
        table = first.to_frame().join(now_closed).reset_index().sort_values(["first_day", "course"])
        st.markdown("**Courses that had every primary section closed, earliest first**")
        st.dataframe(
            table.assign(
                first_day=table.first_day.dt.strftime("%b %-d"),
                closed_share=(100 * table.closed_share).round(1),
            ).rename(
                columns={
                    "course": "Course",
                    "first_day": "First day all closed",
                    "sections_with_status": "Primary sections now",
                    "closed_share": "Closed now (%)",
                }
            ),
            hide_index=True,
            width="stretch",
        )

st.subheader("Courses that gained or lost primary sections")
changes = watch[
    (watch.sections_added_since_previous > 0) | (watch.sections_removed_since_previous > 0)
]
if changes.empty:
    st.info("No Gies course has gained or lost a primary section between snapshots yet.")
else:
    st.dataframe(
        changes.sort_values(["snapshot_date", "course"])[
            [
                "snapshot_date",
                "days_since_registration_open",
                "course",
                "primary_sections",
                "sections_added_since_previous",
                "sections_removed_since_previous",
                "sections_added_since_open",
            ]
        ].rename(
            columns={
                "snapshot_date": "Snapshot",
                "days_since_registration_open": "Days since opening",
                "course": "Course",
                "primary_sections": "Primary sections",
                "sections_added_since_previous": "Added since previous",
                "sections_removed_since_previous": "Removed since previous",
                "sections_added_since_open": "Added since registration opened",
            }
        ),
        hide_index=True,
        width="stretch",
    )

st.caption(
    "Enrollment status comes from the public course pages, read once a day at 8:14 am Central "
    "with permission from the university's Tech Services. Closed isn't the same as full, and Open "
    "(Restricted) means seats held for certain students; the closed share counts Closed only. A "
    "section added after registration opens can mean demand ran ahead of the schedule; it can "
    "also be a room or staffing change. Primary sections are lectures, lecture-discussions, "
    "online lectures, and seminars, not discussions or labs."
)
