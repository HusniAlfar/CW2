import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from hive_database.data_loader import (
    load_it_tickets,
    create_ticket,
    update_ticket,
    delete_ticket,
)

# -----------------------------
# Page configuration (H.I.V.E.)
# -----------------------------
st.set_page_config(
    page_title="H.I.V.E. Tech Cell",
    page_icon="🐝",
    layout="wide"
)

# -----------------------------
# Check login and role
# -----------------------------
# if user is not logged in, stop the page
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("⚠️ Please login to access the H.I.V.E. Tech Cell")
    st.stop()

# only some roles can see this page
# change this list if you want other roles
allowed_roles = ["agent", "it_overseer"]
if st.session_state.role not in allowed_roles:
    st.error("🚫 Access denied – your H.I.V.E. role cannot view this console")
    st.stop()

# -----------------------------
# Sidebar (left menu)
# -----------------------------
st.sidebar.title(" H.I.V.E. Navigation")
st.sidebar.markdown("---")
st.sidebar.write(f"** Agent:** {st.session_state.username}")
st.sidebar.write(f"** Role:** {st.session_state.role}")
st.sidebar.markdown("---")

# link back to main H.I.V.E. dashboard
st.sidebar.page_link("pages/dash.py", label=" H.I.V.E. Home Page",)

# links to other cells (modules)
st.sidebar.page_link("pages/cybersecurity.py", label=" Cyber Security",)
st.sidebar.page_link("pages/data_science.py", label=" Data Science",)

st.sidebar.markdown("---")

# logout button
if st.sidebar.button(" Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.switch_page("login.py")

# -----------------------------
# Load IT ticket data
# -----------------------------
# here we read all tickets from database (or CSV inside the loader)
df = load_it_tickets()

# -----------------------------
# Page header
# -----------------------------
st.title(" H.I.V.E. Tech Cell – Ticket Console")
st.markdown("### Monitoring support tickets for H.I.V.E. infrastructure")
st.markdown("---")

# -----------------------------
# Top metrics (small boxes)
# -----------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Tickets", len(df))

with col2:
    open_tickets = len(df[df["status"] == "Open"])
    st.metric("Open Tickets", open_tickets)

with col3:
    avg_resolution = df["resolution_time_hours"].mean()
    st.metric("Avg Resolution", f"{avg_resolution:.1f} hrs")

with col4:
    critical = len(df[df["priority"] == "Critical"])
    st.metric("Critical Tickets", critical)

st.markdown("---")

# -----------------------------
# Tabs for different views
# -----------------------------
tab_overview, tab_tickets, tab_analysis = st.tabs(
    [" Overview", " Tickets", " Analysis"]
)

# ============================
# TAB 1 – OVERVIEW
# ============================
with tab_overview:
    st.subheader("Tech Cell Overview")

    col1, col2 = st.columns(2)

    # --- chart: tickets by priority ---
    with col1:
        st.markdown("#### Tickets by Priority")
        priority_counts = df["priority"].value_counts()
        fig1 = px.bar(
            x=priority_counts.index,
            y=priority_counts.values,
            labels={"x": "Priority", "y": "Count"},
            title="Ticket Priority Distribution",
        )
        st.plotly_chart(fig1, use_container_width=True)

    # --- chart: tickets by status ---
    with col2:
        st.markdown("#### Ticket Status")
        status_counts = df["status"].value_counts()
        fig2 = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Status Distribution",
        )
        st.plotly_chart(fig2, use_container_width=True)

    # --- chart: tickets per staff member ---
    st.markdown("#### Staff Workload in H.I.V.E. Tech Cell")
    staff_counts = df["assigned_to"].value_counts()
    fig3 = px.bar(
        x=staff_counts.index,
        y=staff_counts.values,
        labels={"x": "Tech Agent", "y": "Tickets Assigned"},
        title="Tickets per Tech Agent",
    )
    st.plotly_chart(fig3, use_container_width=True)

