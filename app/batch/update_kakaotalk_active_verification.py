import os
import sys
from typing import Set
from dotenv import load_dotenv

from app.core import AutogramCore
from app.batch.notification import Discord
from app.insta import Insta
from app.logger import get_logger
from app.util import sleep_by_count

log = get_logger("auto_activer")
load_dotenv()
FIRST_INSTAGRAM_ADMIN = os.environ.get('FIRST_INSTAGRAM_ADMIN')
SECOND_INSTAGRAM_ADMIN = os.environ.get('SECOND_INSTAGRAM_ADMIN')

def get_commenters(insta: Insta, link: str) -> Set[str]:
    media_id = insta.get_media_id(link)
    comments = insta.search_comments(media_id)
    return set(comment.user.username for comment in comments)

# 카카오톡 채팅방 대화내용으로부터 활동내용 갱신
def main():
    discord = Discord()
    core = AutogramCore()
    count = 0
    challenge_required_count = 0
    
    try:
        insta = core.login_producer(FIRST_INSTAGRAM_ADMIN)
        verifications = core.search_user_action_verifications()
    except Exception as e:
        log.error(f"활동 내역을 갱신할 수 없습니다.")
        discord.send_message(f"활동 내역을 갱신할 수 없습니다: [{e}]")
        sys.exit(1)

    log.info(f"{len(verifications)}개에 대한 품앗이 활동 내용을 갱신합니다.")

    for link, usernames in verifications.items():
        try:
            comment_usernames = get_commenters(insta, link)
        except Exception as e:
            if challenge_required_count > 0:
                log.error(f"{link} 정보 조회 실패: {e}")
                discord.send_message(f"{link} 활동 정보 조회 실패 [{e}]")
                break

            if "challenge_required" in str(e) or "login_required" in str(e):
                log.info(f"admin 계정을 변경합니다: [{e}]")
                challenge_required_count += 1
                insta = core.login_producer(SECOND_INSTAGRAM_ADMIN)
                try:
                    comment_usernames = comment_usernames = get_commenters(insta, link)
                except Exception as e:
                    log.error(f"{link} 정보 조회 실패: {e}")
                    discord.send_message(f"{link} 활동 정보 조회 실패 [{e}]")
                    break
            log.warning(f"정보 조회 실패: {e}")

        for username in usernames:
            try:
                count += 1
                sleep_by_count(count=count, amount=5, sec=60)

                if username in comment_usernames:
                    core.delete_user_action_verification(username=username, link=link)

            except Exception as e:
                log.error(f"{username}의 {link} 활동 내역 갱신 실패: {e}")
                discord.send_message(f"{username}의 {link} 활동 내역 갱신 실패 [{e}]")

if __name__ == "__main__":
    main()
