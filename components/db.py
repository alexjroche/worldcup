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
    user_id: str, winner: str, finalist: str, semi_1: str, semi_2: str, golden_boot: str
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
        },
        on_conflict="user_id",
    ).execute()


# ---------------------------------------------------------------------------
# Leaderboard queries
# ---------------------------------------------------------------------------

def get_leaderboard() -> list[dict]:
    """Returns profiles joined with scores, sorted by total_points desc."""
    client = get_client()
    resp = (
        client.table("scores")
        .select("*, profiles(display_name, favourite_player)")
        .order("total_points", desc=True)
        .execute()
    )
    return resp.data or []


def get_submission_counts() -> list[dict]:
    """Returns per-user group submission counts + knockout submitted flag."""
    client = get_client()
    # group counts
    grp = (
        client.table("group_predictions")
        .select("user_id", count="exact")
        .execute()
    )
    # knockout submitted
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

    # join with profiles
    profile_resp = client.table("profiles").select("id, display_name, favourite_player").execute()
    result = []
    for p in (profile_resp.data or []):
        uid = p["id"]
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


def save_knockout_results(winner: str, finalist: str, semi_1: str, semi_2: str, golden_boot: str) -> None:
    svc = get_service_client()
    svc.table("knockout_results").upsert(
        {"id": 1, "winner": winner, "finalist": finalist, "semi_1": semi_1, "semi_2": semi_2, "golden_boot": golden_boot},
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
