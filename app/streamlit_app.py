# Gies program health: enrollment scenarios and the Spring 2027 registration watch, read from the
# committed marts in data/marts. No network calls at runtime.

import marts
import streamlit as st

st.set_page_config(page_title="Gies program health", layout="wide")
page = st.navigation(
    [
        st.Page("scenarios.py", title="Enrollment scenarios", default=True),
        st.Page("registration.py", title="Registration watch"),
    ]
)
# Every page opens with what this is and where the rest of the project lives, since the app is
# often the first link someone clicks.
st.caption(
    "**Gies program health**, an independent look at the Gies College of Business from public "
    f"data. Also: [the four-page brief]({marts.BRIEF}), [six Tableau dashboards]"
    f"({marts.DASHBOARDS}), and [the code and method]({marts.REPO})."
)
page.run()
marts.footer()
