from __future__ import annotations

import streamlit as st
from supabase import create_client, Client

# ---------------------------------------------------------------------------
# Client singleton
# ---------------------------------------------------------------------------

@st.cache_resource
def get_client() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


@st.cache_resource
def get_service_client() -> Client:
    """Service-role client — bypasses RLS. Only used in Admin page."""
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_SERVICE_KEY"]
    return create_client(url, key)


# ---------------------------------------------------------------------------
# Profile queries
# ---------------------------------------------------------------------------

def get_profile(user_id: str) -> dict | None:
    client = get_client()
    resp = client.table("profiles").select("*").eq("id", user_id).single().execute()
    return resp.data


def upsert_profile(user_id: str, display_name: str, favourite_player: str) -> None:
    client = get_client()
    client.table("profiles").upsert({
        "id": user_id,
        "display_name": display_name,
        "favourite_player": favourite_player,
    }).execute()


# ---------------------------------------------------------------------------
# Group prediction queries
# ---------------------------------------------------------------------------

def get_group_predictions(user_id: str) -> dict[str, dict]:
    """Returns {group_name: {position_1..4}} for this user."""
    client = get_client()
    resp = (
        client.table("group_predictions")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )
    return {row["group_name"]: row for row in (resp.data or [])}


def save_group_prediction(
    user_id: str, group_name: str, p1: str, p2: str, p3: str, p4: str
) -> None:
    client = get_client()
    client.table("group_predictions").upsert(
        {
            "user_id": user_id,
            "group_name": group_name,
            "position_1": p1,
            "position_2": p2,
            "position_3": p3,
            "position_4": p4,
        },
        on_conflict="user_id,group_name",
    ).execute()


def count_group_predictions(user_id: str) -> int:
    client = get_client()
    resp = (
        client.table("group_predictions")
        .select("group_name", count="exact")
        .eq("user_id", user_id)
        .execute()
    )
    return resp.count or 0


# ---------------------------------------------------------------------------
# Knockout prediction queries
# ---------------------------------------------------------------------------

def get_knockout_prediction(user_id: str) -> dict | None:
    client = get_client()
    resp = (
        client.table("knockout_predictions")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )
    return resp.data[0] if resp.data else None


def save_knockout_prediction(
    user_id: str, winner: str, finalist: str, semi_1: str, semi_2: str,
    golden_boot: str = "", golden_ball: str = "", golden_glove: str = "",
) -> None:
    client = get_client()
    client.table("knockout_predictions").upsert(
        {
            "user_id": user_id,
            "winner": winner,
            "finalist": finalist,
            "semi_1": semi_1,
            "semi_2": semi_2,
            "golden_boot": golden_boot,
            "golden_ball": golden_ball,
            "golden_glove": golden_glove,
        },
        on_conflict="user_id",
    ).execute()


# ---------------------------------------------------------------------------
# Leaderboard queries
# ---------------------------------------------------------------------------

def get_leaderboard(league_id: str | None = None) -> list[dict]:
    """Returns profiles joined with scores, sorted by total_points desc.
    Pass league_id to restrict to members of that league."""
    client = get_client()
    query = (
        client.table("scores")
        .select("*, profiles(display_name, favourite_player)")
        .order("total_points", desc=True)
    )
    if league_id:
        member_ids = get_league_member_ids(league_id)
        if not member_ids:
            return []
        query = query.in_("user_id", member_ids)
    resp = query.execute()
    return resp.data or []


