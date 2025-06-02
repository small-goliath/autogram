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
    count = 0
    
    try:
        insta = core.login_producer("doto.ri_")
        targets = kakaotalk_parsing.parsing()
        for target in targets:
            count += 1
            if insta.username in target.username:
                continue
            if count % 5 == 0:
                log.info("1분 중단.")
                sleep(60)

            link = target.link
            media_id = insta.get_media_id(link)
            if insta.exists_comment(media_id=media_id, username=insta.username):
                continue
            media = insta.get_media(media_id)
            comment = gpt.generate_comment(media.caption_text)
            insta.comment(media_id, comment)
            insta.like(media_id)
    except CommentError as e:
        log.error(f"{insta.username} 계정으로 {link} 댓글달기 실패.")
        discord.send_message(f"{insta.username} 계정으로 {link} 댓글달기 실패 [{e}]")
    except LikeError as e:
        log.error(f"{insta.username} 계정으로 {link} 좋아요 실패.")
        discord.send_message(f"{insta.username} 계정으로 {link} 좋아요 실패 [{e}]")
    except Exception as e:
        log.error(f"{insta.username} 계정으로 {link} 품앗이 실패.")
        discord.send_message(f"{insta.username} 계정으로 {link} 품앗이 실패 [{e}]")

if __name__ == "__main__":
    main()
