from collections import defaultdict
import os
import re
import sys
import locale
from datetime import timedelta
from app.logger import get_logger
from app.batch.notification import Discord
from app.model.model import ActionTarget
from app.util import get_today

# 카카오톡 대화내용 파싱

log = get_logger("kakaotalk_parser")
locale.setlocale(locale.LC_TIME, 'ko_KR.UTF-8')

def get_target_week_dates():
    today = get_today()
    last_monday = today - timedelta(days=today.weekday() + 7)
    this_monday = today - timedelta(days=today.weekday())
    return last_monday, this_monday

def format_date(date):
    return date.strftime("%Y년 %-m월 %-d일 %A")

def parsing() -> list[ActionTarget]:
    kakaotalk_file = "kakaotalk/KakaoTalk_latest.txt"
    log.info(f"Processing file: {kakaotalk_file}")
    if not os.path.exists(kakaotalk_file):
        log.info("최신 카카오톡 대화방 내용이 없습니다.")
        return
    
    start_date, end_date = get_target_week_dates()
    formatted_start = format_date(start_date)
    formatted_end = format_date(end_date)
    log.info(f"타겟은 {formatted_start} 부터 {formatted_end} 전날까지 입니다.")

    is_last_week = False

    try:
        # 대화방 내용 중 지난주 내용만 체크
        chat = ""
        with open(kakaotalk_file, 'r', encoding='utf-8') as f:
            for line in f:
                # chat += line
                if is_last_week:
                    chat += line
                if line.strip() == formatted_start:
                    is_last_week = True
                elif line.strip() == formatted_end:
                    break


        # limit_by_weeks = os.environ.get("LIMIT_BY_WEEKS", "3")
        # 품앗이 대상 피드/릴스 캐치
        message_pattern = re.compile(
            r"""^
            (20\d{2}\.\s*\d{1,2}\.\s*\d{1,2})         # 날짜
            (?:.*?)                                     # 0개 이상의 문자
            ,\s                                       # 콤마와 공백
            (.*?)                                     # 닉네임
            \s*:\s                                    # 공백과 콜론
            (?:(?!20\d{2}\.\s*\d{1,2}\.\s*\d{1,2}).)*?  # 날짜가 아닌 0개 이상의 문자열
            (https://www\.instagram\.com/[^\s\n]+)    # 인스타그램 링크
            \n+                                       # 1개 이상의 줄바꿈
            (?:(?!20\d{2}\.\s*\d{1,2}\.\s*\d{1,2}).)*?  # 날짜가 아닌 0개 이상의 문자열
            /(?P<digit>\d+)
            """,
            re.MULTILINE | re.VERBOSE
        )

        # 인스타그램 링크 맵핑
        action_targets = []
        messages = message_pattern.findall(chat)
        for match in messages:
            action_targets.append(ActionTarget(
                username=match[1],
                link=str(match[2]).strip()
            ))

        return action_targets

    except Exception as e:
        log.error(f"Batch failure: {e}")
        Discord().send_message(message=f"Batch failure: {e}")
        sys.exit(1)
    finally:
        if os.path.exists(kakaotalk_file):
            last_sunday_date = end_date.strftime("%Y-%m-%d")
            new_filename = f"kakaotalk/KakaoTalk_{last_sunday_date}.txt"
            os.rename(kakaotalk_file, new_filename)

if __name__ == "__main__":
    log.info("Parsing KakaoTalk chat history...")
    action_targets = parsing()
    username_links = defaultdict(list)

    for t in action_targets:
        username_links[t.username].append(t.link)

    log.info(f"총 {len(username_links)}개")
    for username, links in username_links.items():
        log.info(f"{username}: {len(links)}개")
        for link in links:
            log.info(link)