def get_submission_counts(league_id: str | None = None) -> list[dict]:
    """Returns per-user group submission counts + knockout submitted flag.
    Pass league_id to restrict to members of that league."""
    client = get_client()
    grp = (
        client.table("group_predictions")
        .select("user_id", count="exact")
        .execute()
    )
    ko = client.table("knockout_predictions").select("user_id").execute()
    ko_set = {r["user_id"] for r in (ko.data or [])}

    counts: dict[str, dict] = {}
    for row in (grp.data or []):
        uid = row["user_id"]
        counts.setdefault(uid, {"groups": 0, "knockout": False})
        counts[uid]["groups"] += 1
    for uid in ko_set:
        counts.setdefault(uid, {"groups": 0, "knockout": False})
        counts[uid]["knockout"] = True

    member_ids: set[str] | None = None
    if league_id:
        member_ids = set(get_league_member_ids(league_id))

    profile_resp = client.table("profiles").select("id, display_name, favourite_player").execute()
    result = []
    for p in (profile_resp.data or []):
        uid = p["id"]
        if member_ids is not None and uid not in member_ids:
            continue
        c = counts.get(uid, {"groups": 0, "knockout": False})
        result.append({
            "display_name": p["display_name"],
            "favourite_player": p.get("favourite_player", ""),
            "groups_submitted": c["groups"],
            "knockout_submitted": c["knockout"],
        })
    return sorted(result, key=lambda x: x["groups_submitted"], reverse=True)


# ---------------------------------------------------------------------------
# Stats queries (aggregate, post-lock)
# ---------------------------------------------------------------------------

def get_winner_distribution() -> list[dict]:
    client = get_client()
    resp = client.table("knockout_predictions").select("winner").execute()
    counts: dict[str, int] = {}
    for row in (resp.data or []):
        t = row["winner"]
        counts[t] = counts.get(t, 0) + 1
    total = sum(counts.values()) or 1
    return sorted(
        [{"team": t, "count": c, "pct": round(c / total * 100, 1)} for t, c in counts.items()],
        key=lambda x: x["count"],
        reverse=True,
    )


def get_finalist_distribution() -> list[dict]:
    client = get_client()
    resp = client.table("knockout_predictions").select("finalist").execute()
    counts: dict[str, int] = {}
    for row in (resp.data or []):
        t = row["finalist"]
        counts[t] = counts.get(t, 0) + 1
    total = sum(counts.values()) or 1
    return sorted(
        [{"team": t, "count": c, "pct": round(c / total * 100, 1)} for t, c in counts.items()],
        key=lambda x: x["count"],
        reverse=True,
    )


# ---------------------------------------------------------------------------
# Admin / results queries (service role)
# ---------------------------------------------------------------------------

def get_group_results() -> dict[str, dict]:
    client = get_client()
    resp = client.table("group_results").select("*").execute()
    return {row["group_name"]: row for row in (resp.data or [])}


def save_group_result(
    group_name: str, p1: str, p2: str, p3: str, p4: str
) -> None:
    svc = get_service_client()
    svc.table("group_results").upsert(
        {"group_name": group_name, "position_1": p1, "position_2": p2, "position_3": p3, "position_4": p4},
        on_conflict="group_name",
    ).execute()


def get_knockout_results() -> dict | None:
    client = get_client()
    resp = client.table("knockout_results").select("*").limit(1).execute()
    return resp.data[0] if resp.data else None


def save_knockout_results(
    winner: str, finalist: str, semi_1: str, semi_2: str,
    golden_boot: str = "", golden_ball: str = "", golden_glove: str = "",
) -> None:
    svc = get_service_client()
    svc.table("knockout_results").upsert(
        {
            "id": 1,
            "winner": winner, "finalist": finalist,
            "semi_1": semi_1, "semi_2": semi_2,
            "golden_boot": golden_boot,
            "golden_ball": golden_ball,
            "golden_glove": golden_glove,
        },
        on_conflict="id",
    ).execute()


def get_all_predictions_for_scoring() -> tuple[list[dict], list[dict]]:
    """Returns (all group_predictions, all knockout_predictions)."""
    svc = get_service_client()
    grp = svc.table("group_predictions").select("*").execute()
    ko = svc.table("knockout_predictions").select("*").execute()
    return grp.data or [], ko.data or []


def bulk_upsert_scores(scores: list[dict]) -> None:
    svc = get_service_client()
    svc.table("scores").upsert(scores, on_conflict="user_id").execute()


# ---------------------------------------------------------------------------
# Knockout round lifecycle (admin-controlled)
# ---------------------------------------------------------------------------

