import os
from time import sleep
from dotenv import load_dotenv

import app.core as core
from app.batch.notification import Discord
from app.logger import get_logger

log = get_logger("auto_activer")
load_dotenv()
INSTAGRAM_ADMIN = os.environ.get('INSTAGRAM_ADMIN')

# 카카오톡 채팅방 대화내용으로부터 활동내용 갱신
def main():
    discord = Discord()
    count = 0
    
    try:
        insta = core.login_producer(INSTAGRAM_ADMIN)
        verifications = core.search_user_action_verifications()
    except Exception as e:
        log.error(f"활동 내역을 갱신할 수 없습니다.")
        discord.send_message(f"활동 내역을 갱신할 수 없습니다: [{e}]")

    log.info(f"{len(verifications)}개에 대한 품앗이 활동 내용을 갱신합니다.")

    for link, usernames in verifications.items():
        try:
            media_id = insta.get_media_id(link)
            comments = insta.search_comments(media_id)
            comment_usernames = set(comment.user.username for comment in comments)
        except Exception as e:
                log.error(f"{username}의 {link} 정보 조회 실패: {e}")
                discord.send_message(f"{username}의 {link} 활동 정보 조회 실패 [{e}]")

        for username in usernames:
            try:
                if count != 0 and count % 5 == 0:
                    log.info("1분 중단.")
                    sleep(60)
                count += 1

                if username in comment_usernames:
                    core.delete_user_action_verification(username, link)

            except Exception as e:
                log.error(f"{username}의 {link} 활동 내역 갱신 실패: {e}")
                discord.send_message(f"{username}의 {link} 활동 내역 갱신 실패 [{e}]")

if __name__ == "__main__":
    main()
