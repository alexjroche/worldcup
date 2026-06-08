import streamlit as st
from components.auth import login, get_current_user, validate_session

st.set_page_config(page_title="Login — WC2026", page_icon="🔑", layout="centered")

validate_session()
if get_current_user():
    st.switch_page("app.py")

st.title("🔑 Login")
st.markdown("Welcome back! Enter your credentials to access your predictions.")

with st.form("login_form"):
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Login", use_container_width=True)

if submitted:
    if not email or not password:
        st.error("Please fill in all fields.")
    else:
        with st.spinner("Logging in..."):
            err = login(email.strip(), password)
        if err:
            st.error(f"Login failed: {err}")
        else:
            st.success("Logged in!")
            st.switch_page("pages/4_Predictions.py")

st.divider()
st.markdown("Don't have an account?")
st.page_link("pages/2_Register.py", label="Register here", icon="📝")