ROUND_ORDER = ["R32", "R16", "QF", "SF", "Final"]


def get_all_rounds() -> list[dict]:
    client = get_client()
    resp = client.table("knockout_rounds").select("*").execute()
    data = {r["round"]: r for r in (resp.data or [])}
    return [data[r] for r in ROUND_ORDER if r in data]


def set_round_status(round_name: str, status: str) -> None:
    svc = get_service_client()
    update = {"status": status}
    if status == "open":
        update["opened_at"] = "now()"
    elif status == "closed":
        update["closed_at"] = "now()"
    svc.table("knockout_rounds").update(update).eq("round", round_name).execute()


# ---------------------------------------------------------------------------
# Knockout match management (admin writes, public reads)
# ---------------------------------------------------------------------------

def get_matches_for_round(round_name: str) -> list[dict]:
    client = get_client()
    resp = (
        client.table("knockout_matches")
        .select("*")
        .eq("round", round_name)
        .order("match_number")
        .execute()
    )
    return resp.data or []


def upsert_match(round_name: str, match_number: int, team_a: str, team_b: str) -> None:
    svc = get_service_client()
    svc.table("knockout_matches").upsert(
        {"round": round_name, "match_number": match_number, "team_a": team_a, "team_b": team_b},
        on_conflict="round,match_number",
    ).execute()


def save_match_result(match_id: str, winner: str) -> None:
    svc = get_service_client()
    svc.table("knockout_matches").update({"winner": winner}).eq("id", match_id).execute()


# ---------------------------------------------------------------------------
# Knockout match predictions (user writes, RLS-controlled reads)
# ---------------------------------------------------------------------------

def get_user_round_picks(user_id: str, round_name: str) -> dict[str, str]:
    """Returns {match_id: picked_team} for this user and round."""
    client = get_client()
    resp = (
        client.table("knockout_match_predictions")
        .select("match_id, pick, knockout_matches(round)")
        .eq("user_id", user_id)
        .execute()
    )
    return {
        r["match_id"]: r["pick"]
        for r in (resp.data or [])
        if r.get("knockout_matches", {}).get("round") == round_name
    }


def save_round_picks_bulk(user_id: str, picks: list[dict]) -> None:
    """picks = [{"match_id": uuid, "pick": team_name}, ...]"""
    if not picks:
        return
    client = get_client()
    rows = [{"user_id": user_id, "match_id": p["match_id"], "pick": p["pick"]} for p in picks]
    client.table("knockout_match_predictions").upsert(
        rows, on_conflict="user_id,match_id"
    ).execute()


# ---------------------------------------------------------------------------
# Round scoring queries (service role — reads all users)
# ---------------------------------------------------------------------------

def get_all_round_picks_and_results() -> tuple[list[dict], list[dict]]:
    """Returns (all match predictions, all matches with results)."""
    svc = get_service_client()
    picks = svc.table("knockout_match_predictions").select("*").execute()
    matches = svc.table("knockout_matches").select("*").execute()
    return picks.data or [], matches.data or []


# ---------------------------------------------------------------------------
# Score snapshots (timeline chart)
# ---------------------------------------------------------------------------

def save_score_snapshot(label: str, rows: list[dict]) -> None:
    """Insert a snapshot row for every user in rows."""
    svc = get_service_client()
    snapshot_rows = [
        {"snapshot_label": label, "user_id": r["user_id"], "total_points": r.get("total_points_calc", 0)}
        for r in rows
    ]
    if snapshot_rows:
        svc.table("score_snapshots").insert(snapshot_rows).execute()


def get_score_snapshots() -> list[dict]:
    """Returns all snapshots joined with profile display_names, ordered by created_at."""
    client = get_client()
    resp = (
        client.table("score_snapshots")
        .select("*, profiles(display_name)")
        .order("created_at")
        .execute()
    )
    return resp.data or []


# ---------------------------------------------------------------------------
# Hot takes
# ---------------------------------------------------------------------------

