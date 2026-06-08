from __future__ import annotations

from components.db import (
    get_all_predictions_for_scoring,
    get_group_results,
    get_knockout_results,
    bulk_upsert_scores,
    get_service_client,
)


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


def calculate_scores() -> int:
    """Recalculate all scores. Returns the number of users updated."""
    group_preds, ko_preds = get_all_predictions_for_scoring()
    group_results = get_group_results()
    ko_results = get_knockout_results()

    # Compute winner popularity for bold_pick badge
    winner_counts: dict[str, int] = {}
    for kp in ko_preds:
        w = kp.get("winner", "")
        if w:
            winner_counts[w] = winner_counts.get(w, 0) + 1
    total_ko = len(ko_preds) or 1

    # Index group predictions by user
    user_group_scores: dict[str, int] = {}
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

    # Build score rows
    all_users: set[str] = {gp["user_id"] for gp in group_preds} | {kp["user_id"] for kp in ko_preds}
    ko_index = {kp["user_id"]: kp for kp in ko_preds}

    rows = []
    for uid in all_users:
        gpts = user_group_scores.get(uid, 0)
        wpts = fpts = spts = gbpts = 0
        bold = False

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

            pct = winner_counts.get(winner_pred, 0) / total_ko * 100
            bold = pct < 10.0

        rows.append({
            "user_id": uid,
            "group_points": gpts,
            "winner_points": wpts,
            "finalist_points": fpts,
            "semi_points": spts,
            "golden_boot_pts": gbpts,
            "bold_pick": bold,
        })

    if rows:
        bulk_upsert_scores(rows)
    return len(rows)
