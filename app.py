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
1. **Register** and set up your profile (name + favourite player)
2. **Drag** teams into your predicted finishing order for all 12 groups
3. **Pick** your tournament winner, finalist, two semi-finalists & Golden Boot scorer
4. **Submit your hot take** — one bold pre-tournament prediction, sealed until kickoff
5. **Predictions lock** at tournament kickoff on June 11
6. **Pick match winners** round by round as R32 → R16 → QF → SF → Final open up
7. **React** to friends' hot takes and check the **Head to Head** page for trash-talk
8. Watch your score and rank on the live leaderboard!
        """
    )

with col_score:
    st.markdown("### Scoring")
    st.markdown(
        """
**Group stage** *(max 144 pts)*
| Prediction | Points |
|---|---|
| Exact finishing position | 3 pts |
| Right half — top 2 or bottom 2 | 1 pt |

**Pre-tournament picks** *(max 50 pts)*
| Prediction | Points |
|---|---|
| Tournament winner | 20 pts |
| Finalist (runner-up) | 10 pts |
| Each semi-finalist (×2) | 5 pts each |
| Golden Boot scorer | 10 pts |

**Round-by-round match picks** *(max 123 pts)*
| Round | Per correct pick |
|---|---|
| Round of 32 (16 games) | 2 pts |
| Round of 16 (8 games) | 4 pts |
| Quarter-finals (4 games) | 6 pts |
| Semi-finals (2 games) | 10 pts |
| Final (1 game) | 15 pts |

**Maximum possible: 317 pts**
        """
    )

with col_badges:
    st.markdown("### Badges")
    st.markdown(
        """
Badges are awarded automatically as results come in.

| Badge | How to earn |
|---|---|
| ⭐ Bold Pick | Your winner was picked by <10% of players |
| 🎯 Perfect Group | All 4 positions correct in a group *(stackable)* |
| 🔮 Oracle | Correct pre-tournament winner **and** finalist |
| 🐐 Golden Boot | Correct top scorer |
| 🏅 Top of the Table | Highest score after all group results are in |

Badges are shown on the leaderboard and the badge wall. The ▲/▼ column on the leaderboard shows how many places you moved after each score update.
        """
    )

st.divider()

st.markdown("### Features")
feat_col1, feat_col2 = st.columns(2)

with feat_col1:
    st.markdown(
        """
**🗂 Group Stage Predictions**
Drag teams into your predicted finishing order for all 12 groups. Save each group individually and edit any time before June 11 lockout.

**🏆 Pre-tournament Knockout Picks**
Pick your winner, finalist, two semi-finalists and Golden Boot scorer before the tournament starts. These are locked in at kickoff — bold calls rewarded.

**⚡ Round-by-Round Match Picks**
After each round's fixtures are confirmed, pick the winner of every match. Rounds open one at a time: R32 → R16 → QF → SF → Final. More points on the line each round.

**🔥 Hot Takes**
One bold pre-tournament prediction, sealed until kickoff. Post-lock they're all revealed — react with 🔥 😂 🤦 👏 and call out your mates.
        """
    )

with feat_col2:
    st.markdown(
        """
**🏟️ Leagues**
Create a private league and share a 6-character invite code with your friends. Each league has its own leaderboard — your predictions automatically count in every league you join.

**🏆 Live Leaderboard**
Pre-lock: submission progress. Post-lock: full scored table with ▲/▼ rank movers after every update, gold/silver/bronze highlights, and a badge column.

**📈 Score Timeline**
A line chart showing every player's cumulative score after each stage — watch the order change as the tournament progresses.

**⚔️ Head to Head**
Pick any player and see a full side-by-side breakdown — group predictions, knockout picks, match picks, and who's ahead by how much. Built for banter.
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
    cta1, cta2, cta3, cta4, cta5 = st.columns(5)
    with cta1:
        st.page_link("pages/4_Predictions.py", label="My predictions", icon="🎯")
    with cta2:
        st.page_link("pages/5_Leaderboard.py", label="Leaderboard", icon="🏆")
    with cta3:
        st.page_link("pages/10_Leagues.py", label="Leagues", icon="🏟️")
    with cta4:
        st.page_link("pages/8_Hot_Takes.py", label="Hot takes", icon="🔥")
    with cta5:
        st.page_link("pages/9_Head_to_Head.py", label="Head to head", icon="⚔️")
