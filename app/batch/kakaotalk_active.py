import sys
from time import sleep
from typing import List
from warnings import deprecated

import app.core as core
from app.batch import kakaotalk_parsing
from app.batch.notification import Discord
from app.exception.custom_exception import CommentError, LikeError
from app.gpt import GPT
from app.insta import Insta
from app.logger import get_logger
from app.database import Database
from app.model.entity import InstagramAccount

log = get_logger("auto_activer")

# 카카오톡 채팅방 대화내용으로부터 일괄 댓글/좋아요
def main():
    db = Database()
    gpt = GPT()
    discord = Discord()

    try:
        accounts = core.search_instagram_accounts()
        if not accounts:
            log.warning("실행할 인스타그램 계정이 없습니다.")
            return
        
        for account in accounts:
            account = InstagramAccount(id=account['id'], username=account['username'], session=account['session'])
            if account.username != "doto.ri_":
                continue
            insta = Insta(account)
            insta.login()

            count = 0

            try:
                targets = kakaotalk_parsing.parsing()
                for target in targets:
                    count += 1
                    if account.username in target.username:
                        continue
                    if count % 5 == 0:
                        log.info("1분 중단.")
                        sleep(60)

                    link = target.link
                    media_id = insta.get_media_id(link)
                    if insta.exists_comment(media_id=media_id, username=account.username):
                        continue
                    media = insta.get_media(media_id)
                    comment = gpt.generate_comment(media.caption_text)
                    insta.comment(media_id, comment)
                    insta.like(media_id)
            except CommentError as e:
                log.error(f"{account.id} 계정으로 {link} 댓글달기 실패.")
                discord.send_message(f"{account.id} 계정으로 {link} 댓글달기 실패 [{e}]")
            except LikeError as e:
                log.error(f"{account.id} 계정으로 {link} 좋아요 실패.")
                discord.send_message(f"{account.id} 계정으로 {link} 좋아요 실패 [{e}]")
            except Exception as e:
                log.error(f"{account.id} 계정으로 {link} 품앗이 실패.")
                discord.send_message(f"{account.id} 계정으로 {link} 품앗이 실패 [{e}]")
    except Exception as e:
        log.error(f"배치 실패: {e}")
        discord.send_message(message=f"배치 실패: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
