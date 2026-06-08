import streamlit as st
from components.auth import validate_session, get_current_user, require_auth
from components.db import get_hot_take, save_hot_take, get_all_hot_takes
from components.lock import is_locked, time_until_lock

st.set_page_config(page_title="Hot Takes — WC2026", page_icon="🔥", layout="centered")

validate_session()

st.title("🔥 Hot Takes")

locked = is_locked()

if not locked:
    st.markdown(
        "Submit your boldest prediction before the tournament starts. "
        "All hot takes are **sealed until kickoff** — no copying!\n\n"
        f"*{time_until_lock()}*"
    )
else:
    st.markdown("Predictions are locked — the hot takes are revealed! 🎉")

st.divider()

# ---------------------------------------------------------------------------
# Submit / edit your own hot take (pre-lock)
# ---------------------------------------------------------------------------
user = get_current_user()

if not locked:
    if not user:
        st.info("Log in to submit your hot take.")
        st.page_link("pages/1_Login.py", label="Login", icon="🔑")
    else:
        existing = get_hot_take(user.id)
        st.subheader("Your hot take")
        st.caption("One bold, spicy prediction. Could be a result, a player, a shock — anything.")

        with st.form("hot_take_form"):
            take_text = st.text_area(
                "Your prediction",
                value=existing or "",
                placeholder='e.g. "Germany wins it, Mbappé doesn\'t score a single goal"',
                max_chars=280,
                height=100,
            )
            submitted = st.form_submit_button("Save hot take", use_container_width=True)

        if submitted:
            if not take_text.strip():
                st.error("Hot take can't be empty!")
            else:
                save_hot_take(user.id, take_text.strip())
                st.success("Hot take saved — revealed at kickoff!")

# ---------------------------------------------------------------------------
# Reveal wall (post-lock)
# ---------------------------------------------------------------------------
else:
    takes = get_all_hot_takes()

    if not takes:
        st.info("Nobody submitted a hot take — shy bunch!")
    else:
        st.markdown(f"**{len(takes)} hot take(s) submitted:**")
        st.markdown("")

        for t in takes:
            profile = t.get("profiles") or {}
            name = profile.get("display_name", "Anonymous")
            fav = profile.get("favourite_player", "")
            caption = f"— **{name}**"
            if fav:
                caption += f" *(fan of {fav})*"

            st.markdown(
                f"""
                <div style="
                    background: #1e2d3d;
                    border-left: 4px solid #c9a84c;
                    border-radius: 6px;
                    padding: 14px 18px;
                    margin-bottom: 12px;
                ">
                    <div style="font-size: 1.1em; font-style: italic;">"{t['take']}"</div>
                    <div style="font-size: 0.85em; color: #aaa; margin-top: 8px;">{caption}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Also let logged-in users submit post-lock if they missed the window — no, keep sealed.
    if user:
        my_take = get_hot_take(user.id)
        if not my_take:
            st.info("You didn't submit a hot take before the deadline — better luck next tournament!")