# ============================
# TAB 2 – TICKET MANAGEMENT
# ============================
with tab_tickets:
    st.subheader("Ticket Management – H.I.V.E. Support Queue")

    # -------------
    # create ticket
    # -------------
    with st.expander("➕ Create New Ticket"):
        with st.form("create_ticket"):
            # basic inputs for new ticket
            new_id = st.number_input(
                "Ticket ID",
                min_value=1,
                value=int(df["ticket_id"].max() + 1)
            )
            new_priority = st.selectbox(
                "Priority",
                ["Low", "Medium", "High", "Critical"]
            )
            new_description = st.text_area("Description")
            new_status = st.selectbox(
                "Status",
                ["Open", "In Progress", "Resolved", "Waiting for User"]
            )
            new_assigned = st.selectbox(
                "Assign To",
                ["Tech_Agent_A", "Tech_Agent_B", "Tech_Agent_C"]
            )
            new_created = st.text_input(
                "Created At",
                value=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            new_resolution = st.number_input(
                "Resolution Time (hours)",
                min_value=0.0,
                value=0.0
            )

            if st.form_submit_button("Create Ticket"):
                # call helper to save ticket in database
                create_ticket(
                    new_id,
                    new_priority,
                    new_description,
                    new_status,
                    new_assigned,
                    new_created,
                    new_resolution,
                )
                st.success("✅ New H.I.V.E. ticket created")
                st.rerun()

    # -------------
    # list tickets
    # -------------
    st.markdown("#### All Tickets in Queue")

    # simple filters
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_status = st.multiselect(
            "Filter by Status",
            df["status"].unique(),
            default=df["status"].unique(),
        )
    with col2:
        filter_priority = st.multiselect(
            "Filter by Priority",
            df["priority"].unique(),
            default=df["priority"].unique(),
        )
    with col3:
        filter_staff = st.multiselect(
            "Filter by Tech Agent",
            df["assigned_to"].unique(),
            default=df["assigned_to"].unique(),
        )

    # apply filters to dataframe
    filtered_df = df[
        (df["status"].isin(filter_status))
        & (df["priority"].isin(filter_priority))
        & (df["assigned_to"].isin(filter_staff))
    ]

    st.dataframe(filtered_df, use_container_width=True)

    # -------------
    # update / delete
    # -------------
    col1, col2 = st.columns(2)

    # --- update ticket ---
    with col1:
        with st.expander(" Update Ticket"):
            update_id = st.selectbox(
                "Select Ticket ID",
                df["ticket_id"].values
            )
            ticket = df[df["ticket_id"] == update_id].iloc[0]

            with st.form("update_ticket"):
                status_options = [
                    "Open",
                    "In Progress",
                    "Resolved",
                    "Waiting for User",
                ]
                priority_options = ["Low", "Medium", "High", "Critical"]

                upd_status = st.selectbox(
                    "Status",
                    status_options,
                    index=status_options.index(ticket["status"]),
                )
                upd_priority = st.selectbox(
                    "Priority",
                    priority_options,
                    index=priority_options.index(ticket["priority"]),
                )
                upd_resolution = st.number_input(
                    "Resolution Time (hrs)",
                    value=float(ticket["resolution_time_hours"]),
                )

                if st.form_submit_button("Update"):
                    update_ticket(
                        update_id,
                        status=upd_status,
                        priority=upd_priority,
                        resolution_time_hours=upd_resolution,
                    )
                    st.success("✅ Ticket updated for H.I.V.E. Tech Cell")
                    st.rerun()

    # --- delete ticket ---
    with col2:
        with st.expander("🗑️ Delete Ticket"):
            delete_id = st.selectbox(
                "Select Ticket ID to Delete",
                df["ticket_id"].values,
                key="delete",
            )

            if st.button("Delete Ticket", type="primary"):
                delete_ticket(delete_id)
                st.success("✅ Ticket removed from H.I.V.E. queue")
                st.rerun()

# ============================
# TAB 3 – ANALYSIS
# ============================
with tab_analysis:
    st.subheader("Performance Analysis – H.I.V.E. Tech Agents")

    # -------------
    # staff performance
    # -------------
    st.markdown("####  Tech Agent Performance")

    staff_performance = df.groupby("assigned_to").agg(
        {
            "ticket_id": "count",
            "resolution_time_hours": "mean",
        }
    ).rename(
        columns={
            "ticket_id": "total_tickets",
            "resolution_time_hours": "avg_resolution_time",
        }
    )

    staff_performance = staff_performance.sort_values(
        "avg_resolution_time",
        ascending=False,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Average Resolution Time by Tech Agent**")
        st.dataframe(staff_performance, use_container_width=True)

        slowest_staff = staff_performance["avg_resolution_time"].idxmax()
        slowest_time = staff_performance["avg_resolution_time"].max()

        st.warning(
            f"⚠️ Performance alert: {slowest_staff} has the highest "
            f"average resolution time ({slowest_time:.1f} hours)"
        )

    with col2:
        fig = px.bar(
            staff_performance,
            x=staff_performance.index,
            y="avg_resolution_time",
            labels={
                "x": "Tech Agent",
                "avg_resolution_time": "Avg Resolution Time (hrs)",
            },
            title="Average Resolution Time by Tech Agent",
        )
        st.plotly_chart(fig, use_container_width=True)

    # -------------
    # status bottleneck
    # -------------
    st.markdown("####  Status Bottleneck Analysis")

    status_resolution = (
        df.groupby("status")["resolution_time_hours"]
        .mean()
        .sort_values(ascending=False)
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Average Resolution Time by Status**")
        st.dataframe(status_resolution, use_container_width=True)

        bottleneck_status = status_resolution.idxmax()
        bottleneck_time = status_resolution.max()

        st.info(
            f" Bottleneck: tickets in '{bottleneck_status}' status "
            f"take the longest time ({bottleneck_time:.1f} hours)"
        )

    with col2:
        fig = px.bar(
            x=status_resolution.index,
            y=status_resolution.values,
            labels={"x": "Status", "y": "Avg Resolution Time (hrs)"},
            title="Resolution Time by Status",
        )
        st.plotly_chart(fig, use_container_width=True)

    # -------------
    # priority vs resolution
    # -------------
    st.markdown("####  Priority vs Resolution Time")

    fig = px.box(
        df,
        x="priority",
        y="resolution_time_hours",
        labels={
            "priority": "Priority",
            "resolution_time_hours": "Resolution Time (hours)",
        },
        title="Resolution Time Distribution by Priority",
    )
    st.plotly_chart(fig, use_container_width=True)

# footer
st.markdown("---")
st.caption(" H.I.V.E. Tech Cell – Infrastructure Support Module")
