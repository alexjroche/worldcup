from __future__ import annotations

from components.db import (
    get_all_predictions_for_scoring,
    get_group_results,
    get_knockout_results,
    get_all_round_picks_and_results,
    bulk_upsert_scores,
    save_score_snapshot,
    get_service_client,
)

ROUND_POINTS = {"R32": 2, "R16": 4, "QF": 6, "SF": 10, "Final": 15}


def _score_group(predicted: list[str], actual: list[str]) -> int:
    """Score one group prediction against the actual result. Max 12 points."""
    score = 0
    for i, team in enumerate(predicted):
        if i < len(actual) and team == actual[i]:
            score += 3  # exact position
        elif team in actual[:2] and i < 2:
            score += 1  # right zone (top 2)
        elif team in actual[2:] and i >= 2:
            score += 1  # right zone (bottom 2)
    return score


def _score_winner(prediction: str, actual: str | None) -> int:
    return 20 if actual and prediction == actual else 0


def _score_finalist(prediction: str, actual: str | None) -> int:
    return 10 if actual and prediction == actual else 0


def _score_semis(semi_1: str, semi_2: str, actual_semi_1: str | None, actual_semi_2: str | None) -> int:
    actual_semis = {s for s in [actual_semi_1, actual_semi_2] if s}
    score = 0
    if semi_1 in actual_semis:
        score += 5
    if semi_2 in actual_semis:
        score += 5
    return score


def _score_golden_boot(prediction: str, actual: str | None) -> int:
    if not actual or not prediction:
        return 0
    return 10 if prediction.strip().lower() == actual.strip().lower() else 0


def _score_round_picks(user_picks: list[dict], matches_by_id: dict[str, dict]) -> int:
    total = 0
    for pick in user_picks:
        match = matches_by_id.get(pick["match_id"])
        if match and match.get("winner") and pick["pick"] == match["winner"]:
            total += ROUND_POINTS.get(match["round"], 0)
    return total


def calculate_scores(snapshot_label: str | None = None) -> int:
    """Recalculate all scores. Returns the number of users updated.
    If snapshot_label is provided, saves a timeline snapshot."""
    group_preds, ko_preds = get_all_predictions_for_scoring()
    group_results = get_group_results()
    ko_results = get_knockout_results()
    round_picks, round_matches = get_all_round_picks_and_results()

    # Winner popularity → bold_pick badge
    winner_counts: dict[str, int] = {}
    for kp in ko_preds:
        w = kp.get("winner", "")
        if w:
            winner_counts[w] = winner_counts.get(w, 0) + 1
    total_ko = len(ko_preds) or 1

    # Group scoring — also track per-group exact hits for Perfect Group badge
    user_group_scores: dict[str, int] = {}
    user_perfect_groups: dict[str, int] = {}
    for gp in group_preds:
        uid = gp["user_id"]
        gname = gp["group_name"]
        if gname not in group_results:
            continue
        result = group_results[gname]
        predicted = [gp["position_1"], gp["position_2"], gp["position_3"], gp["position_4"]]
        actual = [result["position_1"], result["position_2"], result["position_3"], result["position_4"]]
        pts = _score_group(predicted, actual)
        user_group_scores[uid] = user_group_scores.get(uid, 0) + pts
        if pts == 12:  # all 4 positions exact = perfect group
            user_perfect_groups[uid] = user_perfect_groups.get(uid, 0) + 1

    # Top of the Table badge: highest group_points when all 12 results are in
    all_groups_done = len(group_results) == 12
    top_of_table_uids: set[str] = set()
    if all_groups_done and user_group_scores:
        max_gpts = max(user_group_scores.values())
        top_of_table_uids = {uid for uid, pts in user_group_scores.items() if pts == max_gpts}

    # Round picks
    user_round_picks: dict[str, list[dict]] = {}
    for rp in round_picks:
        uid = rp["user_id"]
        user_round_picks.setdefault(uid, []).append(rp)
    matches_by_id = {m["id"]: m for m in round_matches}

    all_users: set[str] = (
        {gp["user_id"] for gp in group_preds}
        | {kp["user_id"] for kp in ko_preds}
        | {rp["user_id"] for rp in round_picks}
    )
    ko_index = {kp["user_id"]: kp for kp in ko_preds}

    rows = []
    for uid in all_users:
        gpts = user_group_scores.get(uid, 0)
        wpts = fpts = spts = gbpts = rpts = 0
        bold = oracle = gb_win = False

        kp = ko_index.get(uid)
        if kp:
            winner_pred = kp.get("winner", "")
            if ko_results:
                wpts = _score_winner(winner_pred, ko_results.get("winner"))
                fpts = _score_finalist(kp.get("finalist", ""), ko_results.get("finalist"))
                spts = _score_semis(
                    kp.get("semi_1", ""), kp.get("semi_2", ""),
                    ko_results.get("semi_1"), ko_results.get("semi_2"),
                )
                gbpts = _score_golden_boot(kp.get("golden_boot", ""), ko_results.get("golden_boot"))
                oracle = wpts > 0 and fpts > 0
                gb_win = gbpts > 0

            pct = winner_counts.get(winner_pred, 0) / total_ko * 100
            bold = pct < 10.0

        rpts = _score_round_picks(user_round_picks.get(uid, []), matches_by_id)
        total = gpts + wpts + fpts + spts + gbpts + rpts

        rows.append({
            "user_id": uid,
            "group_points": gpts,
            "winner_points": wpts,
            "finalist_points": fpts,
            "semi_points": spts,
            "golden_boot_pts": gbpts,
            "round_points": rpts,
            "bold_pick": bold,
            "badge_perfect_groups": user_perfect_groups.get(uid, 0),
            "badge_oracle": oracle,
            "badge_golden_boot_win": gb_win,
            "badge_top_of_table": uid in top_of_table_uids,
            # used only for snapshot, not written to DB
            "total_points_calc": total,
        })

    if rows:
        # Strip the helper key before writing to DB
        db_rows = [{k: v for k, v in r.items() if k != "total_points_calc"} for r in rows]
        bulk_upsert_scores(db_rows)
        if snapshot_label:
            save_score_snapshot(snapshot_label, rows)

    return len(rows)
