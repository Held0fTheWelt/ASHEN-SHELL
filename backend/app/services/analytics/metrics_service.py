"""
Real dashboard metrics from persisted user data only.
No fake revenue, sessions, or conversion. Definitions:
- Active now: users with last_seen_at within the last 15 minutes.
- Active users over time: distinct users with last_seen_at in each time bucket.
- User growth: cumulative count of users with created_at <= end of each bucket.
"""
from datetime import timedelta

from sqlalchemy import and_, distinct, func, or_

from app.extensions import db
from app.models import User
from app.utils.time_utils import utc_now as _utc_now

ACTIVE_NOW_WINDOW_MINUTES = 15
RANGE_LAST_DAY = "24h"
RANGE_LAST_WEEK = "7d"
RANGE_LAST_MONTH = "30d"
RANGE_LAST_YEAR = "12m"
VALID_RANGES = (RANGE_LAST_DAY, RANGE_LAST_WEEK, RANGE_LAST_MONTH, RANGE_LAST_YEAR)
LAST_DAY_BUCKET_COUNT = 24
LAST_WEEK_BUCKET_COUNT = 7
LAST_MONTH_BUCKET_COUNT = 30
LAST_YEAR_BUCKET_COUNT = 12
LAST_DAY_DURATION = timedelta(hours=LAST_DAY_BUCKET_COUNT)
CALENDAR_DAY = timedelta(days=1)
LAST_YEAR_LOOKBACK = timedelta(days=365)
APPROX_MONTH_STEP = timedelta(days=LAST_MONTH_BUCKET_COUNT)
BUCKET_LABEL_FORMATS = {
    RANGE_LAST_DAY: "%H:%M",
    RANGE_LAST_WEEK: "%Y-%m-%d",
    RANGE_LAST_MONTH: "%Y-%m-%d",
    RANGE_LAST_YEAR: "%Y-%m",
}


def _daily_ceiling(value):
    return value.replace(hour=0, minute=0, second=0, microsecond=0) + CALENDAR_DAY


def _month_floor(value):
    return value.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def _bucket_series(start, *, bucket_count: int, step: timedelta):
    return [(start + step * index, start + step * (index + 1)) for index in range(bucket_count)]


def _range_end_and_buckets(range_key: str):
    """Return (range_end_utc, list of (bucket_start, bucket_end) in UTC)."""
    now = _utc_now()
    if range_key == RANGE_LAST_DAY:
        return now, _bucket_series(now - LAST_DAY_DURATION, bucket_count=LAST_DAY_BUCKET_COUNT, step=timedelta(hours=1))
    if range_key == RANGE_LAST_WEEK:
        end = _daily_ceiling(now)
        return end, _bucket_series(end - timedelta(days=LAST_WEEK_BUCKET_COUNT), bucket_count=LAST_WEEK_BUCKET_COUNT, step=CALENDAR_DAY)
    if range_key == RANGE_LAST_MONTH:
        end = _daily_ceiling(now)
        return end, _bucket_series(end - timedelta(days=LAST_MONTH_BUCKET_COUNT), bucket_count=LAST_MONTH_BUCKET_COUNT, step=CALENDAR_DAY)
    if range_key == RANGE_LAST_YEAR:
        end = _month_floor(now)
        return end, _bucket_series(end - LAST_YEAR_LOOKBACK, bucket_count=LAST_YEAR_BUCKET_COUNT, step=APPROX_MONTH_STEP)
    return now, []


def get_metrics(range_key: str):
    """
    Return dict: active_now, registered_total, verified_total, banned_total,
    active_users_over_time, user_growth_over_time, selected_range, bucket_info.
    All values from real user data. range_key must be 24h|7d|30d|12m.
    """
    if range_key not in VALID_RANGES:
        range_key = "24h"

    now = _utc_now()
    active_cutoff = now - timedelta(minutes=ACTIVE_NOW_WINDOW_MINUTES)

    active_now = db.session.query(func.count(User.id)).filter(
        User.last_seen_at >= active_cutoff
    ).scalar() or 0

    registered_total = db.session.query(func.count(User.id)).scalar() or 0
    verified_total = db.session.query(func.count(User.id)).filter(
        User.email_verified_at.isnot(None)
    ).scalar() or 0
    banned_total = db.session.query(func.count(User.id)).filter(User.is_banned.is_(True)).scalar() or 0

    range_end, buckets = _range_end_and_buckets(range_key)
    bucket_labels = []
    active_users_over_time = []
    user_growth_over_time = []

    for b_start, b_end in buckets:
        bucket_labels.append(b_start.strftime(BUCKET_LABEL_FORMATS[range_key]))

        active_in_bucket = db.session.query(func.count(distinct(User.id))).filter(
            and_(
                User.last_seen_at >= b_start,
                User.last_seen_at < b_end,
            )
        ).scalar() or 0
        active_users_over_time.append(active_in_bucket)

        growth_at_end = db.session.query(func.count(User.id)).filter(
            or_(User.created_at <= b_end, User.created_at.is_(None))
        ).scalar() or 0
        user_growth_over_time.append(growth_at_end)

    return {
        "active_now": active_now,
        "registered_total": registered_total,
        "verified_total": verified_total,
        "banned_total": banned_total,
        "active_users_over_time": active_users_over_time,
        "user_growth_over_time": user_growth_over_time,
        "selected_range": range_key,
        "bucket_labels": bucket_labels,
        "bucket_info": {
            "range": range_key,
            "bucket_count": len(buckets),
        },
    }
