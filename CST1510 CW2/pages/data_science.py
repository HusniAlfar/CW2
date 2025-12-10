import streamlit as st
import plotly.express as px
from datetime import datetime

# import helpers from our H.I.V.E. database module
from hive_database.data_loader import (
    load_datasets_metadata,
    create_dataset,
    update_dataset,
    delete_dataset,
)

# -----------------------------
# Page configuration (H.I.V.E.)
# -----------------------------
st.set_page_config(
    page_title="H.I.V.E. Data",
    page_icon="📊",
    layout="wide",
)

# -----------------------------
# Check if user is logged in
# -----------------------------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("⚠️ Please login to access the H.I.V.E. Data Lab")
    st.stop()

# only some roles can see this page
if st.session_state.role not in ["agent", "data_scientist"]:
    st.error("🚫 Access denied – your H.I.V.E. role cannot view this lab")
    st.stop()

# -----------------------------
# Sidebar (left menu)
# -----------------------------
st.sidebar.title("H.I.V.E. Navigation")
st.sidebar.markdown("---")
st.sidebar.write(f"**👤 Agent:** {st.session_state.username}")
st.sidebar.write(f"**🎭 Role:** {st.session_state.role}")
st.sidebar.markdown("---")

# link back to main dashboard  (NO empty icon argument!)
st.sidebar.page_link("pages/dash.py", label="🏠 H.I.V.E. Home Page")

# normal agent can see all cells
if st.session_state.role == "agent":
    st.sidebar.page_link("pages/cybersecurity.py", label="🛡️ Cyber Security")
    st.sidebar.page_link("pages/it_tickets.py", label="💻 IT Tickets")

st.sidebar.markdown("---")

# logout button
if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.switch_page("login.py")

# -----------------------------
# Load dataset metadata
# -----------------------------
df = load_datasets_metadata()

# -----------------------------
# Main header
# -----------------------------
st.title("📊 H.I.V.E. Data Lab")
st.markdown("### Dataset Management & Analytics for H.I.V.E.")
st.markdown("---")

# -----------------------------
# Top metrics
# -----------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Datasets", len(df))

with col2:
    total_rows = df["rows"].sum()
    st.metric("Total Rows", f"{total_rows:,}")

with col3:
    # simple estimate: 1 KB per row
    storage_gb = (total_rows * 1000) / (1024**3)
    st.metric("Est. Storage", f"{storage_gb:.2f} GB")

with col4:
    sources = df["uploaded_by"].nunique()
    st.metric("Data Sources", sources)

st.markdown("---")

# -----------------------------
# Tabs: overview / datasets / analysis
# -----------------------------
tab_overview, tab_datasets, tab_analysis = st.tabs(
    ["📊 Overview", "📋 Datasets", "🔍 Analysis"]
)

# ============================
# TAB 1 – OVERVIEW
# ============================
with tab_overview:
    st.subheader("Dataset Overview in H.I.V.E.")

    col1, col2 = st.columns(2)

    # --- bar chart: rows per dataset ---
    with col1:
        st.markdown("#### Dataset Size (Rows)")
        fig1 = px.bar(
            df,
            x="name",
            y="rows",
            title="Rows per Dataset",
            labels={"name": "Dataset", "rows": "Number of Rows"},
        )
        fig1.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig1, use_container_width=True)

    # --- pie chart: datasets by source ---
    with col2:
        st.markdown("#### Data Sources")
        source_counts = df["uploaded_by"].value_counts()
        fig2 = px.pie(
            values=source_counts.values,
            names=source_counts.index,
            title="Datasets by Source",
        )
        st.plotly_chart(fig2, use_container_width=True)

    # --- scatter: rows vs columns ---
    st.markdown("#### Dataset Complexity")
    fig3 = px.scatter(
        df,
        x="rows",
        y="columns",
        size="rows",
        hover_data=["name"],
        title="Rows vs Columns",
        labels={
            "rows": "Number of Rows",
            "columns": "Number of Columns",
        },
    )
    st.plotly_chart(fig3, use_container_width=True)

