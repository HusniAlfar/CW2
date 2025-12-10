import streamlit as st
import plotly.express as px
from datetime import datetime

from hive_database.data_loader import (
    load_cyber_incidents,
    create_incident,
    update_incident,
    delete_incident,
)

# Page configuration
st.set_page_config(
    page_title="H.I.V.E. – Cyber Cell",
    page_icon="🛡️",
    layout="wide",
)

# Check login
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("⚠️ Please login first.")
    st.stop()

if st.session_state.role not in ["agent", "cyber_analyst"]:
    st.error("🚫 Access denied. Cyber Cell is only for agents and cyber analysts.")
    st.stop()

# Sidebar
st.sidebar.title("H.I.V.E. Navigation")
st.sidebar.markdown("---")
st.sidebar.write(f"**Agent:** {st.session_state.username}")
st.sidebar.write(f"**Role:** {st.session_state.role}")
st.sidebar.markdown("---")

st.sidebar.page_link("pages/dash.py", label=" H.I.V.E. Home Page",)
if st.session_state.role == "agent":
    st.sidebar.page_link("pages/data_science.py", label=" Data Science",)
    st.sidebar.page_link("pages/it_tickets.py", label=" it tickets",)

st.sidebar.markdown("---")
if st.sidebar.button(" Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.switch_page("login.py")

# Load data
df = load_cyber_incidents()

# Main title
st.title(" Cyber Security – Incident Dashboard")
st.markdown("### Monitor and manage security incidents in the H.I.V.E.")
st.markdown("---")

# Tabs
tab_overview, tab_incidents, tab_analysis = st.tabs(
    [" Overall", " Incidents", " Analysis"]
)

# ========= TAB 1 – OVERVIEW =========
with tab_overview:
    st.subheader("Threat Overview")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total incidents", len(df))
    with col2:
        st.metric("Open incidents", len(df[df["status"] == "Open"]))
    with col3:
        st.metric("Critical incidents", len(df[df["severity"] == "Critical"]))
    with col4:
        st.metric("Phishing attacks", len(df[df["category"] == "Phishing"]))

    st.markdown("---")

    c1, c2 = st.columns(2)
    # Category bar chart
    with c1:
        st.markdown("#### Incidents by category")
        cat_counts = df["category"].value_counts()
        fig_cat = px.bar(
            x=cat_counts.index,
            y=cat_counts.values,
            labels={"x": "Category", "y": "Count"},
            title="Incident categories",
        )
        st.plotly_chart(fig_cat, use_container_width=True)

    # Severity pie chart
    with c2:
        st.markdown("#### Severity levels")
        sev_counts = df["severity"].value_counts()
        fig_sev = px.pie(
            values=sev_counts.values,
            names=sev_counts.index,
            title="Severity distribution",
        )
        st.plotly_chart(fig_sev, use_container_width=True)

    st.markdown("#### Incident status")
    status_counts = df["status"].value_counts()
    fig_status = px.bar(
        x=status_counts.index,
        y=status_counts.values,
        labels={"x": "Status", "y": "Count"},
        title="Status distribution",
    )
    st.plotly_chart(fig_status, use_container_width=True)

# ========= TAB 2 – INCIDENTS =========
with tab_incidents:
    st.subheader("Incident Management")

    # --- create incident ---
    with st.expander("➕ Add new incident"):
        with st.form("create_incident_form"):
            new_id = st.number_input(
                "Incident ID",
                min_value=1,
                value=int(df["incident_id"].max() + 1),
            )
            new_time = st.text_input(
                "Timestamp",
                value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            )
            new_sev = st.selectbox(
                "Severity", ["Low", "Medium", "High", "Critical"]
            )
            new_cat = st.selectbox(
                "Category",
                ["Phishing", "Malware", "DDoS", "Unauthorized Access", "Misconfiguration"],
            )
            new_status = st.selectbox(
                "Status", ["Open", "In Progress", "Resolved", "Closed"]
            )
            new_desc = st.text_area("Description")

            create_btn = st.form_submit_button("Create incident")
            if create_btn:
                create_incident(
                    new_id, new_time, new_sev, new_cat, new_status, new_desc
                )
                st.success("✅ Incident created.")
                st.rerun()

    st.markdown("#### All incidents")

    # --- filters ---
    f1, f2, f3 = st.columns(3)
    with f1:
        sel_status = st.multiselect(
            "Filter by status",
            options=df["status"].unique().tolist(),
            default=df["status"].unique().tolist(),
        )
    with f2:
        sel_sev = st.multiselect(
            "Filter by severity",
            options=df["severity"].unique().tolist(),
            default=df["severity"].unique().tolist(),
        )
    with f3:
        sel_cat = st.multiselect(
            "Filter by category",
            options=df["category"].unique().tolist(),
            default=df["category"].unique().tolist(),
        )

    filtered = df[
        (df["status"].isin(sel_status))
        & (df["severity"].isin(sel_sev))
        & (df["category"].isin(sel_cat))
    ]

    st.dataframe(filtered, use_container_width=True)

    c_left, c_right = st.columns(2)

    # --- update ---
    with c_left:
        with st.expander("✏️ Update incident"):
            upd_id = st.selectbox(
                "Select incident ID", df["incident_id"].values
            )
            current = df[df["incident_id"] == upd_id].iloc[0]

            with st.form("update_incident_form"):
                new_status = st.selectbox(
                    "Status",
                    ["Open", "In Progress", "Resolved", "Closed"],
                    index=["Open", "In Progress", "Resolved", "Closed"].index(
                        current["status"]
                    ),
                )
                new_severity = st.selectbox(
                    "Severity",
                    ["Low", "Medium", "High", "Critical"],
                    index=["Low", "Medium", "High", "Critical"].index(
                        current["severity"]
                    ),
                )

                upd_btn = st.form_submit_button("Update incident")
                if upd_btn:
                    update_incident(
                        upd_id, status=new_status, severity=new_severity
                    )
                    st.success("✅ Incident updated.")
                    st.rerun()

    # --- delete ---
    with c_right:
        with st.expander("🗑️ Delete incident"):
            del_id = st.selectbox(
                "Select incident ID to delete",
                df["incident_id"].values,
                key="del_incident",
            )
            if st.button("Delete incident", type="primary"):
                delete_incident(del_id)
                st.success("✅ Incident deleted.")
                st.rerun()

# ========= TAB 3 – ANALYSIS =========
with tab_analysis:
    st.subheader("Threat analysis")

    st.markdown("#### Phishing focus")
    phishing_df = df[df["category"] == "Phishing"]

    c1, c2 = st.columns(2)
    with c1:
        st.metric("Total phishing incidents", len(phishing_df))
        st.metric(
            "Open / In progress",
            len(
                phishing_df[
                    phishing_df["status"].isin(["Open", "In Progress"])
                ]
            ),
        )

    with c2:
        if not phishing_df.empty:
            ph_status = phishing_df["status"].value_counts()
            fig_ph = px.pie(
                values=ph_status.values,
                names=ph_status.index,
                title="Phishing incidents by status",
            )
            st.plotly_chart(fig_ph, use_container_width=True)
        else:
            st.info("No phishing incidents in current data.")

    st.markdown("---")
    st.info(
        "💡 Use this tab in your report to discuss which categories and severities "
        "cause the most risk inside the H.I.V.E. system."
    )
