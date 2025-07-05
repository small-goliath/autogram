import os
import sys
from time import sleep
from typing import List
from dotenv import load_dotenv

from app.core import AutogramCore
from app.batch.notification import Discord
from app.insta import Insta
from app.logger import get_logger
from app.util import get_outsiders, sleep_by_count

log = get_logger("auto_activer")
core = AutogramCore()
load_dotenv()
FIRST_INSTAGRAM_ADMIN = os.environ.get('FIRST_INSTAGRAM_ADMIN')
SECOND_INSTAGRAM_ADMIN = os.environ.get('SECOND_INSTAGRAM_ADMIN')

def update(insta: Insta, link: str, outsiders: List[str]):
    media_id = insta.get_media_id(link)
    media = insta.get_media(media_id)
    if media.user.username in outsiders:
        core.delete_user_action_verification(link=link)

# 결제 안하거나 활동 중단한 이용자 링크 제거
def main():
    discord = Discord()
    count = 0
    challenge_required_count = 0
    
    try:
        insta = core.login_producer(FIRST_INSTAGRAM_ADMIN)
        verifications = core.search_user_action_verifications()
    except Exception as e:
        log.error(f"활동 중단한 이용자 링크 제거할 수 없습니다.")
        discord.send_message(f"활동 중단한 이용자 링크 제거할 수 없습니다: [{e}]")
        sys.exit(1)

    log.info(f"{len(verifications)}개에 대한 링크를 수집합니다.")
    outsiders = get_outsiders()
    log.info(f"탈퇴자: {outsiders}")

    for link, _ in verifications.items():
        try:
            update(insta, link, outsiders)
        except Exception as e:
            if challenge_required_count > 0:
                log.error(f"{link} 정보 조회 실패: {e}")
                discord.send_message(f"{link} 정보 조회 실패 [{e}]")
                break

            if "challenge_required" in str(e):
                challenge_required_count += 1
                insta = core.login_producer(SECOND_INSTAGRAM_ADMIN)
                try :
                    update(insta, link, outsiders)
                except Exception as e:
                    log.error(f"{link} 정보 조회 실패: {e}")
                    discord.send_message(f"{link} 정보 조회 실패 [{e}]")
                    break
        count += 1
        sleep_by_count(count=count, amount=5, sec=10)

if __name__ == "__main__":
    main()