def get_hot_take(user_id: str) -> str | None:
    client = get_client()
    resp = client.table("hot_takes").select("take").eq("user_id", user_id).execute()
    return resp.data[0]["take"] if resp.data else None


def save_hot_take(user_id: str, take: str) -> None:
    client = get_client()
    client.table("hot_takes").upsert(
        {"user_id": user_id, "take": take},
        on_conflict="user_id",
    ).execute()


def get_all_hot_takes() -> list[dict]:
    """Returns all hot takes joined with display_name, ordered by created_at."""
    client = get_client()
    resp = (
        client.table("hot_takes")
        .select("id, take, created_at, profiles(display_name, favourite_player)")
        .order("created_at")
        .execute()
    )
    return resp.data or []


# ---------------------------------------------------------------------------
# Hot take reactions
# ---------------------------------------------------------------------------

def get_all_reactions() -> list[dict]:
    """Returns all reaction rows: [{hot_take_id, user_id, emoji}]."""
    client = get_client()
    resp = client.table("hot_take_reactions").select("hot_take_id, user_id, emoji").execute()
    return resp.data or []


def toggle_reaction(user_id: str, hot_take_id: str, emoji: str) -> None:
    client = get_client()
    existing = (
        client.table("hot_take_reactions")
        .select("id")
        .eq("user_id", user_id)
        .eq("hot_take_id", hot_take_id)
        .eq("emoji", emoji)
        .execute()
    )
    if existing.data:
        client.table("hot_take_reactions").delete().eq("id", existing.data[0]["id"]).execute()
    else:
        client.table("hot_take_reactions").insert(
            {"user_id": user_id, "hot_take_id": hot_take_id, "emoji": emoji}
        ).execute()


# ---------------------------------------------------------------------------
# Head-to-head helpers
# ---------------------------------------------------------------------------

def get_all_profiles() -> list[dict]:
    """Returns all profiles sorted by display_name."""
    client = get_client()
    resp = (
        client.table("profiles")
        .select("id, display_name, favourite_player")
        .order("display_name")
        .execute()
    )
    return resp.data or []


def get_scores_by_user_id(user_id: str) -> dict | None:
    client = get_client()
    resp = client.table("scores").select("*").eq("user_id", user_id).execute()
    return resp.data[0] if resp.data else None


def get_all_user_round_picks(user_id: str) -> dict[str, str]:
    """Returns {match_id: pick} across all rounds for a user."""
    client = get_client()
    resp = (
        client.table("knockout_match_predictions")
        .select("match_id, pick")
        .eq("user_id", user_id)
        .execute()
    )
    return {r["match_id"]: r["pick"] for r in (resp.data or [])}


# ---------------------------------------------------------------------------
# Rank helpers (used by scoring.py)
# ---------------------------------------------------------------------------

def get_current_ranks() -> dict[str, int]:
    """Returns {user_id: rank} from the current scores table."""
    svc = get_service_client()
    resp = (
        svc.table("scores")
        .select("user_id, rank")
        .execute()
    )
    return {r["user_id"]: r["rank"] for r in (resp.data or []) if r.get("rank")}


# ---------------------------------------------------------------------------
# League management
# ---------------------------------------------------------------------------

def create_league(user_id: str, name: str) -> dict:
    """Create a new league with a random 6-char invite code; auto-joins creator."""
    import random, string
    code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    client = get_client()
    resp = client.table("leagues").insert({
        "name": name,
        "invite_code": code,
        "created_by": user_id,
    }).execute()
    league = resp.data[0]
    client.table("league_members").insert({
        "league_id": league["id"],
        "user_id": user_id,
    }).execute()
    return league


def get_league_by_code(code: str) -> dict | None:
    client = get_client()
    resp = client.table("leagues").select("*").eq("invite_code", code.strip().upper()).execute()
    return resp.data[0] if resp.data else None


