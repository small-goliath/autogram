import locale
from datetime import datetime, timedelta, timezone

def get_today() -> datetime:
    locale.setlocale(locale.LC_TIME, 'ko_KR.UTF-8')
    KST = timezone(timedelta(hours=9))
    return datetime.now(KST)

def get_formatted_today(format: str) -> datetime:
    return get_today().strftime(format)