import locale
import codecs
from datetime import datetime, timedelta, timezone
import os
from time import sleep
from typing import Callable, Dict, List
from dotenv import load_dotenv
from instagrapi.types import Media

from app.logger import get_logger

log = get_logger("root")

class FeedCache:
    def __init__(self):
        self._cache: Dict[str, List[Media]] = {}

    def get_feeds(self, username: str, search_feeds_func: Callable[[str], List[Media]]) -> List[Media]:
        if username not in self._cache:
            self._cache[username] = search_feeds_func(username)
        return self._cache[username]

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
    
def get_outsiders() -> List[str]:
    load_dotenv()
    return [item.strip() for item in os.getenv('OUTSIDERS', '').split(',') if item.strip()]
    
def sleep_by_count(count: int, amount: int, sec: int):
    if count % amount == 0:
        sleep_to_log(sec)

def sleep_to_log(sec: int):
    log.info(f"{sec}초 중단.")
    sleep(sec)