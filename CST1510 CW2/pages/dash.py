import streamlit as st
# Page configuration
st.set_page_config(
    page_title="H.I.V.E.",
    page_icon="🐝",
    layout="wide",
)

# Login check
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("⚠️ Please login first to access the H.I.V.E. dashboard.")
    st.stop()

# Sidebar navigation
st.sidebar.title("H.I.V.E. Guide")
st.sidebar.markdown("---")
st.sidebar.write(f"**Agent:** {st.session_state.username}")
st.sidebar.write(f"**Role:** {st.session_state.role}")
st.sidebar.markdown("---")

st.sidebar.page_link("pages/cybersecurity.py", label=" CyberSecurity", )
st.sidebar.page_link("pages/data_science.py", label=" Data Science", )
st.sidebar.page_link("pages/it_tickets.py", label=" IT tickets",)

st.sidebar.markdown("---")

if st.sidebar.button(" Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.switch_page("login.py")

# -----------------------------
# MAIN CONTENT
# -----------------------------
st.title("H.I.V.E. Home Page")
st.markdown(
    """
Welcome to **H.I.V.E.**, .
"""
)

role = st.session_state.role

# =======================
# Agent – vertical layout
# =======================
if role == "agent":
    st.subheader("Agent Overview")
    st.write("You have access to all three domains in H.I.V.E.")

    # --- Cyber Cell (block 1) ---
    st.markdown("### Cyber Security")
    st.write("View and analyse cybersecurity incidents.")
    if st.button("Go to Cyber Security", key="btn_cyber", use_container_width=True):
        st.switch_page("pages/cybersecurity.py")

    st.markdown("---")

    # --- Data Lab (block 2) ---
    st.markdown("###  Data Science")
    st.write("Explore datasets and their statistics.")
    if st.button("Go to Data Science", key="btn_data", use_container_width=True):
        st.switch_page("pages/data_science.py")

    st.markdown("---")

    # --- Tech Cell (block 3) ---
    st.markdown("###  It tickets")
    st.write("Track IT tickets and operations health.")
    if st.button("Go to IT tickets", key="btn_it", use_container_width=True):
        st.switch_page("pages/it_tickets.py")

# =======================
# Other roles
# =======================
elif role == "cyber_analyst":
    st.subheader("Cyber Cell Access")
    st.write("You are focused on cybersecurity operations.")
    if st.button("Open Cyber Cell Dashboard", use_container_width=True):
        st.switch_page("pages/cybersecurity.py")

elif role == "data_scientist":
    st.subheader("Data Lab Access")
    st.write("You are responsible for dataset management and analytics.")
    if st.button("Open Data Lab Dashboard", use_container_width=True):
        st.switch_page("pages/data_science.py")

elif role == "it_overseer":
    st.subheader("Tech Cell Access")
    st.write("You manage IT operations and ticket performance.")
    if st.button("Open Tech Cell Dashboard", use_container_width=True):
        st.switch_page("pages/it_tickets.py")

st.markdown("---")
st.caption("H.I.V.E. Nexus – Central Command Dashboard")
