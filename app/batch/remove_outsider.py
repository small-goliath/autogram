import os
from time import sleep
from dotenv import load_dotenv

import app.core as core
from app.batch.notification import Discord
from app.logger import get_logger
from app.util import get_outsiders, sleep_by_count

log = get_logger("auto_activer")
load_dotenv()
INSTAGRAM_ADMIN = os.environ.get('INSTAGRAM_ADMIN')

# 결제 안하거나 활동 중단한 이용자 링크 제거
def main():
    discord = Discord()
    count = 0
    
    try:
        insta = core.login_producer(INSTAGRAM_ADMIN)
        verifications = core.search_user_action_verifications()
    except Exception as e:
        log.error(f"활동 중단한 이용자 링크 제거할 수 없습니다.")
        discord.send_message(f"활동 중단한 이용자 링크 제거할 수 없습니다: [{e}]")

    log.info(f"{len(verifications)}개에 대한 링크를 수집합니다.")
    outsiders = get_outsiders()
    log.info(f"탈퇴자: {outsiders}")

    for link, _ in verifications.items():
        try:
            media_id = insta.get_media_id(link)
            media = insta.get_media(media_id)
            if media.user.username in outsiders:
                core.delete_user_action_verification(link=link)
        except Exception as e:
                log.error(f"{link} 정보 조회 실패: {e}")
                discord.send_message(f"{link} 정보 조회 실패 [{e}]")
                continue
        count += 1
        sleep_by_count(count=count, amount=5, sec=10)

if __name__ == "__main__":
    main()