# ============================
# TAB 2 – DATASET MANAGEMENT
# ============================
with tab_datasets:
    st.subheader("Dataset Management – H.I.V.E. Data Lab")

    # -------------
    # add new dataset
    # -------------
    with st.expander("➕ Add New Dataset"):
        with st.form("create_dataset"):
            new_id = st.number_input(
                "Dataset ID",
                min_value=1,
                value=int(df["dataset_id"].max() + 1),
            )
            new_name = st.text_input("Dataset Name")
            new_rows = st.number_input(
                "Number of Rows",
                min_value=0,
                value=1000,
            )
            new_columns = st.number_input(
                "Number of Columns",
                min_value=1,
                value=10,
            )
            new_uploaded_by = st.selectbox(
                "Uploaded By",
                ["data_scientist", "cyber_analyst", "it_overseer"],
            )
            new_upload_date = st.date_input(
                "Upload Date",
                value=datetime.now(),
            )

            if st.form_submit_button("Add Dataset"):
                create_dataset(
                    new_id,
                    new_name,
                    new_rows,
                    new_columns,
                    new_uploaded_by,
                    str(new_upload_date),
                )
                st.success("✅ Dataset added to H.I.V.E. Data Lab")
                st.rerun()

    # -------------
    # list all datasets with filters
    # -------------
    st.markdown("#### All Datasets")

    col1, col2 = st.columns(2)

    with col1:
        filter_source = st.multiselect(
            "Filter by Source",
            df["uploaded_by"].unique(),
            default=df["uploaded_by"].unique(),
        )

    with col2:
        min_rows = st.number_input(
            "Minimum Rows",
            min_value=0,
            value=0,
        )

    filtered_df = df[
        (df["uploaded_by"].isin(filter_source))
        & (df["rows"] >= min_rows)
    ]

    st.dataframe(filtered_df, use_container_width=True)

    # -------------
    # update / delete dataset
    # -------------
    col1, col2 = st.columns(2)

    # --- update dataset ---
    with col1:
        with st.expander("✏️ Update Dataset"):
            update_id = st.selectbox(
                "Select Dataset ID",
                df["dataset_id"].values,
            )
            dataset = df[df["dataset_id"] == update_id].iloc[0]

            with st.form("update_dataset"):
                upd_name = st.text_input("Name", value=dataset["name"])
                upd_rows = st.number_input(
                    "Rows",
                    value=int(dataset["rows"]),
                )
                upd_columns = st.number_input(
                    "Columns",
                    value=int(dataset["columns"]),
                )

                if st.form_submit_button("Update"):
                    update_dataset(
                        update_id,
                        name=upd_name,
                        rows=upd_rows,
                        columns=upd_columns,
                    )
                    st.success("✅ Dataset updated in H.I.V.E.")
                    st.rerun()

    # --- delete dataset ---
    with col2:
        with st.expander("🗑️ Delete Dataset"):
            delete_id = st.selectbox(
                "Select Dataset ID to Delete",
                df["dataset_id"].values,
                key="delete",
            )

            if st.button("Delete Dataset", type="primary"):
                delete_dataset(delete_id)
                st.success("✅ Dataset removed from H.I.V.E. Data Lab")
                st.rerun()

# ============================
# TAB 3 – ANALYSIS / GOVERNANCE
# ============================
with tab_analysis:
    st.subheader("Data Governance Analysis – H.I.V.E.")

    # -------------
    # resource consumption
    # -------------
    st.markdown("#### 🎯 High-Value Insight: Resource Consumption")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Largest Datasets (by rows)**")
        top_datasets = df.nlargest(3, "rows")[
            ["name", "rows", "uploaded_by"]
        ]
        st.dataframe(top_datasets, use_container_width=True)

    with col2:
        st.markdown("**Source Dependency (total rows per source)**")
        source_rows = (
            df.groupby("uploaded_by")["rows"]
            .sum()
            .sort_values(ascending=False)
        )
        fig = px.bar(
            x=source_rows.index,
            y=source_rows.values,
            labels={"x": "Source", "y": "Total Rows"},
            title="Total Rows per Source",
        )
        st.plotly_chart(fig, use_container_width=True)

    # -------------
    # archiving suggestion
    # -------------
    st.markdown("#### 📋 Data Governance Recommendations")

    large_threshold = df["rows"].quantile(0.75)
    large_datasets = df[df["rows"] > large_threshold]

    st.info(
        f"💡 Archiving suggestion: {len(large_datasets)} datasets "
        f"are above the 75th percentile ({large_threshold:,.0f} rows). "
        "These datasets can be reviewed for archiving or compression."
    )

    if len(large_datasets) > 0:
        st.markdown("**Datasets suggested for archiving:**")
        st.dataframe(
            large_datasets[
                ["name", "rows", "uploaded_by", "upload_date"]
            ],
            use_container_width=True,
        )

    # -------------
    # summary per source
    # -------------
    st.markdown("#### 📊 Source Dependency Summary")

    total_by_source = df.groupby("uploaded_by").agg(
        {
            "dataset_id": "count",
            "rows": "sum",
        }
    ).rename(
        columns={
            "dataset_id": "dataset_count",
            "rows": "total_rows",
        }
    )

    st.dataframe(total_by_source, use_container_width=True)

# footer
st.markdown("---")
st.caption("📊 H.I.V.E. Data Lab – Research & Analytics Module")
