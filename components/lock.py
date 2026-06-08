import datetime

# First match: Mexico vs — June 11 2026, kickoff ~18:00 UTC
LOCK_TIME = datetime.datetime(2026, 6, 11, 18, 0, 0, tzinfo=datetime.timezone.utc)


def is_locked() -> bool:
    return datetime.datetime.now(datetime.timezone.utc) >= LOCK_TIME


def time_until_lock() -> str:
    now = datetime.datetime.now(datetime.timezone.utc)
    delta = LOCK_TIME - now
    if delta.total_seconds() <= 0:
        return "Predictions are locked — tournament has started!"
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    parts.append(f"{minutes}m")
    return f"{'  '.join(parts)} until predictions lock"
