import streamlit as st
from collections import defaultdict
from components.auth import validate_session, get_current_user
from components.db import get_hot_take, save_hot_take, get_all_hot_takes, get_all_reactions, toggle_reaction
from components.lock import is_locked, time_until_lock

st.set_page_config(page_title="Hot Takes — WC2026", page_icon="🔥", layout="centered")

validate_session()

st.title("🔥 Hot Takes")

locked = is_locked()
user = get_current_user()

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
# Submit / edit (pre-lock)
# ---------------------------------------------------------------------------
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
            if st.form_submit_button("Save hot take", use_container_width=True):
                if not take_text.strip():
                    st.error("Hot take can't be empty!")
                else:
                    save_hot_take(user.id, take_text.strip())
                    st.success("Hot take saved — revealed at kickoff!")
    st.stop()

# ---------------------------------------------------------------------------
# Reveal wall (post-lock)
# ---------------------------------------------------------------------------
takes = get_all_hot_takes()

if not takes:
    st.info("Nobody submitted a hot take — shy bunch!")
    if user and not get_hot_take(user.id):
        st.caption("You didn't submit one before the deadline — better luck next tournament!")
    st.stop()

# Pre-load all reactions into a lookup: {take_id: {emoji: count}}
all_reactions = get_all_reactions()
reaction_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
user_reactions: dict[str, set[str]] = defaultdict(set)

for r in all_reactions:
    tid = r["hot_take_id"]
    emoji = r["emoji"]
    reaction_counts[tid][emoji] += 1
    if user and r["user_id"] == user.id:
        user_reactions[tid].add(emoji)

EMOJIS = ["🔥", "😂", "🤦", "👏"]

st.markdown(f"**{len(takes)} hot take(s):**")

for t in takes:
    tid = t["id"]
    profile = t.get("profiles") or {}
    name = profile.get("display_name", "Anonymous")
    fav = profile.get("favourite_player", "")
    byline = f"— **{name}**"
    if fav:
        byline += f" *(fan of {fav})*"

    st.markdown(
        f"""
        <div style="
            background: #1e2d3d;
            border-left: 4px solid #c9a84c;
            border-radius: 6px;
            padding: 14px 18px;
            margin-bottom: 6px;
        ">
            <div style="font-size: 1.1em; font-style: italic;">"{t['take']}"</div>
            <div style="font-size: 0.85em; color: #aaa; margin-top: 8px;">{byline}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Reaction buttons
    r_cols = st.columns(len(EMOJIS))
    for col, emoji in zip(r_cols, EMOJIS):
        count = reaction_counts[tid][emoji]
        already = emoji in user_reactions[tid]
        label = f"{emoji} {count}" if count else emoji
        # Highlight if user already reacted
        btn_type = "primary" if already else "secondary"
        with col:
            if user:
                if st.button(label, key=f"react_{tid}_{emoji}", type=btn_type, use_container_width=True):
                    toggle_reaction(user.id, tid, emoji)
                    st.rerun()
            else:
                st.button(label, key=f"react_{tid}_{emoji}_anon", disabled=True, use_container_width=True)

    st.markdown("")

if not user:
    st.caption("Log in to react to hot takes.")
