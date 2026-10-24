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
page.run()
marts.footer()
