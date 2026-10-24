# Spring 2027 registration watch: primary sections per Gies course in each daily snapshot.

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

courses = sorted(watch.course.unique())
largest = latest.sort_values(["primary_sections", "course"], ascending=[False, True]).course.iloc[0]
course = st.selectbox("Course", courses, index=courses.index(largest))
one = watch[watch.course == course].sort_values("snapshot_date")
now = int(one.primary_sections.iloc[-1])
st.altair_chart(
    charts.sections_chart(
        one,
        f"{course}: {now} primary section{'s' if now != 1 else ''} as of {as_of:%b %-d}",
    ),
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
    "The Course Explorer API doesn't report whether a section is open or closed, so this tracks "
    "the section list. A section added after registration opens can mean demand ran ahead of the "
    "schedule; it can also be a room or staffing change. Primary sections are lectures, "
    "lecture-discussions, online lectures, and seminars, not discussions or labs."
)
