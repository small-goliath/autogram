import os
import re
import sys
import locale
from datetime import datetime, timedelta, timezone
from app.model.entity import ActionTarget
from app.logger import get_logger
from app.batch.notification import Discord
from app.database import Database

log = get_logger("kakaotalk_parser")
locale.setlocale(locale.LC_TIME, 'ko_KR.UTF-8')

def get_target_week_dates():
    KST = timezone(timedelta(hours=9))
    today = datetime.now(KST)
    last_monday = today - timedelta(days=today.weekday() + 7)
    this_monday = today - timedelta(days=today.weekday())
    return last_monday, this_monday

def format_date(date):
    return date.strftime("--------------- %Y년 %-m월 %-d일 %A ---------------")

def main():
    db = Database()
    kakaotalk_file = "kakaotalk/KakaoTalk_latest.txt"
    log.info(f"Processing file: {kakaotalk_file}")
    if not os.path.exists(kakaotalk_file):
        log.info("최신 카카오톡 대화방 내용이 없습니다.")
        return
    
    last_monday, this_monday = get_target_week_dates()
    formatted_last_monday = format_date(last_monday)
    formatted_this_monday = format_date(this_monday)
    log.info(f"타겟은 {formatted_last_monday} 부터 {formatted_this_monday} 전날까지 입니다.")

    is_last_week = False

    try:
        # 대화방 내용 중 지난주 내용만 체크
        chat = ""
        with open(kakaotalk_file, 'r', encoding='utf-8') as f:
            for line in f:
                if is_last_week:
                    chat += line
                if line.strip() == formatted_last_monday:
                    is_last_week = True
                elif line.strip() == formatted_this_monday:
                    is_last_week = False

        # 품앗이 대상 피드/릴스 캐치
        limit_by_weeks = os.environ.get("LIMIT_BY_WEEKS", "3")
        message_pattern = re.compile(
            fr"\[(.*?)\] \[오. (.*?)\]\s*(.*?)\s*(https://www\.instagram\.com[^\s]+)\s*((?:.|\n)*?/{re.escape(limit_by_weeks)})",
            re.MULTILINE
        )

        # 인스타그램 링크 맵핑
        action_targets = []
        messages = message_pattern.findall(chat)
        for match in messages:
            action_targets.append(ActionTarget(
                username=str(match[0]).split("@")[1],
                link=str(match[3]).strip(),
                monday=last_monday.strftime("%Y-%m-%d"),
                sunday=(this_monday - timedelta(days=1)).strftime("%Y-%m-%d")
            ))

        db.save_action_targets(action_targets)
    except Exception as e:
        log.error(f"Batch failure: {e}")
        Discord().send_message(message=f"Batch failure: {e}")
        sys.exit(1)
    finally:
        if os.path.exists(kakaotalk_file):
            last_sunday_date = this_monday.strftime("%Y-%m-%d")
            new_filename = f"kakaotalk/KakaoTalk_{last_sunday_date}.txt"
            os.rename(kakaotalk_file, new_filename)

if __name__ == "__main__":
    log.info("Parsing KakaoTalk chat history...")
    main()