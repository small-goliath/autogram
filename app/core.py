from collections import defaultdict
import sys
from typing import DefaultDict, List, Optional
from instagrapi.types import Media

from app.batch.notification import Discord
from app.database import Database, read_only_transactional, transactional
from app.exception.custom_exception import CommentError, LikeError, LoginError, SearchCommentError
from app.gpt import GPT
from app.insta import Insta
from app.logger import get_logger
from app.model.entity import UserActionVerification
from app.util import FeedCache, get_formatted_today
from tenacity import retry, stop_after_attempt, wait_fixed

class AutogramCore:
    def __init__(self):
        self.log = get_logger("auto_activer")
        self.db = Database()
        self.discord = Discord()
        self.feed_cache = FeedCache()

    def login_producers(self) -> List[Insta]:
        with transactional() as session:
            producers = self.db.search_producers(session)
            if not producers:
                self.log.warning("실행할 인스타그램 계정이 없습니다.")
                sys.exit(0)
            
            producer_instagrams = []
            for producer in producers:
                producer_instagram = Insta(producer)
                try:
                    producer_instagram.login()
                    producer_instagrams.append(producer_instagram)
                except LoginError as e:
                    self.log.error(f"{producer.username} 로그인 실패: {e}")
                    self.discord.send_message(f"{producer.username} 로그인 실패 [{e}]")
                    continue
                except Exception as e:
                    self.log.error(f"{producer.username} 로그인 중 알 수 없는 오류 발생: {e}")
                    continue

            return producer_instagrams
    def login_producer(self, username: str) -> Insta:
        with transactional() as session:
            producer = self.db.search_producer(username=username, session=session)
            if not producer:
                self.log.warning("실행할 인스타그램 계정이 없습니다.")
                sys.exit(0)
            
            producer_instagram = Insta(producer)
            try:
                producer_instagram.login()
            except Exception as e:
                self.log.error(f"{producer.username} 로그인 실패: {e}")
                self.discord.send_message(f"{producer.username} 로그인 실패 [{e}]")
                sys.exit(1)

            return producer_instagram
        
    def get_consumers(self) -> List[str]:
        with read_only_transactional() as session:
            consumers = self.db.search_consumers(session)
            return [consumer.username for consumer in consumers]
        
    def set_payment(self, username: str, count: int):
        today = get_formatted_today("%Y-%m")
        with transactional() as session:
            payment = self.db.search_payment(session=session, username=username, year_month=today)
            self.log.info(f"{username}의 count를 {count}만큼 더합니다.")
            if payment:
                payment.count += count
                session.add(payment)
            else:
                self.db.create_payment(username=username, count=count, year_month=today)

    def process_feeds(self, producer_instagram: Insta, feeds: List[Media], consumer_username: str) -> int:
        count = 0
        for feed in feeds:
            try:
                self._process_single_feed(producer_instagram, feed)
                count += 1
            except Exception as e:
                self.log_and_notify("처리", producer_instagram, feed, e, consumer_username)
        return count

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(5),
        retry_error_callback=lambda retry_state: retry_state.outcome.exception()
    )
    def _process_single_feed(self, producer_instagram: Insta, feed: Media):
        gpt = GPT()
        try:
            if producer_instagram.exists_comment(media_id=feed.id, username=producer_instagram.username):
                return

            comment = gpt.generate_comment(feed.caption_text)
            producer_instagram.comment(feed.id, comment)
            producer_instagram.like(feed.id)
        except (CommentError, LikeError) as e:
            raise e
        except SearchCommentError as e:
            self.log.warning(f"댓글 조회 실패, 재시도합니다: {e}")
            raise e
        except Exception as e:
            raise e

    def log_and_notify(self, action: str, producer_instagram: Insta, media: Media, error: Exception, consumer_username: str):
        feed_info = f"{media.user.full_name}({consumer_username})의 피드: {media.caption_text}"
        self.log.error(f"{producer_instagram.username} 계정으로 {action} 실패: {feed_info}")
        self.discord.send_message(f"{producer_instagram.username} 계정으로 {feed_info} {action} 실패 [{error}]")

    def action(self):
        producer_instagrams = self.login_producers()
        consumer_usernames = self.get_consumers()
        if not consumer_usernames:
            self.log.warning("실행할 인스타그램 계정이 없습니다.")
            return
        
        for producer_instagram in producer_instagrams:
            for consumer_username in consumer_usernames:
                try:
                    if consumer_username == producer_instagram.username:
                        continue

                    feeds = self.feed_cache.get_feeds(consumer_username, 
                                                      lambda u: producer_instagram.search_feeds_such_user_id(username=u, amount=4))
                    
                    count = self.process_feeds(producer_instagram, feeds, consumer_username)
                    self.set_payment(consumer_username, count)
                except Exception as e:
                    self.log.warning(f"{producer_instagram.username}계정으로 {consumer_username} 액션 실패: {e}")

    def search_sns_raise_users(self) -> List[str]:
        with read_only_transactional() as session:
            users = self.db.search_sns_raise_users(session)
            return [user.username for user in users]

    def save_user_action_verification(self, username: str, link: str):
        with transactional() as session:
            user_action_verification = UserActionVerification(username=username, link=link)

            self.db.save_user_action_verification(session=session, user_action_verification=user_action_verification)

    def search_user_action_verifications(self) -> DefaultDict[str, List[str]]:
        with read_only_transactional() as session:
            verifications = self.db.search_user_action_verifications(session)
            verifications_dict = defaultdict(list)

            for verification in verifications:
                verifications_dict[verification.link].append(verification.username)

            return verifications_dict
        
    def delete_user_action_verification(self, username: Optional[str] = None, link: str = None):
        with transactional() as session:
            if username:
                self.log.info(f"{username}이 {link}에 품앗이를 했습니다. 갱신합니다. 스르륵...")
            else:
                self.log.info(f"{link}는 탈퇴자 링크입니다. 삭제합니다. 스르륵...")
            deleted_count = self.db.delete_user_action_verification(session=session, username=username, link=link)
            self.log.info(f"삭제된 row 수: {deleted_count}")
