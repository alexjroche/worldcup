from __future__ import annotations

import streamlit as st
from components.db import get_client, get_profile, upsert_profile, get_service_client


def _init_session() -> None:
    for key in ("user", "access_token", "profile"):
        st.session_state.setdefault(key, None)


def get_current_user() -> dict | None:
    _init_session()
    return st.session_state.get("user")


def get_current_profile() -> dict | None:
    _init_session()
    return st.session_state.get("profile")


def _load_profile(user_id: str) -> None:
    profile = get_profile(user_id)
    st.session_state["profile"] = profile


def validate_session() -> None:
    """Called on every page load. Verifies the stored JWT is still valid."""
    _init_session()
    token = st.session_state.get("access_token")
    if not token:
        return
    try:
        client = get_client()
        resp = client.auth.get_user(token)
        if resp and resp.user:
            st.session_state["user"] = resp.user
            if not st.session_state.get("profile"):
                _load_profile(resp.user.id)
        else:
            _clear_session()
    except Exception:
        _clear_session()


def _clear_session() -> None:
    st.session_state["user"] = None
    st.session_state["access_token"] = None
    st.session_state["profile"] = None


def login(email: str, password: str) -> str | None:
    """Returns error message string, or None on success."""
    try:
        client = get_client()
        resp = client.auth.sign_in_with_password({"email": email, "password": password})
        if resp.session:
            st.session_state["user"] = resp.user
            st.session_state["access_token"] = resp.session.access_token
            _load_profile(resp.user.id)
            return None
        return "Login failed. Check your email and password."
    except Exception as e:
        return str(e)


def register(email: str, password: str, display_name: str, favourite_player: str) -> str | None:
    """Returns error message string, or None on success."""
    try:
        client = get_client()
        # Pass profile fields as user metadata so the DB trigger can create the
        # profile row with SECURITY DEFINER (bypassing RLS on first insert).
        resp = client.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "display_name": display_name,
                    "favourite_player": favourite_player,
                }
            },
        })
        if resp.user:
            if resp.session:
                st.session_state["user"] = resp.user
                st.session_state["access_token"] = resp.session.access_token
                # Trigger creates the row but may not set these fields correctly,
                # so write them explicitly with the service client.
                get_service_client().table("profiles").upsert({
                    "id": resp.user.id,
                    "display_name": display_name,
                    "favourite_player": favourite_player,
                }).execute()
                _load_profile(resp.user.id)
            return None
        return "Registration failed. Try a different email."
    except Exception as e:
        return str(e)


def logout() -> None:
    try:
        get_client().auth.sign_out()
    except Exception:
        pass
    _clear_session()


def require_auth() -> bool:
    """Returns True if user is logged in. Shows login prompt and returns False if not."""
    validate_session()
    if not get_current_user():
        st.warning("Please log in to access this page.")
        st.page_link("pages/1_Login.py", label="Go to Login")
        return False
    return True


def require_admin() -> bool:
    """Returns True if user is logged in and is an admin."""
    if not require_auth():
        return False
    profile = get_current_profile()
    if not profile or not profile.get("is_admin"):
        st.error("You don't have permission to access this page.")
        return False
    return True
