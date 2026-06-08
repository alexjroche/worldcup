import streamlit as st
import pandas as pd
import altair as alt
from components.auth import validate_session, get_current_user
from components.db import get_leaderboard, get_submission_counts, get_score_snapshots, get_user_leagues
from components.lock import is_locked

st.set_page_config(page_title="Leaderboard — WC2026", page_icon="🏆", layout="wide")

validate_session()
current_user = get_current_user()

st.title("🏆 Leaderboard")
locked = is_locked()

# ---------------------------------------------------------------------------
# League selector (shown if user is in any leagues)
# ---------------------------------------------------------------------------
league_id: str | None = None
if current_user:
    my_leagues = get_user_leagues(current_user.id)
    if my_leagues:
        options = ["🌍 All players"] + [l["name"] for l in my_leagues]
        sel = st.selectbox("Viewing", options, key="lb_league_sel")
        if sel != "🌍 All players":
            chosen = next(l for l in my_leagues if l["name"] == sel)
            league_id = chosen["id"]
        if league_id:
            st.caption(f"Showing only members of **{sel}**. Switch to 'All players' to see the global leaderboard.")

# ---------------------------------------------------------------------------
# Pre-lock: submission progress only
# ---------------------------------------------------------------------------
if not locked:
    st.info(
        "Predictions are still open — leaderboard shows submission progress only. "
        "Full scores will appear once the tournament is underway."
    )
    counts = get_submission_counts(league_id=league_id)
    if not counts:
        st.markdown("No players have registered yet — be the first!")
    else:
        df = pd.DataFrame(counts)
        df["knockout"] = df["knockout_submitted"].map({True: "✅", False: "❌"})
        df = df.rename(columns={
            "display_name": "Player",
            "favourite_player": "Fav player",
            "groups_submitted": "Groups (of 12)",
            "knockout": "Knockout picks",
        })[["Player", "Fav player", "Groups (of 12)", "Knockout picks"]]
        st.dataframe(df, use_container_width=True, hide_index=True)
    st.stop()

# ---------------------------------------------------------------------------
# Post-lock: full scored leaderboard
# ---------------------------------------------------------------------------
rows = get_leaderboard(league_id=league_id)

if not rows:
    st.info("No scores yet — check back after the first results are entered.")
    st.stop()

# Build badge strings
BADGE_DEFS = [
    ("bold_pick",           "⭐", "Bold Pick — winner chosen by <10% of players"),
    ("badge_oracle",        "🔮", "Oracle — correct winner AND finalist"),
    ("badge_golden_boot_win","🐐", "Golden Boot — correct top scorer"),
    ("badge_top_of_table",  "🏅", "Top of the Table — leading after group stage"),
]

current_uid = current_user.id if current_user else None

table = []
for i, row in enumerate(rows, 1):
    profile = row.get("profiles") or {}
    name = profile.get("display_name", "Unknown")
    fav = profile.get("favourite_player", "")
    perfect = row.get("badge_perfect_groups", 0)

    badges = "".join(emoji for field, emoji, _ in BADGE_DEFS if row.get(field))
    if perfect:
        badges += "🎯" * perfect

    prev = row.get("prev_rank")
    if prev and prev != i:
        delta = prev - i
        mover = f"▲{delta}" if delta > 0 else f"▼{abs(delta)}"
    else:
        mover = "—"

    you = " 👈" if row.get("user_id") == current_uid else ""
    table.append({
        "Rank": i,
        "+/-": mover,
        "Player": f"{name}{you}",
        "Badges": badges,
        "Fav player": fav,
        "Groups": row.get("group_points", 0),
        "Pre-KO": row.get("winner_points", 0) + row.get("finalist_points", 0) + row.get("semi_points", 0) + row.get("golden_boot_pts", 0),
        "Match Picks": row.get("round_points", 0),
        "Total": row.get("total_points", 0),
    })

df = pd.DataFrame(table)

def highlight_top(r):
    if r["Rank"] == 1:
        return ["background-color: #c9a84c; color: black"] * len(r)
    elif r["Rank"] == 2:
        return ["background-color: #888; color: black"] * len(r)
    elif r["Rank"] == 3:
        return ["background-color: #804a00; color: white"] * len(r)
    return [""] * len(r)

st.dataframe(df.style.apply(highlight_top, axis=1), use_container_width=True, hide_index=True)

# Badge legend
with st.expander("Badge guide"):
    for _, emoji, desc in BADGE_DEFS:
        st.markdown(f"{emoji} {desc}")
    st.markdown("🎯 Perfect Group — all 4 positions correct in a group (one per group)")

st.divider()

# ---------------------------------------------------------------------------
# Score timeline chart
# ---------------------------------------------------------------------------
st.subheader("📈 Score timeline")

snapshots = get_score_snapshots()
if not snapshots:
    st.info("Timeline will appear once scores have been calculated at least twice.")
else:
    df_snap = pd.DataFrame([
        {
            "Snapshot": s["snapshot_label"],
            "Player": (s.get("profiles") or {}).get("display_name", "Unknown"),
            "Points": s["total_points"],
            "created_at": s["created_at"],
        }
        for s in snapshots
    ])

    # Sort snapshot labels by first appearance time
    label_order = df_snap.drop_duplicates("Snapshot").sort_values("created_at")["Snapshot"].tolist()

    chart = (
        alt.Chart(df_snap)
        .mark_line(point=True)
        .encode(
            x=alt.X("Snapshot:O", sort=label_order, title="Stage"),
            y=alt.Y("Points:Q", title="Total points"),
            color=alt.Color("Player:N", legend=alt.Legend(title="Player")),
            tooltip=["Player", "Snapshot", "Points"],
        )
        .properties(height=380)
        .interactive()
    )
    st.altair_chart(chart, use_container_width=True)

st.divider()

# ---------------------------------------------------------------------------
# Badge wall
# ---------------------------------------------------------------------------
st.subheader("🏅 Badge wall")

badge_rows = []
for row in rows:
    profile = row.get("profiles") or {}
    name = profile.get("display_name", "Unknown")
    earned = []
    for field, emoji, desc in BADGE_DEFS:
        if row.get(field):
            earned.append(f"{emoji} {desc.split(' — ')[0]}")
    perfect = row.get("badge_perfect_groups", 0)
    for _ in range(perfect):
        earned.append("🎯 Perfect Group")
    if earned:
        badge_rows.append({"Player": name, "Badges": "  ·  ".join(earned)})

if badge_rows:
    st.dataframe(pd.DataFrame(badge_rows), use_container_width=True, hide_index=True)
else:
    st.info("No badges awarded yet — they unlock as results come in.")