def join_league(user_id: str, league_id: str, wager_in: bool = False) -> None:
    client = get_client()
    client.table("league_members").upsert(
        {"league_id": league_id, "user_id": user_id, "wager_in": wager_in},
        on_conflict="league_id,user_id",
    ).execute()


def set_wager_preference(user_id: str, league_id: str, wager_in: bool) -> None:
    """Update a member's wager opt-in for a specific league."""
    svc = get_service_client()
    svc.table("league_members").update(
        {"wager_in": wager_in}
    ).eq("league_id", league_id).eq("user_id", user_id).execute()


def leave_league(user_id: str, league_id: str) -> None:
    client = get_client()
    client.table("league_members").delete().eq("league_id", league_id).eq("user_id", user_id).execute()


def get_user_leagues(user_id: str) -> list[dict]:
    """Returns leagues the user belongs to, each with member_count and wager_in."""
    client = get_client()
    resp = (
        client.table("league_members")
        .select("league_id, wager_in, leagues(id, name, invite_code, created_by)")
        .eq("user_id", user_id)
        .execute()
    )
    leagues = []
    for r in (resp.data or []):
        if r.get("leagues"):
            league = dict(r["leagues"])
            league["wager_in"] = r.get("wager_in", False)
            leagues.append(league)
    for league in leagues:
        count_resp = (
            client.table("league_members")
            .select("user_id", count="exact")
            .eq("league_id", league["id"])
            .execute()
        )
        league["member_count"] = count_resp.count or 0
    return sorted(leagues, key=lambda x: x["name"])


def get_league_member_ids(league_id: str) -> list[str]:
    """Returns list of user_ids in a league."""
    client = get_client()
    resp = client.table("league_members").select("user_id").eq("league_id", league_id).execute()
    return [r["user_id"] for r in (resp.data or [])]


# ---------------------------------------------------------------------------
# Super-admin helpers (service role only)
# ---------------------------------------------------------------------------

def admin_get_user_emails() -> dict[str, str]:
    """Returns {user_id: email} for every registered user."""
    svc = get_service_client()
    try:
        users = svc.auth.admin.list_users()
        return {u.id: (u.email or "") for u in (users or [])}
    except Exception:
        return {}


def admin_get_prediction_coverage() -> list[dict]:
    """Returns per-user prediction completion stats."""
    svc = get_service_client()
    profiles = svc.table("profiles").select("id, display_name, favourite_player, created_at").execute()

    grp = svc.table("group_predictions").select("user_id").execute()
    grp_counts: dict[str, int] = {}
    for r in (grp.data or []):
        uid = r["user_id"]
        grp_counts[uid] = grp_counts.get(uid, 0) + 1

    ko = svc.table("knockout_predictions").select("user_id, golden_boot, golden_ball, golden_glove").execute()
    ko_map = {r["user_id"]: r for r in (ko.data or [])}

    result = []
    for p in (profiles.data or []):
        uid = p["id"]
        ko_row = ko_map.get(uid, {})
        result.append({
            "user_id": uid,
            "display_name": p["display_name"],
            "favourite_player": p.get("favourite_player", ""),
            "created_at": p.get("created_at", ""),
            "groups_done": grp_counts.get(uid, 0),
            "ko_done": uid in ko_map,
            "boot_done": bool(ko_row.get("golden_boot")),
            "ball_done": bool(ko_row.get("golden_ball")),
            "glove_done": bool(ko_row.get("golden_glove")),
        })
    return result


def admin_get_all_leagues() -> list[dict]:
    """Returns all leagues with member display names and wager preferences."""
    svc = get_service_client()
    resp = (
        svc.table("leagues")
        .select("id, name, invite_code, created_at, league_members(user_id, wager_in, profiles(display_name))")
        .order("created_at")
        .execute()
    )
    return resp.data or []


def admin_get_all_hot_takes() -> list[dict]:
    """Returns all hot takes regardless of lock status."""
    svc = get_service_client()
    resp = (
        svc.table("hot_takes")
        .select("take, created_at, profiles(display_name)")
        .order("created_at")
        .execute()
    )
    return resp.data or []
