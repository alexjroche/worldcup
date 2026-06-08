import streamlit as st
from components.auth import require_auth, get_current_user
from components.db import (
    get_group_predictions, save_group_prediction,
    get_knockout_prediction, save_knockout_prediction,
    count_group_predictions,
)
from components.lock import is_locked, time_until_lock
from data.teams import GROUPS, ALL_TEAMS, team_display, strip_flag

st.set_page_config(page_title="Predictions — WC2026", page_icon="🎯", layout="wide")

if not require_auth():
    st.stop()

user = get_current_user()
uid = user.id
locked = is_locked()

st.title("🎯 Your Predictions")

if locked:
    st.error("🔒 Predictions are locked — the tournament has started!")
else:
    st.info(f"⏳ {time_until_lock()} — save your predictions before kickoff!")

# Load existing predictions once
existing_groups = get_group_predictions(uid)
existing_ko = get_knockout_prediction(uid)

groups_done = count_group_predictions(uid)
ko_done = existing_ko is not None

# Progress bar
st.markdown(f"**Progress:** {groups_done}/12 groups · Knockout: {'✅' if ko_done else '❌'}")
progress = (groups_done + (1 if ko_done else 0)) / 13
st.progress(progress)

tab_groups, tab_knockout, tab_summary = st.tabs(["🗂 Group Stage", "🏆 Knockout & Golden Boot", "📋 Summary"])

# ===========================================================================
# TAB 1: GROUP STAGE
# ===========================================================================
with tab_groups:
    st.markdown("Drag — or select — the finishing order for each group. Save each group individually.")

    group_names = list(GROUPS.keys())
    # Show in 3 columns of 4 groups each
    for row_start in range(0, 12, 3):
        cols = st.columns(3)
        for col_idx, col in enumerate(cols):
            gi = row_start + col_idx
            if gi >= len(group_names):
                break
            gname = group_names[gi]
            teams = GROUPS[gname]
            existing = existing_groups.get(gname)
            saved_badge = "✅" if existing else "⬜"

            with col:
                st.markdown(f"### Group {gname} {saved_badge}")
                default_order = (
                    [existing["position_1"], existing["position_2"], existing["position_3"], existing["position_4"]]
                    if existing else teams
                )

                picks = []
                options = [team_display(t) for t in teams]
                all_valid = True

                for pos in range(4):
                    label = f"{pos + 1}{'st' if pos == 0 else 'nd' if pos == 1 else 'rd' if pos == 2 else 'th'} place"
                    default_val = team_display(default_order[pos]) if pos < len(default_order) else options[pos]
                    sel = st.selectbox(
                        label,
                        options=options,
                        index=options.index(default_val) if default_val in options else pos,
                        key=f"grp_{gname}_{pos}",
                        disabled=locked,
                    )
                    picks.append(strip_flag(sel))

                if len(picks) != len(set(picks)):
                    st.warning("Each team must appear once.")
                    all_valid = False

                if not locked:
                    if st.button(f"Save Group {gname}", key=f"save_grp_{gname}", use_container_width=True, disabled=not all_valid):
                        save_group_prediction(uid, gname, picks[0], picks[1], picks[2], picks[3])
                        existing_groups[gname] = {
                            "position_1": picks[0], "position_2": picks[1],
                            "position_3": picks[2], "position_4": picks[3],
                        }
                        st.success(f"Group {gname} saved!")
                        st.rerun()

# ===========================================================================
# TAB 2: KNOCKOUT & GOLDEN BOOT
# ===========================================================================
with tab_knockout:
    st.markdown(
        "Pick the teams you think will reach the semi-finals, the finalist and the winner. "
        "All four knockout picks must be different teams."
    )

    team_options = [team_display(t) for t in ALL_TEAMS]

    def _default(field: str, fallback_idx: int) -> str:
        if existing_ko and existing_ko.get(field):
            return team_display(existing_ko[field])
        return team_options[fallback_idx]

    col1, col2 = st.columns(2)
    with col1:
        winner_sel = st.selectbox(
            "🥇 Tournament Winner",
            options=team_options,
            index=team_options.index(_default("winner", 0)),
            disabled=locked,
            key="ko_winner",
        )
        finalist_sel = st.selectbox(
            "🥈 Finalist (Runner-up)",
            options=team_options,
            index=team_options.index(_default("finalist", 1)),
            disabled=locked,
            key="ko_finalist",
        )
    with col2:
        semi1_sel = st.selectbox(
            "4️⃣ Semi-finalist 1",
            options=team_options,
            index=team_options.index(_default("semi_1", 2)),
            disabled=locked,
            key="ko_semi1",
        )
        semi2_sel = st.selectbox(
            "4️⃣ Semi-finalist 2",
            options=team_options,
            index=team_options.index(_default("semi_2", 3)),
            disabled=locked,
            key="ko_semi2",
        )

    st.divider()
    st.markdown("#### ⚽ Golden Boot — top scorer")
    golden_boot_val = existing_ko.get("golden_boot", "") if existing_ko else ""
    golden_boot = st.text_input(
        "Player name (e.g. Kylian Mbappé)",
        value=golden_boot_val or "",
        disabled=locked,
        key="ko_golden_boot",
    )

    # Validation
    ko_picks = [strip_flag(winner_sel), strip_flag(finalist_sel), strip_flag(semi1_sel), strip_flag(semi2_sel)]
    ko_valid = len(ko_picks) == len(set(ko_picks))

    if not ko_valid:
        st.warning("Your winner, finalist and semi-finalists must all be different teams.")

    if not locked:
        if st.button("Save Knockout Picks", use_container_width=True, disabled=not ko_valid):
            save_knockout_prediction(
                uid,
                ko_picks[0], ko_picks[1], ko_picks[2], ko_picks[3],
                golden_boot.strip(),
            )
            st.success("Knockout picks saved!")
            st.rerun()

# ===========================================================================
# TAB 3: SUMMARY
# ===========================================================================
with tab_summary:
    st.markdown("### Your full prediction summary")

    if locked:
        st.success("Predictions are locked in — good luck!")
    else:
        remaining = 12 - groups_done
        if remaining > 0:
            st.warning(f"You still have {remaining} group(s) to predict.")
        if not ko_done:
            st.warning("You haven't saved your knockout picks yet.")

    st.markdown("#### Group predictions")
    if not existing_groups:
        st.info("No group predictions saved yet.")
    else:
        import pandas as pd
        rows = []
        for gname in sorted(existing_groups.keys()):
            gp = existing_groups[gname]
            rows.append({
                "Group": gname,
                "1st": gp["position_1"],
                "2nd": gp["position_2"],
                "3rd": gp["position_3"],
                "4th": gp["position_4"],
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.markdown("#### Knockout picks")
    if not existing_ko:
        st.info("No knockout picks saved yet.")
    else:
        col1, col2 = st.columns(2)
        col1.metric("Winner", existing_ko.get("winner", "—"))
        col2.metric("Finalist", existing_ko.get("finalist", "—"))
        col1.metric("Semi 1", existing_ko.get("semi_1", "—"))
        col2.metric("Semi 2", existing_ko.get("semi_2", "—"))
        if existing_ko.get("golden_boot"):
            st.metric("Golden Boot", existing_ko["golden_boot"])
