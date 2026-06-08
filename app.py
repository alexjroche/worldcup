import streamlit as st
from components.auth import validate_session, get_current_user, get_current_profile, logout
from components.lock import is_locked, time_until_lock

st.set_page_config(
    page_title="World Cup 2026 Predictions",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

validate_session()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## ⚽ WC2026 Predictions")

    locked = is_locked()
    if locked:
        st.error("🔒 Predictions are locked!")
    else:
        st.info(f"⏳ {time_until_lock()}")

    st.divider()

    user = get_current_user()
    profile = get_current_profile()

    if user and profile:
        st.markdown(f"**{profile.get('display_name', 'Player')}**")
        if profile.get("favourite_player"):
            st.caption(f"Fav: {profile['favourite_player']}")
        if st.button("Logout", use_container_width=True):
            logout()
            st.rerun()
    else:
        st.page_link("pages/1_Login.py", label="Login", icon="🔑")
        st.page_link("pages/2_Register.py", label="Register", icon="📝")

# ---------------------------------------------------------------------------
# Home page
# ---------------------------------------------------------------------------
st.title("⚽ World Cup 2026 Predictions")
st.markdown("The **2026 FIFA World Cup** — 48 teams, 12 groups, one winner. Make your picks before June 11.")

st.divider()

col_how, col_score, col_badges = st.columns(3)

with col_how:
    st.markdown("### How to play")
    st.markdown(
        """
1. **Register** and set up your profile
2. **Drag** teams into your predicted group finishing order
3. **Pick** your tournament winner, finalist, semi-finalists & Golden Boot scorer
4. **Submit your hot take** — a bold pre-tournament prediction, sealed until kickoff
5. **Predictions lock** at kickoff on June 11
6. **Pick match winners** each round as the knockout stages open
7. Watch your score climb on the leaderboard!
        """
    )

with col_score:
    st.markdown("### Scoring")
    st.markdown(
        """
| Prediction | Points |
|---|---|
| Exact group position | 3 pts |
| Correct group zone | 1 pt |
| Tournament winner | 20 pts |
| Finalist | 10 pts |
| Semi-finalist | 5 pts each |
| Golden Boot | 10 pts |
| R32 match pick | 2 pts |
| R16 match pick | 4 pts |
| QF match pick | 6 pts |
| SF match pick | 10 pts |
| Final match pick | 15 pts |
| **Maximum possible** | **317 pts** |
        """
    )

with col_badges:
    st.markdown("### Badges")
    st.markdown(
        """
| Badge | How to earn |
|---|---|
| ⭐ Bold Pick | Pick a winner chosen by <10% of players |
| 🎯 Perfect Group | All 4 positions correct in a group |
| 🔮 Oracle | Correct winner **and** finalist |
| 🐐 Golden Boot | Correct top scorer |
| 🏅 Top of the Table | Leading after the group stage |
        """
    )

st.divider()

st.markdown("### Features")
feat_col1, feat_col2 = st.columns(2)

with feat_col1:
    st.markdown(
        """
**🗂 Group Stage Predictions**
Drag and drop all 12 groups into your predicted finishing order. Save each group individually — come back and edit before lockout.

**⚡ Round-by-Round Match Picks**
After each knockout round draws its matchups, pick the winner of every game. R32 opens after the group stage, then R16, QF, SF and the Final — each unlocked by the admin as real fixtures are confirmed.

**🔥 Hot Takes**
Submit one bold pre-tournament prediction before June 11. Every hot take is sealed until lockout — then they're all revealed on the Hot Takes wall.
        """
    )

with feat_col2:
    st.markdown(
        """
**🏆 Live Leaderboard**
Before lockout: see who's submitted their predictions. After lockout: full points table with a score breakdown per category and gold/silver/bronze row highlighting.

**📈 Score Timeline**
A live line chart showing every player's cumulative points after each stage — watch yourself overtake (or get overtaken) as the tournament progresses.

**🏅 Badge Wall**
Earn badges as results come in. The badge wall on the leaderboard page shows every player's achievements at a glance.
        """
    )

st.divider()

# CTA buttons
if not user:
    col1, col2 = st.columns(2)
    with col1:
        st.page_link("pages/2_Register.py", label="Register to play", icon="📝")
    with col2:
        st.page_link("pages/1_Login.py", label="Login", icon="🔑")
else:
    cta1, cta2, cta3 = st.columns(3)
    with cta1:
        st.page_link("pages/4_Predictions.py", label="My predictions", icon="🎯")
    with cta2:
        st.page_link("pages/5_Leaderboard.py", label="Leaderboard", icon="🏆")
    with cta3:
        st.page_link("pages/8_Hot_Takes.py", label="Hot takes", icon="🔥")
