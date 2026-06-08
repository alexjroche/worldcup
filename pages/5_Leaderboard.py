import streamlit as st
import pandas as pd
from components.auth import validate_session
from components.db import get_leaderboard, get_submission_counts
from components.lock import is_locked

st.set_page_config(page_title="Leaderboard — WC2026", page_icon="🏆", layout="wide")

validate_session()

st.title("🏆 Leaderboard")
locked = is_locked()

if not locked:
    st.info(
        "Predictions are still open — leaderboard shows submission progress only. "
        "Full scores will appear once the tournament is underway."
    )

    counts = get_submission_counts()
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
else:
    # Full scored leaderboard
    rows = get_leaderboard()

    if not rows:
        st.info("No scores yet — check back after the first results are entered.")
    else:
        table = []
        for i, row in enumerate(rows, 1):
            profile = row.get("profiles") or {}
            name = profile.get("display_name", "Unknown")
            fav = profile.get("favourite_player", "")
            badge = "⭐" if row.get("bold_pick") else ""
            table.append({
                "Rank": i,
                "Player": f"{name} {badge}".strip(),
                "Fav player": fav,
                "Groups": row.get("group_points", 0),
                "Winner": row.get("winner_points", 0),
                "Finalist": row.get("finalist_points", 0),
                "Semis": row.get("semi_points", 0),
                "Golden Boot": row.get("golden_boot_pts", 0),
                "Total": row.get("total_points", 0),
            })

        df = pd.DataFrame(table)

        # Highlight top 3
        def highlight_top(row):
            if row["Rank"] == 1:
                return ["background-color: #c9a84c; color: black"] * len(row)
            elif row["Rank"] == 2:
                return ["background-color: #888; color: black"] * len(row)
            elif row["Rank"] == 3:
                return ["background-color: #804a00; color: white"] * len(row)
            return [""] * len(row)

        styled = df.style.apply(highlight_top, axis=1)
        st.dataframe(styled, use_container_width=True, hide_index=True)
        st.caption("⭐ = Bold Pick badge (winner chosen by <10% of players)")
