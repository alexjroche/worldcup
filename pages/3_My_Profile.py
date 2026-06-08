import streamlit as st
from components.auth import require_auth, get_current_user, get_current_profile
from components.db import (
    upsert_profile, get_profile, count_group_predictions,
    get_knockout_prediction, get_group_results, get_knockout_results,
)
from components.lock import is_locked

st.set_page_config(page_title="My Profile — WC2026", page_icon="👤", layout="centered")

if not require_auth():
    st.stop()

user = get_current_user()
profile = get_current_profile()
uid = user.id

st.title("👤 My Profile")

# ---------------------------------------------------------------------------
# Edit profile
# ---------------------------------------------------------------------------
with st.expander("Edit profile", expanded=False):
    with st.form("profile_form"):
        new_name = st.text_input("Display name", value=profile.get("display_name", ""))
        new_player = st.text_input("Favourite player", value=profile.get("favourite_player", "") or "")
        if st.form_submit_button("Save changes", use_container_width=True):
            if not new_name.strip():
                st.error("Display name cannot be empty.")
            else:
                upsert_profile(uid, new_name.strip(), new_player.strip())
                # refresh in session
                updated = get_profile(uid)
                st.session_state["profile"] = updated
                st.success("Profile updated!")
                st.rerun()

# ---------------------------------------------------------------------------
# Prediction summary
# ---------------------------------------------------------------------------
st.subheader("Your predictions summary")

groups_done = count_group_predictions(uid)
ko_pred = get_knockout_prediction(uid)
locked = is_locked()

col1, col2, col3 = st.columns(3)
col1.metric("Groups predicted", f"{groups_done}/12")
col2.metric("Knockout picked", "Yes" if ko_pred else "No")
col3.metric("Status", "Locked" if locked else "Open")

if not locked and groups_done < 12:
    st.warning(f"You have {12 - groups_done} group(s) left to predict before lock!")
    st.page_link("pages/4_Predictions.py", label="Go to Predictions", icon="🎯")

# ---------------------------------------------------------------------------
# Knockout picks (always visible to the owner)
# ---------------------------------------------------------------------------
if ko_pred:
    st.subheader("Your knockout picks")
    col1, col2 = st.columns(2)
    col1.metric("Winner", ko_pred.get("winner", "—"))
    col2.metric("Finalist", ko_pred.get("finalist", "—"))
    col1.metric("Semi-finalist 1", ko_pred.get("semi_1", "—"))
    col2.metric("Semi-finalist 2", ko_pred.get("semi_2", "—"))
    if ko_pred.get("golden_boot"):
        st.metric("Golden Boot pick", ko_pred["golden_boot"])

# ---------------------------------------------------------------------------
# Score breakdown (if results are in)
# ---------------------------------------------------------------------------
group_results = get_group_results()
ko_results = get_knockout_results()

if group_results or ko_results:
    st.subheader("Your scores so far")
    from components.scoring import (
        _score_group, _score_winner, _score_finalist, _score_semis, _score_golden_boot
    )
    from components.db import get_group_predictions

    user_group_preds = get_group_predictions(uid)
    total = 0

    if group_results:
        grp_total = 0
        rows = []
        for gname, res in sorted(group_results.items()):
            if gname in user_group_preds:
                gp = user_group_preds[gname]
                pred = [gp["position_1"], gp["position_2"], gp["position_3"], gp["position_4"]]
                actual = [res["position_1"], res["position_2"], res["position_3"], res["position_4"]]
                pts = _score_group(pred, actual)
                grp_total += pts
                rows.append({"Group": gname, "Your pick": " → ".join(pred), "Actual": " → ".join(actual), "Points": pts})
        if rows:
            import pandas as pd
            st.markdown(f"**Group stage: {grp_total} pts**")
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        total += grp_total

    if ko_results and ko_pred:
        wpts = _score_winner(ko_pred.get("winner", ""), ko_results.get("winner"))
        fpts = _score_finalist(ko_pred.get("finalist", ""), ko_results.get("finalist"))
        spts = _score_semis(ko_pred.get("semi_1", ""), ko_pred.get("semi_2", ""), ko_results.get("semi_1"), ko_results.get("semi_2"))
        gbpts = _score_golden_boot(ko_pred.get("golden_boot", ""), ko_results.get("golden_boot"))
        ko_total = wpts + fpts + spts + gbpts
        total += ko_total
        st.markdown(f"**Knockout picks: {ko_total} pts** (winner {wpts} + finalist {fpts} + semis {spts} + golden boot {gbpts})")

    st.metric("Total score", f"{total} pts")
