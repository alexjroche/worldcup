import streamlit as st
from components.auth import require_admin
from components.db import (
    get_group_results, save_group_result,
    get_knockout_results, save_knockout_results,
    get_all_rounds, set_round_status,
    get_matches_for_round, upsert_match, save_match_result,
    ROUND_ORDER,
)
from components.scoring import calculate_scores, ROUND_POINTS
from data.teams import GROUPS, ALL_TEAMS, team_display, strip_flag

st.set_page_config(page_title="Admin — WC2026", page_icon="🛠", layout="wide")

if not require_admin():
    st.stop()

st.title("🛠 Admin Panel")
st.caption("Enter official results and trigger score recalculation.")

existing_group_results = get_group_results()
existing_ko_results = get_knockout_results()

tab_grp, tab_ko, tab_rounds, tab_scores = st.tabs(["Group Results", "Knockout Results", "Round Knockout", "Recalculate Scores"])

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
# ROUND KNOCKOUT MANAGEMENT
# ===========================================================================
with tab_rounds:
    st.markdown("Manage knockout rounds: enter matchups, open predictions, enter results, close rounds.")

    rounds_data = {r["round"]: r for r in get_all_rounds()}
    team_options_all = [team_display(t) for t in ALL_TEAMS]

    # --- Part 1: Round status overview ---
    st.subheader("Round status")
    status_cols = st.columns(5)
    for i, rname in enumerate(ROUND_ORDER):
        rnd = rounds_data.get(rname, {})
        status = rnd.get("status", "pending")
        badge = {"pending": "⬜", "open": "🟢", "closed": "🔒"}.get(status, "⬜")
        with status_cols[i]:
            st.markdown(f"**{rname}**  \n{badge} {status.title()}")
            if status == "pending":
                if st.button("Open", key=f"open_{rname}", use_container_width=True):
                    set_round_status(rname, "open")
                    st.success(f"{rname} is now open for picks.")
                    st.rerun()
            elif status == "open":
                if st.button("Close", key=f"close_{rname}", use_container_width=True, type="primary"):
                    set_round_status(rname, "closed")
                    st.success(f"{rname} closed.")
                    st.rerun()

    st.divider()

    # --- Part 2: Enter matchups ---
    st.subheader("Enter matchups")
    MATCH_COUNTS = {"R32": 16, "R16": 8, "QF": 4, "SF": 2, "Final": 1}
    sel_round_matchups = st.selectbox("Round", ROUND_ORDER, key="admin_matchup_round")
    n_matches = MATCH_COUNTS[sel_round_matchups]
    existing_matches = {m["match_number"]: m for m in get_matches_for_round(sel_round_matchups)}

    st.caption(f"{n_matches} matches — select teams for each fixture.")

    with st.form(f"matchups_{sel_round_matchups}"):
        matchup_picks = []
        pair_cols = st.columns(2)
        for mn in range(1, n_matches + 1):
            existing = existing_matches.get(mn, {})
            def_a = team_display(existing["team_a"]) if existing.get("team_a") else team_options_all[0]
            def_b = team_display(existing["team_b"]) if existing.get("team_b") else team_options_all[1]
            col = pair_cols[(mn - 1) % 2]
            with col:
                st.markdown(f"**Match {mn}**")
                a = st.selectbox("Team A", team_options_all,
                    index=team_options_all.index(def_a) if def_a in team_options_all else 0,
                    key=f"mu_{sel_round_matchups}_{mn}_a")
                b = st.selectbox("Team B", team_options_all,
                    index=team_options_all.index(def_b) if def_b in team_options_all else 1,
                    key=f"mu_{sel_round_matchups}_{mn}_b")
                matchup_picks.append((mn, strip_flag(a), strip_flag(b)))

        if st.form_submit_button("Save matchups", use_container_width=True):
            for mn, ta, tb in matchup_picks:
                upsert_match(sel_round_matchups, mn, ta, tb)
            st.success(f"{sel_round_matchups} matchups saved!")
            st.rerun()

    st.divider()

    # --- Part 3: Enter results ---
    st.subheader("Enter results")
    sel_round_results = st.selectbox("Round", ROUND_ORDER, key="admin_results_round")
    result_matches = get_matches_for_round(sel_round_results)

    if not result_matches:
        st.info("No matchups entered for this round yet.")
    else:
        for match in result_matches:
            mid = match["id"]
            ta, tb = match["team_a"], match["team_b"]
            current_winner = match.get("winner")
            winner_opts = [team_display(ta), team_display(tb)]
            default_w = team_display(current_winner) if current_winner else winner_opts[0]
            wcol1, wcol2 = st.columns([3, 1])
            with wcol1:
                won_sel = st.selectbox(
                    f"Match {match['match_number']}: {team_display(ta)} vs {team_display(tb)}",
                    winner_opts,
                    index=winner_opts.index(default_w) if default_w in winner_opts else 0,
                    key=f"res_round_{sel_round_results}_{mid}",
                )
            with wcol2:
                st.markdown("&nbsp;", unsafe_allow_html=True)
                if st.button("Save", key=f"save_res_round_{mid}"):
                    save_match_result(mid, strip_flag(won_sel))
                    st.success("Saved!")
                    st.rerun()

# ===========================================================================
# RECALCULATE SCORES
# ===========================================================================
with tab_scores:
    st.markdown(
        "Recalculate all scores from current results. "
        "Run after entering any new group or round results."
    )
    snapshot_label = st.text_input(
        "Timeline snapshot label",
        placeholder="e.g. After Group Stage, After R32, After QF…",
        help="If filled in, this run will be saved as a point on the score timeline chart.",
    )
    if st.button("Recalculate All Scores", use_container_width=True, type="primary"):
        with st.spinner("Calculating..."):
            n = calculate_scores(snapshot_label.strip() or None)
        st.success(f"Scores recalculated for {n} player(s).")
        if snapshot_label.strip():
            st.info(f"Snapshot '{snapshot_label.strip()}' saved to timeline.")
