import json
import os
import sys
from typing import List
from instagrapi.types import Media
from dotenv import load_dotenv

from app.batch.notification import Discord
from app.database import Database, read_only_transactional, transactional
from app.exception.custom_exception import CommentError, LikeError, SearchCommentError
from app.gpt import GPT
from app.insta import Insta
from app.logger import get_logger
from app.util import get_formatted_today

log = get_logger("auto_activer")
db = Database()
discord = Discord()

def login_producers() -> List[Insta]:
    with transactional() as session:
        producers = db.search_producers(session)
        if not producers:
            log.warning("실행할 인스타그램 계정이 없습니다.")
            sys.exit(0)
        
        producer_instagrams = []
        for producer in producers:
            producer_instagram = Insta(producer)
            try:
                producer_instagram.login()
                producer_instagrams.append(producer_instagram)
            except Exception as e:
                log.error(f"{producer.username} 로그인 실패: {e}")
                discord.send_message(f"{producer.username} 로그인 실패 [{e}]")
                continue

        return producer_instagrams
    
def get_consumers() -> List[str]:
    with read_only_transactional() as session:
        consumers = db.search_consumers(session)
        return [consumer.username for consumer in consumers]
    
def set_payment(username: str, count: int):
    today = get_formatted_today("%Y-%m")
    with transactional() as session:
        payment = db.search_payment(session=session, username=username, year_month=today)
        log.info(f"{username}의 count를 {count}만큼 더합니다.")
        payment.count += count
        session.add(payment)

def process_feeds(producer_instagram: Insta, feeds: List[Media]) -> int:
    count = 0
    gpt = GPT()
    for feed in feeds:
        try:
            if producer_instagram.exists_comment(media_id=feed.id, username=producer_instagram.username):
                continue

            comment = gpt.generate_comment(feed.caption_text)
            producer_instagram.comment(feed.id, comment)
            producer_instagram.like(feed.id)
            count += 1
        except SearchCommentError as e:
            log_and_notify("댓글조회", producer_instagram, feed, e)
        except CommentError as e:
            log_and_notify("댓글달기", producer_instagram, feed, e)
        except LikeError as e:
            log_and_notify("좋아요", producer_instagram, feed, e)
        except Exception as e:
            log_and_notify("댓글/좋아요", producer_instagram, feed, e)
    return count

def log_and_notify(action: str, producer_instagram: Insta, media: Media, error: Exception):
    feed_info = f"{media.user.full_name}의 피드: {media.caption_text}"
    log.error(f"{producer_instagram.username} 계정으로 {action} 실패: {feed_info}")
    discord.send_message(f"{producer_instagram.username} 계정으로 {feed_info} {action} 실패 [{error}]")

def action():
    producer_instagrams = login_producers()
    consumer_usernames = get_consumers()
    if not consumer_usernames:
        log.warning("실행할 인스타그램 계정이 없습니다.")
        return
    
    target_feeds = {}
    for producer_instagram in producer_instagrams:
        for consumer_username in consumer_usernames:
            try:
                if consumer_username == producer_instagram.username:
                    continue

                if consumer_username not in target_feeds:
                    target_feeds[consumer_username] = producer_instagram.search_feeds_such_user_id(username=consumer_username, amount=4)
                
                count = process_feeds(producer_instagram, target_feeds[consumer_username])
                set_payment(consumer_username, count)
            except Exception as e:
                log.warning(f"{producer_instagram}계정으로 {consumer_username} 액션 실패: {e}")

def login_producer(username: str) -> Insta:
    with transactional() as session:
        producer = db.search_producer(username=username, session=session)
        if not producer:
            log.warning("실행할 인스타그램 계정이 없습니다.")
            sys.exit(0)
        
        producer_instagram = Insta(producer)
        try:
            producer_instagram.login()
        except Exception as e:
            log.error(f"{producer.username} 로그인 실패: {e}")
            discord.send_message(f"{producer.username} 로그인 실패 [{e}]")

        return producer_instagram
    
def save_unfollowers():
    load_dotenv()
    user_id_map = json.loads(os.getenv("USER_ID_MAP"))
    admin_username = "_doto.ri_"

    producer_instagram = login_producer(username=admin_username)
    with read_only_transactional() as session:
        target_users = db.search_unfollower_users(session)
        if not target_users:
            log.warning("실행할 인스타그램 계정이 없습니다.")
            return
        
    for target_user in target_users:
        target_username = target_user['username']
        try:
            user_id = user_id_map[target_username]
            unfollowers = producer_instagram.search_unfollowers(user_id)
            
            with transactional() as session:
                db.delete_all_unfollowers(session=session, user_id=target_user['id'])
                if unfollowers:
                    db.save_unfollowers(session=session, unfollowers=unfollowers)
        except Exception as e:
            log.warning(f"{target_username} 언팔 조회 실패: {e}")
            discord.send_message(f"{target_username} 언팔 조회 실패: {e}")
            raise e
