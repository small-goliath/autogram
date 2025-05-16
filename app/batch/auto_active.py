import csv
import os
import sys
from typing import List
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

from app.batch.notification import Discord
from app.exception.custom_exception import CommentError, LikeError
from app.gpt import GPT
from app.insta import Insta
from app.logger import get_logger
from app.database import Database
from app.model.entity import Action

log = get_logger("auto_activer")

def main():
    db = Database()
    gpt = GPT()
    discord = Discord()

    try:
        accounts = db.search_instagram_accounts()
        if not accounts:
            log.warning("실행할 인스타그램 계정이 없습니다.")
            return
        
        actions: List[Action] = []
        for account in accounts:
            insta = Insta(account)
            insta.login()

            try:
                targets = db.search_action_targets(account.id)
                link = ""
                for target in targets:
                    link = target.link
                    media_id = insta.get_media_id(link)
                    media = insta.get_media(media_id)
                    comment = gpt.generate_comment(media.caption_text)
                    insta.comment(media_id, comment)
                    actions.append(Action(action_target_id=target.id, account_id=account.id))
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
                
        db.save_actions(actions=actions)
    except Exception as e:
        log.error(f"배치 실패: {e}")
        discord.send_message(message=f"배치 실패: {e}")

        if len(actions) > 0:
            load_dotenv()
            KST = timezone(timedelta(hours=9))
            filename = f"{os.environ.get('FAILED_ACTIONS_DIR')}/{datetime.now(KST).strftime("%Y-%m-%d")}.csv"
            with open(filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["action_target_id", "account_id"])
                for action in actions:
                    writer.writerow([action.action_target_id, action.account_id])
            log.info(f"저장하지 못한 actions csv 저장: {filename}")

        sys.exit(1)

if __name__ == "__main__":
    main()