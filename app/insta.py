import json
import os
from time import sleep
from typing import List
from instagrapi.types import Media, Comment
from instagrapi import Client
from app.exception.custom_exception import CommentError, LikeError, SearchCommentError
from app.model.entity import Producer
from app.logger import get_logger
from app.util import sleep_by_count

import json
import os
from time import sleep
from typing import List
from instagrapi.types import Media, Comment
from instagrapi import Client
from app.exception.custom_exception import CommentError, LikeError, LoginError, SearchCommentError
from app.model.entity import Producer
from app.logger import get_logger
from app.util import sleep_by_count, sleep_to_log

class Insta:
    LIKE_SLEEP_SEC = 5
    COMMENT_SLEEP_SEC = 1
    SEARCH_COMMENT_SLEEP_SEC = 10
    SEARCH_FEEDS_SLEEP_SEC = 3

    def __init__(self, account: Producer):
        self.username = account.username
        self.session_file = f"insta_session/{self.username}.json"
        self.session = json.loads(account.session) if account.session else {}
        self.client = Client()
        self.log = get_logger("root")

    def load_settings(self) -> dict:
        if os.path.exists(self.session_file):
            self.client.load_settings(self.session_file)
        else:
            self.client.set_settings(self.session)

    def login(self):
        try:
            self.log.info(f"{self.username}으로 로그인을 시도합니다.")
            self.load_settings()
            self.log.info(f"===== {self.username}으로 로그인하였습니다. =====")
        except Exception as e:
            raise LoginError(f"{self.username} 계정을 로그인할 수 없습니다.") from e
        finally:
            self.client.dump_settings(self.session_file)
    def get_user_id(self) -> str:
        return self.client.user_id

    def get_media_id(self, uri: str) -> str:
        media_pk = self.client.media_pk_from_url(uri)
        return  self.client.media_id(media_pk)

    def get_media(self, media_id: str) -> Media:
        self.log.info(f"{media_id}의 정보를 조회합니다.")
        return self.client.media_info(media_id)
    
    def comment(self, media_id: str, comment: str):
        self.log.info(f"[{media_id}]피드에 [{comment}] 댓글을 작성합니다.")
        try:
            sleep_to_log(self.COMMENT_SLEEP_SEC)
            self.client.media_comment(media_id=media_id, text=comment)
        except Exception as e:
            raise CommentError("댓글을 달지 못했습니다.") from e

    def like(self, media_id: str):
        self.log.info(f"[{media_id}]를 좋아요합니다.")
        try:
            sleep_to_log(self.LIKE_SLEEP_SEC)
            self.client.media_like(media_id=media_id)
        except Exception as e:
            raise LikeError("좋아요를 하지 못했습니다.") from e

    def search_comments(self, media_id: str) -> List[Comment]:
        self.log.info(f"{media_id}의 댓글을 조회합니다.")
        try:
            comments: List[Comment] = []
            next_min_id = None
            count = 0
            while True:
                count += 1
                comments_part, next_min_id = self.client.media_comments_chunk(media_id=media_id, max_amount=10, min_id=next_min_id)
                comments.extend(comments_part)
                sleep_to_log(self.SEARCH_COMMENT_SLEEP_SEC)
                if not next_min_id:
                    break
                sleep_by_count(count=count, amount=5, sec=20)
            return comments
        except Exception as e:
            self.log.error(f"{media_id} 댓글 조회 중 오류 발생: {e}")
            raise SearchCommentError(f"댓글을 조회하지 못했습니다: {e}") from e
        
    def exists_comment(self, media_id: str, username: str) -> bool:
        sleep_to_log(self.SEARCH_COMMENT_SLEEP_SEC)
        try:
            comments: List[Comment] = self.search_comments(media_id=media_id)
            return any(comment.user.username == username for comment in comments)
        except Exception as e:
            raise SearchCommentError("댓글을 조회���지 못했습니다.") from e
        
    def search_user_ids(self, username: str) -> str:
        self.log.info(f"user_id를 조회합니다: {username}")
        try:
            return self.client.user_id_from_username(username=username)
        except Exception as e:
            self.log.error(f"{username}의 user_id를 찾을 수 없습니다: {e}")
        
    def search_feeds(self, user_id: str, amount: int) -> List[Media]:
        self.log.info(f"피드를 조회합니다: {user_id}")
        try:
            return self.client.user_medias(user_id=user_id, amount=amount, sleep=self.SEARCH_FEEDS_SLEEP_SEC)
        except Exception as e:
            self.log.error(f"{user_id}의 피드를 찾을 수 없습니다: {e}")
    
    def search_feeds_such_user_id(self, username: str, amount: int) -> List[Media]:
        self.log.info(f"{username}의 최신 피드 {amount}개를 조회합니다.")
        target_user_id = self.search_user_ids(username=username)
        return self.search_feeds(user_id=target_user_id, amount=amount)