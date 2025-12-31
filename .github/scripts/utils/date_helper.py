"""
Date utility functions for batch processing
"""

from datetime import datetime, timedelta


def get_target_week_dates() -> tuple[datetime, datetime]:
    """
    지난주의 시작일과 종료일을 반환합니다.
    월요일을 주의 시작으로 가정합니다.

    Returns:
        (start_date, end_date): 지난주 월요일, 이번주 월요일
    """
    today = datetime.now()

    # 이번주 월요일
    days_since_monday = today.weekday()
    this_monday = today - timedelta(days=days_since_monday)

    # 지난주 월요일
    last_monday = this_monday - timedelta(days=7)

    return last_monday, this_monday


def format_date(date: datetime) -> str:
    """
    카카오톡 대화방 형식으로 날짜를 포맷합니다.

    Args:
        date: datetime 객체

    Returns:
        "2024. 10. 21." 형식의 문자열
    """
    return f"{date.year}. {date.month}. {date.day}."


def get_week_start_date() -> datetime.date:
    """
    현재 주의 시작일(월요일)을 반환합니다.

    Returns:
        주의 시작일 (date 객체)
    """
    today = datetime.now()
    days_since_monday = today.weekday()
    monday = today - timedelta(days=days_since_monday)
    return monday.date()
