import streamlit as st
import pandas as pd
from components.auth import require_auth, get_current_user, get_current_profile
from components.db import (
    get_all_profiles, get_scores_by_user_id,
    get_group_predictions, get_knockout_prediction,
    get_all_user_round_picks, get_matches_for_round,
    get_group_results, get_knockout_results,
)
from components.lock import is_locked
from components.scoring import ROUND_POINTS, _score_group
from components.db import ROUND_ORDER
from data.teams import GROUPS, team_display

st.set_page_config(page_title="Head to Head — WC2026", page_icon="⚔️", layout="wide")

if not require_auth():
    st.stop()

user = get_current_user()
profile = get_current_profile()
my_uid = user.id
my_name = profile.get("display_name", "You") if profile else "You"

st.title("⚔️ Head to Head")
st.markdown("Pick a player to compare your predictions against theirs.")

# ---------------------------------------------------------------------------
# Opponent picker
# ---------------------------------------------------------------------------
all_profiles = [p for p in get_all_profiles() if p["id"] != my_uid]

if not all_profiles:
    st.info("No other players have registered yet.")
    st.stop()

opponent_names = [p["display_name"] for p in all_profiles]
sel_name = st.selectbox("Choose your opponent", opponent_names)
opponent = next(p for p in all_profiles if p["display_name"] == sel_name)
opp_uid = opponent["id"]
opp_name = opponent["display_name"]

st.divider()

locked = is_locked()

# ---------------------------------------------------------------------------
# Score comparison
# ---------------------------------------------------------------------------
my_score = get_scores_by_user_id(my_uid)
opp_score = get_scores_by_user_id(opp_uid)

my_total = my_score.get("total_points", 0) if my_score else 0
opp_total = opp_score.get("total_points", 0) if opp_score else 0
diff = my_total - opp_total

col_me, col_vs, col_them = st.columns([2, 1, 2])
with col_me:
    st.metric(f"🫵 {my_name}", f"{my_total} pts")
with col_vs:
    st.markdown("<div style='text-align:center; font-size:2em; padding-top:16px;'>vs</div>", unsafe_allow_html=True)
with col_them:
    st.metric(f"🎯 {opp_name}", f"{opp_total} pts", delta=f"{opp_total - my_total:+d} on you" if diff != 0 else "Tied")

if not locked:
    st.info("Full comparison unlocks after predictions lock on June 11.")
    st.stop()

st.divider()

# ---------------------------------------------------------------------------
# Group predictions comparison
# ---------------------------------------------------------------------------
st.subheader("🗂 Group Stage")

my_grp_preds = get_group_predictions(my_uid)
opp_grp_preds = get_group_predictions(opp_uid)
group_results = get_group_results()

grp_rows = []
for gname in sorted(GROUPS.keys()):
    my_gp = my_grp_preds.get(gname)
    opp_gp = opp_grp_preds.get(gname)
    result = group_results.get(gname)

    def fmt_pred(gp: dict | None) -> str:
        if not gp:
            return "—"
        return " → ".join([gp["position_1"], gp["position_2"], gp["position_3"], gp["position_4"]])

    def grp_pts(gp: dict | None) -> str:
        if not gp or not result:
            return "?"
        pred = [gp["position_1"], gp["position_2"], gp["position_3"], gp["position_4"]]
        actual = [result["position_1"], result["position_2"], result["position_3"], result["position_4"]]
        pts = _score_group(pred, actual)
        return f"{pts}/12"

    actual_str = fmt_pred(result) if result else "Not yet"
    grp_rows.append({
        "Group": gname,
        f"{my_name}": fmt_pred(my_gp),
        f"{my_name} pts": grp_pts(my_gp),
        f"{opp_name}": fmt_pred(opp_gp),
        f"{opp_name} pts": grp_pts(opp_gp),
        "Actual": actual_str,
    })

st.dataframe(pd.DataFrame(grp_rows), use_container_width=True, hide_index=True)

st.divider()

# ---------------------------------------------------------------------------
# Pre-tournament knockout picks comparison
# ---------------------------------------------------------------------------
st.subheader("🏆 Pre-tournament Knockout Picks")

my_ko = get_knockout_prediction(my_uid)
opp_ko = get_knockout_prediction(opp_uid)
ko_results = get_knockout_results()

fields = [
    ("winner",    "🥇 Tournament Winner", 20),
    ("finalist",  "🥈 Finalist",          10),
    ("semi_1",    "4️⃣ Semi-finalist 1",   5),
    ("semi_2",    "4️⃣ Semi-finalist 2",   5),
    ("golden_boot","⚽ Golden Boot",       10),
]

ko_rows = []
for field, label, max_pts in fields:
    my_pick  = (my_ko  or {}).get(field, "—") or "—"
    opp_pick = (opp_ko or {}).get(field, "—") or "—"
    actual   = (ko_results or {}).get(field, "?") if ko_results else "?"

    def pts_badge(pick: str, actual_val: str, pts: int) -> str:
        if actual_val == "?" or not pick or pick == "—":
            return ""
        match = pick.strip().lower() == actual_val.strip().lower() if field == "golden_boot" else pick == actual_val
        return f" ✅ +{pts}" if match else " ❌"

    ko_rows.append({
        "Pick": label,
        f"{my_name}": f"{my_pick}{pts_badge(my_pick, actual, max_pts)}",
        f"{opp_name}": f"{opp_pick}{pts_badge(opp_pick, actual, max_pts)}",
        "Actual": actual,
    })

st.dataframe(pd.DataFrame(ko_rows), use_container_width=True, hide_index=True)

st.divider()

# ---------------------------------------------------------------------------
# Match picks comparison (per round)
# ---------------------------------------------------------------------------
st.subheader("⚡ Match Picks")

my_match_picks  = get_all_user_round_picks(my_uid)
opp_match_picks = get_all_user_round_picks(opp_uid)

any_rounds = False
for rname in ROUND_ORDER:
    matches = get_matches_for_round(rname)
    matches_with_result = [m for m in matches if m.get("winner")]
    if not matches_with_result:
        continue

    any_rounds = True
    pts_each = ROUND_POINTS.get(rname, 0)
    my_correct = opp_correct = 0

    with st.expander(f"{rname} ({pts_each} pts each)", expanded=True):
        round_rows = []
        for match in matches_with_result:
            mid = match["id"]
            winner = match["winner"]
            my_pick  = my_match_picks.get(mid, "—")
            opp_pick = opp_match_picks.get(mid, "—")

            def fmt_pick(pick: str) -> str:
                if pick == "—":
                    return "—"
                return f"{pick} ✅" if pick == winner else f"{pick} ❌"

            if my_pick == winner:
                my_correct += 1
            if opp_pick == winner:
                opp_correct += 1

            round_rows.append({
                "Match": f"{match['team_a']} vs {match['team_b']}",
                "Winner": winner,
                f"{my_name}": fmt_pick(my_pick),
                f"{opp_name}": fmt_pick(opp_pick),
            })

        st.dataframe(pd.DataFrame(round_rows), use_container_width=True, hide_index=True)
        c1, c2 = st.columns(2)
        c1.metric(f"{my_name}", f"{my_correct}/{len(matches_with_result)} correct (+{my_correct * pts_each} pts)")
        c2.metric(f"{opp_name}", f"{opp_correct}/{len(matches_with_result)} correct (+{opp_correct * pts_each} pts)")

if not any_rounds:
    st.info("Round-by-round match picks will appear here once knockout results are entered.")
