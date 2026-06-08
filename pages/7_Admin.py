import streamlit as st
from components.auth import require_admin
from components.db import (
    get_group_results, save_group_result,
    get_knockout_results, save_knockout_results,
)
from components.scoring import calculate_scores
from data.teams import GROUPS, ALL_TEAMS, team_display, strip_flag

st.set_page_config(page_title="Admin — WC2026", page_icon="🛠", layout="wide")

if not require_admin():
    st.stop()

st.title("🛠 Admin Panel")
st.caption("Enter official results and trigger score recalculation.")

existing_group_results = get_group_results()
existing_ko_results = get_knockout_results()

tab_grp, tab_ko, tab_scores = st.tabs(["Group Results", "Knockout Results", "Recalculate Scores"])

# ===========================================================================
# GROUP RESULTS
# ===========================================================================
with tab_grp:
    st.markdown("Enter the final group standings (top 4) for each group.")

    group_names = list(GROUPS.keys())
    for row_start in range(0, 12, 3):
        cols = st.columns(3)
        for col_idx, col in enumerate(cols):
            gi = row_start + col_idx
            if gi >= len(group_names):
                break
            gname = group_names[gi]
            teams = GROUPS[gname]
            existing = existing_group_results.get(gname)
            saved_badge = "✅" if existing else "⬜"

            with col:
                st.markdown(f"### Group {gname} {saved_badge}")
                options = [team_display(t) for t in teams]

                default_order = (
                    [existing["position_1"], existing["position_2"], existing["position_3"], existing["position_4"]]
                    if existing else teams
                )

                picks = []
                for pos in range(4):
                    label = f"{'1st' if pos==0 else '2nd' if pos==1 else '3rd' if pos==2 else '4th'} place"
                    default_val = team_display(default_order[pos]) if pos < len(default_order) else options[pos]
                    sel = st.selectbox(
                        label,
                        options=options,
                        index=options.index(default_val) if default_val in options else pos,
                        key=f"res_grp_{gname}_{pos}",
                    )
                    picks.append(strip_flag(sel))

                if st.button(f"Save Group {gname} Result", key=f"save_res_{gname}", use_container_width=True):
                    save_group_result(gname, picks[0], picks[1], picks[2], picks[3])
                    existing_group_results[gname] = {
                        "position_1": picks[0], "position_2": picks[1],
                        "position_3": picks[2], "position_4": picks[3],
                    }
                    st.success(f"Group {gname} result saved!")
                    st.rerun()

# ===========================================================================
# KNOCKOUT RESULTS
# ===========================================================================
with tab_ko:
    st.markdown("Enter the knockout results as the tournament progresses.")
    team_options = [team_display(t) for t in ALL_TEAMS]

    def _ko_default(field: str, fallback_idx: int) -> str:
        if existing_ko_results and existing_ko_results.get(field):
            return team_display(existing_ko_results[field])
        return team_options[fallback_idx]

    col1, col2 = st.columns(2)
    with col1:
        winner_sel = st.selectbox("🥇 Tournament Winner", team_options,
            index=team_options.index(_ko_default("winner", 0)), key="res_winner")
        finalist_sel = st.selectbox("🥈 Finalist", team_options,
            index=team_options.index(_ko_default("finalist", 1)), key="res_finalist")
    with col2:
        semi1_sel = st.selectbox("Semi-finalist 1", team_options,
            index=team_options.index(_ko_default("semi_1", 2)), key="res_semi1")
        semi2_sel = st.selectbox("Semi-finalist 2", team_options,
            index=team_options.index(_ko_default("semi_2", 3)), key="res_semi2")

    golden_boot_val = existing_ko_results.get("golden_boot", "") if existing_ko_results else ""
    golden_boot = st.text_input("Golden Boot (top scorer)", value=golden_boot_val or "", key="res_gb")

    if st.button("Save Knockout Results", use_container_width=True):
        save_knockout_results(
            strip_flag(winner_sel), strip_flag(finalist_sel),
            strip_flag(semi1_sel), strip_flag(semi2_sel),
            golden_boot.strip(),
        )
        st.success("Knockout results saved!")
        st.rerun()

# ===========================================================================
# RECALCULATE SCORES
# ===========================================================================
with tab_scores:
    st.markdown(
        "Click below to recalculate all scores from the current results. "
        "Run this after entering new group or knockout results."
    )
    if st.button("Recalculate All Scores", use_container_width=True, type="primary"):
        with st.spinner("Calculating..."):
            n = calculate_scores()
        st.success(f"Scores recalculated for {n} player(s).")
