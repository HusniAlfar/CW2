import streamlit as st
from hive_database.connection import setup_database
from authentication.security import (
    validate_username,
    validate_password,
    register_user,
    login_user,
)

st.set_page_config(
    page_title="HIVE Access Portal",
    page_icon="🐝",
    layout="wide"
)

# Run database setup one time at start
setup_database()

# Session state setup

# Here we keep information about the current user
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = None

if "role" not in st.session_state:
    st.session_state.role = None


def show_login_page():
    """
    Show the login and register screen.

    This is the front page for the H.I.V.E. system.
    """

    # We use three columns to center the content
    left_col, center_col, right_col = st.columns([1, 2, 1])

    with center_col:
        # H.I.V.E. logo (put hive_logo.png in the same folder)
        st.image("hive_logo.png", width=150)

        # Main title and subtitle
        st.title(" HIVE Access Portal")
        st.markdown("### We Exist As One Organism. As you might say a hive.")
        st.markdown("---")

        # Two tabs: Login and Register
        login_tab, register_tab = st.tabs([" Login", " Register"])

        # LOGIN TAB
        with login_tab:
            # Form for login
            with st.form("login_form"):
                login_username = st.text_input(
                    "Username",
                    placeholder="Enter your H.I.V.E. ID"
                )
                login_password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your secret key"
                )

                login_button = st.form_submit_button(
                    " Access H.I.V.E.",
                    use_container_width=True
                )

                if login_button:
                    # Check empty fields
                    if not login_username or not login_password:
                        st.error("⚠️ Please fill in all fields")
                    else:
                        # Try to log in the user
                        success, result = login_user(login_username, login_password)

                        if success:
                            # Save user info in session
                            st.session_state.logged_in = True
                            st.session_state.username = result["username"]
                            st.session_state.role = result["role"]

                            st.success(f"✅ Welcome back, Agent {login_username}.")
                            st.rerun()
                        else:
                            # result here is an error message string
                            st.error(f"❌ {result}")

        #REGISTER TAB
        with register_tab:
            # Form for new account
            with st.form("register_form"):
                reg_username = st.text_input(
                    "Choose Username",
                    key="reg_user",
                    placeholder="Pick your H.I.V.E. codename",
                    help="3–20 letters or numbers"
                )

                reg_password = st.text_input(
                    "Password",
                    type="password",
                    key="reg_pass",
                    placeholder="Create a strong password",
                    help="At least 6 chars, with uppercase, lowercase and number"
                )

                reg_confirm = st.text_input(
                    "Confirm Password",
                    type="password",
                    placeholder="Repeat your password"
                )

                reg_role = st.selectbox(
                    "Select Your H.I.V.E. Role",
                    ["agent", "cyber_analyst", "data_scientist", "it_overseer"],
                    help="Pick the role that fits your mission"
                )

                register_button = st.form_submit_button(
                    "✨ Join H.I.V.E.",
                    use_container_width=True
                )

                if register_button:
                    # Check if any field is empty
                    if not reg_username or not reg_password or not reg_confirm:
                        st.error("⚠️ Please fill in all fields")
                    elif reg_password != reg_confirm:
                        st.error("❌ Passwords do not match")
                    else:
                        # First check username rules
                        username_ok, user_msg = validate_username(reg_username)
                        if not username_ok:
                            st.error(f"❌ {user_msg}")
                        else:
                            # Then check password rules
                            password_ok, pass_msg = validate_password(reg_password)
                            if not password_ok:
                                st.error(f"❌ {pass_msg}")
                            else:
                                # Try to create the new user
                                created, result = register_user(
                                    reg_username,
                                    reg_password,
                                    reg_role
                                )

                                if created:
                                    st.success("✅ Registration complete! You can now log in.")
                                else:
                                    # result is an error text like "Username already exists"
                                    st.error(f"❌ {result}")


def main():
    """
    Main app controller.

    If user is not logged in -> show login page.
    If user is logged in -> send them to dashboard page.
    """
    if not st.session_state.logged_in:
        show_login_page()
    else:
        # Go to the main H.I.V.E. dashboard
        # Make sure you have pages/dash.py in your Streamlit project
        st.switch_page("pages/dash.py")


# Run the app
if __name__ == "__main__":
    main()
