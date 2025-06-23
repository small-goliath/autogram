from collections import defaultdict
import os
from time import sleep
from typing import List
from dotenv import load_dotenv

import app.core as core
from app.batch import kakaotalk_parsing
from app.batch.notification import Discord
from app.logger import get_logger
from app.model.entity import ActionTarget
from app.util import getOutsiders

log = get_logger("auto_activer")
load_dotenv()
INSTAGRAM_ADMIN = os.environ.get('INSTAGRAM_ADMIN')

# 카카오톡 채팅방 대화내용으로부터 활동내용 피드백
def main():
    discord = Discord()
    count = 0
    
    try:
        insta = core.login_producer(INSTAGRAM_ADMIN)
        target_posts: List[ActionTarget] = kakaotalk_parsing.parsing()
        target_users = core.search_sns_raise_users()
    except Exception as e:
        log.error(f"지난주 활동 내역을 체크할 수 없습니다.")
        discord.send_message(f"지난주 활동 내역을 체크할 수 없습니다: [{e}]")

    log.info(f"{len(target_posts)}개에 대한 품앗이 활동 내용을 체크합니다.")
    for target_post in target_posts:
        link = None
        try:
            if insta.username == str(target_post.username).split('@')[-1]:
                continue

            if count != 0 and count % 5 == 0:
                log.info("1분 중단.")
                sleep(60)
            count += 1

            link = target_post.link
            media_id = insta.get_media_id(link)
            writer_username = insta.get_media(media_id).user.username
            outsiders = getOutsiders()
            if writer_username in outsiders:
                continue
            comments = insta.search_comments(media_id)

            comment_usernames = set(comment.user.username for comment in comments)

            for target_username in target_users:
                if target_username == writer_username:
                    continue
                if target_username not in comment_usernames:
                    try:
                        core.save_user_action_verification(username=target_username, link=link)
                    except Exception as e:
                        discord.send_message(f"{target_username}이 {link} 품앗이를 하지 않았다.")
                        log.error(f"{target_username}이 {link} 품앗이를 하지 않았다: {e}")

        except Exception as e:
            log.error(f"{link} 활동 내역 체크 실패: {e}")
            discord.send_message(f"{link} 활동 내역 체크 실패 [{e}]")
    discord.send_message("품앗이 활동내용 검증이 완료되었습니다.")

if __name__ == "__main__":
    main()
