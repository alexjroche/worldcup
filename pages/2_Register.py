import streamlit as st
from components.auth import register, get_current_user, validate_session

st.set_page_config(page_title="Register — WC2026", page_icon="📝", layout="centered")

validate_session()
if get_current_user():
    st.switch_page("app.py")

st.title("📝 Register")
st.markdown("Join the predictions game — pick your winner before June 11!")

with st.form("register_form"):
    display_name = st.text_input("Your name (shown on leaderboard)", placeholder="e.g. Alex")
    favourite_player = st.text_input("Favourite player", placeholder="e.g. Lionel Messi")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    password2 = st.text_input("Confirm password", type="password")
    submitted = st.form_submit_button("Create account", use_container_width=True)

if submitted:
    if not all([display_name, email, password, password2]):
        st.error("Please fill in all required fields.")
    elif password != password2:
        st.error("Passwords don't match.")
    elif len(password) < 6:
        st.error("Password must be at least 6 characters.")
    else:
        with st.spinner("Creating your account..."):
            err = register(email.strip(), password, display_name.strip(), favourite_player.strip())
        if err:
            st.error(f"Registration failed: {err}")
        else:
            st.success("Account created! Let's make some predictions.")
            st.switch_page("pages/4_Predictions.py")

st.divider()
st.markdown("Already have an account?")
st.page_link("pages/1_Login.py", label="Login here", icon="🔑")
