import streamlit as st
import pandas as pd
from components.auth import validate_session
from components.db import get_winner_distribution, get_finalist_distribution, get_service_client
from components.lock import is_locked
from data.teams import GROUPS

st.set_page_config(page_title="Prediction Stats — WC2026", page_icon="📊", layout="wide")

validate_session()

st.title("📊 Prediction Stats")
locked = is_locked()

if not locked:
    st.warning("Stats are hidden until predictions lock on June 11 — no copying!")
    st.stop()

st.markdown("See what everyone predicted before the tournament started.")

# ---------------------------------------------------------------------------
# Winner distribution
# ---------------------------------------------------------------------------
st.subheader("Who did players pick to win?")

winner_dist = get_winner_distribution()
if not winner_dist:
    st.info("No winner predictions yet.")
else:
    df_w = pd.DataFrame(winner_dist)
    total = df_w["count"].sum()
    st.caption(f"Based on {total} prediction(s)")

    # Mark bold picks (<10%)
    df_w["bold"] = df_w["pct"] < 10
    df_w["Team"] = df_w.apply(
        lambda r: f"⭐ {r['team']}" if r["bold"] else r["team"], axis=1
    )
    df_w = df_w.rename(columns={"count": "Picks", "pct": "% of players"})[["Team", "Picks", "% of players"]]

    col1, col2 = st.columns([2, 3])
    with col1:
        st.dataframe(df_w, use_container_width=True, hide_index=True)
    with col2:
        chart_data = pd.DataFrame(winner_dist).set_index("team")[["count"]].head(15)
        st.bar_chart(chart_data, use_container_width=True)

st.divider()

# ---------------------------------------------------------------------------
# Finalist distribution
# ---------------------------------------------------------------------------
st.subheader("Who did players pick as finalist?")

fin_dist = get_finalist_distribution()
if not fin_dist:
    st.info("No finalist predictions yet.")
else:
    df_f = pd.DataFrame(fin_dist)
    df_f = df_f.rename(columns={"team": "Team", "count": "Picks", "pct": "% of players"})

    col1, col2 = st.columns([2, 3])
    with col1:
        st.dataframe(df_f, use_container_width=True, hide_index=True)
    with col2:
        st.bar_chart(df_f.set_index("Team")[["Picks"]].head(15), use_container_width=True)

st.divider()

# ---------------------------------------------------------------------------
# Most popular group picks
# ---------------------------------------------------------------------------
st.subheader("Most popular group winners")

svc = get_service_client()
resp = svc.table("group_predictions").select("group_name, position_1").execute()

if resp.data:
    group_tops: dict[str, dict[str, int]] = {}
    for row in resp.data:
        gname = row["group_name"]
        team = row["position_1"]
        group_tops.setdefault(gname, {})
        group_tops[gname][team] = group_tops[gname].get(team, 0) + 1

    rows = []
    for gname in sorted(group_tops.keys()):
        counts = group_tops[gname]
        top_team = max(counts, key=lambda t: counts[t])
        top_pct = round(counts[top_team] / sum(counts.values()) * 100, 1)
        rows.append({"Group": gname, "Most picked winner": top_team, "% who picked them": top_pct})

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
