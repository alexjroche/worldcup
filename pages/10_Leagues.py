import streamlit as st
from components.auth import require_auth, get_current_user
from components.db import (
    create_league, get_league_by_code, join_league,
    leave_league, get_user_leagues,
)

st.set_page_config(page_title="Leagues — WC2026", page_icon="🏟️", layout="centered")

if not require_auth():
    st.stop()

user = get_current_user()
uid = user.id

st.title("🏟️ Leagues")
st.markdown(
    "Create a private league with friends or join one using an invite code. "
    "Each league has its own leaderboard — your predictions count in every league you're in."
)

# ---------------------------------------------------------------------------
# User's current leagues
# ---------------------------------------------------------------------------
my_leagues = get_user_leagues(uid)

if my_leagues:
    st.subheader("Your leagues")
    for league in my_leagues:
        with st.container(border=True):
            col_name, col_code, col_meta, col_action = st.columns([3, 2, 1, 1])
            with col_name:
                st.markdown(f"**{league['name']}**")
                if league.get("created_by") == uid:
                    st.caption("Created by you")
            with col_code:
                st.markdown("Invite code")
                st.code(league["invite_code"], language=None)
            with col_meta:
                count = league.get("member_count", 0)
                st.metric("Members", count)
            with col_action:
                st.markdown("&nbsp;", unsafe_allow_html=True)
                if st.button("Leave", key=f"leave_{league['id']}", type="secondary", use_container_width=True):
                    leave_league(uid, league["id"])
                    st.rerun()
else:
    st.info("You're not in any leagues yet — create one below or join with a code.")

st.divider()

# ---------------------------------------------------------------------------
# Create / Join forms
# ---------------------------------------------------------------------------
col_create, col_join = st.columns(2)

with col_create:
    st.subheader("Create a league")
    st.caption("Pick a name — you'll get a 6-character code to share with your group.")
    with st.form("create_league_form"):
        league_name = st.text_input("League name", placeholder="e.g. The Wolf Pack", max_chars=50)
        submitted = st.form_submit_button("Create league", use_container_width=True, type="primary")
        if submitted:
            if not league_name.strip():
                st.error("Enter a name for your league.")
            else:
                league = create_league(uid, league_name.strip())
                st.success(f"League created!")
                st.info(f"Invite code: **{league['invite_code']}**  \nShare this with your friends so they can join.")
                st.rerun()

with col_join:
    st.subheader("Join a league")
    st.caption("Enter the 6-character code you received from a friend.")
    with st.form("join_league_form"):
        code_input = st.text_input("Invite code", placeholder="e.g. WOLF42", max_chars=6)
        submitted = st.form_submit_button("Join league", use_container_width=True, type="primary")
        if submitted:
            if not code_input.strip():
                st.error("Enter an invite code.")
            else:
                league = get_league_by_code(code_input.strip().upper())
                if not league:
                    st.error("No league found with that code. Check the code and try again.")
                else:
                    # Check if already a member
                    already = any(l["id"] == league["id"] for l in my_leagues)
                    if already:
                        st.info(f"You're already in **{league['name']}**.")
                    else:
                        join_league(uid, league["id"])
                        st.success(f"Joined **{league['name']}**!")
                        st.rerun()

st.divider()

st.caption(
    "Your predictions and scores are the same regardless of which leagues you're in — "
    "leagues just filter who you compete against on the leaderboard."
)
