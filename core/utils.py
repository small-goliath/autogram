"""
Core utility functions.
"""

from datetime import datetime, timezone, timedelta


# KST (Korea Standard Time) timezone
KST = timezone(timedelta(hours=9))


def get_kst_now() -> datetime:
    """
    현재 KST (Korea Standard Time) 시간을 반환합니다 (timezone-naive).

    PostgreSQL의 TIMESTAMP (WITHOUT TIME ZONE) 컬럼과 호환되도록
    timezone 정보를 제거한 KST 시간을 반환합니다.

    Returns:
        timezone-naive KST datetime 객체
    """
    return datetime.now(KST).replace(tzinfo=None)
