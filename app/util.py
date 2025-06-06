import locale
import codecs
from datetime import datetime, timedelta, timezone

def get_today() -> datetime:
    locale.setlocale(locale.LC_TIME, 'ko_KR.UTF-8')
    KST = timezone(timedelta(hours=9))
    return datetime.now(KST)

def get_formatted_today(format: str) -> datetime:
    return get_today().strftime(format)

def json_value(data, *args, default=None):
    cur = data
    for a in args:
        try:
            if isinstance(a, int):
                cur = cur[a]
            else:
                cur = cur.get(a)
        except (IndexError, KeyError, TypeError, AttributeError):
            return default
    return cur

def decode(raw_data, default: str = None) -> str:
    if not raw_data:
        return ""

    try:
        return codecs.decode(raw_data, 'unicode_escape').encode('latin1').decode('utf-8')
    except :
        return default