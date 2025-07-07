from typing import List

from app.core import AutogramCore
from app.batch import kakaotalk_parsing
from app.batch.notification import Discord
from app.exception.custom_exception import CommentError, LikeError
from app.gpt import GPT
from app.insta import Insta
from app.logger import get_logger
from app.model.model import ActionTarget
from app.util import get_outsiders, sleep_by_count

log = get_logger("auto_activer")

# 카카오톡 채팅방 대화내용으로부터 일괄 댓글/좋아요
def main():
    gpt = GPT()
    discord = Discord()
    count = 0
    targets: List[ActionTarget] = []
    insta: Insta = None
    core = AutogramCore()

    try:
        insta = core.login_producer("doto.ri_")
        targets = kakaotalk_parsing.parsing()
    except Exception as e:
        log.error(f"품앗이를 할 수 없습니다.")
        discord.send_message(f"품앗이를 할 수 없습니다: [{e}]")

    for target in targets:
        try:
            count += 1
            if insta.username in str(target.username).split('@')[-1]:
                continue
            sleep_by_count(count=count, amount=5, sec=60)

            link = target.link
            media_id = insta.get_media_id(link)
            if insta.exists_comment(media_id=media_id, username=insta.username):
                continue
            media = insta.get_media(media_id)
            outsiders = get_outsiders()
            if media.user.username in outsiders:
                continue
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
