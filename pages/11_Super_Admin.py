import streamlit as st
import pandas as pd
from components.auth import require_admin
from components.db import (
    admin_get_user_emails,
    admin_get_prediction_coverage,
    admin_get_all_leagues,
    admin_get_all_hot_takes,
    get_leaderboard,
)

st.set_page_config(page_title="Super Admin — WC2026", page_icon="🔐", layout="wide")

if not require_admin():
    st.stop()

st.title("🔐 Super Admin")
st.caption("Full visibility across all players, leagues, and predictions.")

tab_players, tab_leagues, tab_takes = st.tabs(["👥 Players", "🏟️ Leagues", "🔥 Hot Takes"])

# ===========================================================================
# PLAYERS
# ===========================================================================
with tab_players:
    st.subheader("All players")

    coverage = admin_get_prediction_coverage()
    emails = admin_get_user_emails()
    scores_rows = get_leaderboard()  # sorted by total_points desc
    scores_map = {r["user_id"]: r for r in scores_rows}

    rows = []
    for i, row in enumerate(
        sorted(scores_rows, key=lambda r: r.get("total_points", 0), reverse=True), 1
    ):
        uid = row["user_id"]
        cov = next((c for c in coverage if c["user_id"] == uid), {})
        profile = row.get("profiles") or {}

        badges = ""
        if row.get("bold_pick"):        badges += "⭐"
        if row.get("badge_oracle"):     badges += "🔮"
        if row.get("badge_golden_boot_win"): badges += "🐐"
        if row.get("badge_top_of_table"):    badges += "🏅"
        perfect = row.get("badge_perfect_groups", 0)
        if perfect:
            badges += "🎯" * perfect

        awards = (
            ("⚽" if cov.get("boot_done")  else "·") +
            ("🏅" if cov.get("ball_done")  else "·") +
            ("🧤" if cov.get("glove_done") else "·")
        )

        rows.append({
            "Rank":         i,
            "Name":         profile.get("display_name", "—"),
            "Email":        emails.get(uid, "—"),
            "Fav player":   profile.get("favourite_player", "—"),
            "Groups":       f"{cov.get('groups_done', 0)}/12",
            "KO picks":     "✅" if cov.get("ko_done") else "❌",
            "Awards":       awards,
            "Badges":       badges,
            "Group pts":    row.get("group_points", 0),
            "KO pts":       (
                row.get("winner_points", 0) + row.get("finalist_points", 0) +
                row.get("semi_points", 0) + row.get("golden_boot_pts", 0) +
                row.get("golden_ball_pts", 0) + row.get("golden_glove_pts", 0)
            ),
            "Round pts":    row.get("round_points", 0),
            "Total":        row.get("total_points", 0),
        })

    # Also include players who registered but have no score row yet
    scored_uids = {r["user_id"] for r in scores_rows}
    for cov in coverage:
        uid = cov["user_id"]
        if uid not in scored_uids:
            rows.append({
                "Rank": "—",
                "Name": cov["display_name"],
                "Email": emails.get(uid, "—"),
                "Fav player": cov.get("favourite_player", "—"),
                "Groups": f"{cov.get('groups_done', 0)}/12",
                "KO picks": "✅" if cov.get("ko_done") else "❌",
                "Awards": (
                    ("⚽" if cov.get("boot_done")  else "·") +
                    ("🏅" if cov.get("ball_done")  else "·") +
                    ("🧤" if cov.get("glove_done") else "·")
                ),
                "Badges": "",
                "Group pts": 0, "KO pts": 0, "Round pts": 0, "Total": 0,
            })

    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(f"{len(rows)} registered player(s)")
    else:
        st.info("No players registered yet.")

# ===========================================================================
# LEAGUES
# ===========================================================================
with tab_leagues:
    st.subheader("All leagues")

    leagues = admin_get_all_leagues()

    if not leagues:
        st.info("No leagues created yet.")
    else:
        for league in leagues:
            members = league.get("league_members") or []
            wagering = [
                (m.get("profiles") or {}).get("display_name", "—")
                for m in members if m.get("wager_in")
            ]
            fun_only = [
                (m.get("profiles") or {}).get("display_name", "—")
                for m in members if not m.get("wager_in")
            ]
            with st.container(border=True):
                col_name, col_code, col_count, col_wager, col_fun = st.columns([2, 1, 1, 3, 3])
                with col_name:
                    st.markdown(f"**{league['name']}**")
                with col_code:
                    st.code(league["invite_code"], language=None)
                with col_count:
                    st.metric("Members", len(members))
                with col_wager:
                    st.markdown(f"**💰 Wagering ({len(wagering)})**")
                    st.markdown(", ".join(wagering) if wagering else "—")
                with col_fun:
                    st.markdown(f"**🎮 Just for fun ({len(fun_only)})**")
                    st.markdown(", ".join(fun_only) if fun_only else "—")

        st.caption(f"{len(leagues)} league(s) total")

# ===========================================================================
# HOT TAKES (admin sees all, pre- and post-lock)
# ===========================================================================
with tab_takes:
    st.subheader("All hot takes")
    st.caption("Visible to admin regardless of lock status.")

    takes = admin_get_all_hot_takes()

    if not takes:
        st.info("No hot takes submitted yet.")
    else:
        rows = []
        for t in takes:
            profile = t.get("profiles") or {}
            rows.append({
                "Player": profile.get("display_name", "—"),
                "Hot take": t["take"],
                "Submitted": t.get("created_at", "")[:16].replace("T", " "),
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.caption(f"{len(takes)} hot take(s)")
