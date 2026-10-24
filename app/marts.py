# Reads the committed marts in data/marts. Community Cloud puts this folder on the import path but
# not the repo root, so the path is built here rather than taken from ingest/paths.py.

from pathlib import Path

import pandas as pd
import streamlit as st

MARTS = Path(__file__).resolve().parent.parent / "data" / "marts"
REPO = "https://github.com/omvyas77/program-health"


@st.cache_data
def read(name):
    return pd.read_parquet(MARTS / f"{name}.parquet")


def footer():
    projection = read("mart_projection")
    watch = read("mart_registration_watch")
    last_fall = projection[projection.scenario == "actual"].fall_year.max()
    snapshot = watch.snapshot_date.max()
    st.divider()
    st.caption(
        "Sources: Division of Management Information enrollment reports (Fall 2012 to Fall "
        f"2025, from the Internet Archive), DAIR's Statistical Abstract (Fall {last_fall}), "
        f"and the Course Explorer API (daily snapshots, latest {snapshot:%b %-d, %Y}). "
        f"Enrollment data through Fall {last_fall}. Method and code: "
        f"[{REPO.removeprefix('https://')}]({REPO})."
    )
    st.caption(
        "An independent project, not affiliated with or endorsed by the University of Illinois."
    )
