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
st.markdown(
    """
    Welcome to the **World Cup 2026** predictions game!

    The 2026 FIFA World Cup kicks off in **North America** with **48 teams** competing across **12 groups**.

    ### How to play
    1. **Register** or log in
    2. **Predict** the finishing order of all 12 groups
    3. **Pick** your tournament winner, finalist, semi-finalists and Golden Boot
    4. **Predictions lock** when the tournament kicks off — then watch your score climb!

    ### Scoring
    | Prediction | Points |
    |---|---|
    | Exact group position | 3 pts |
    | Correct group zone (top 2 or bottom 2) | 1 pt |
    | Correct tournament winner | 20 pts |
    | Correct finalist (runner-up) | 10 pts |
    | Correct semi-finalist | 5 pts each |
    | Correct Golden Boot | 10 pts |
    | **Maximum possible** | **194 pts** |

    > ⭐ **Bold Pick badge** — if your winner pick is chosen by fewer than 10% of players and they win, you earn the Contrarian badge!
    """
)

if not user:
    col1, col2 = st.columns(2)
    with col1:
        st.page_link("pages/1_Login.py", label="Login", icon="🔑")
    with col2:
        st.page_link("pages/2_Register.py", label="Register", icon="📝")
else:
    st.page_link("pages/4_Predictions.py", label="Make your predictions", icon="🎯")
