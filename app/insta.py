import json
import os
from time import sleep
from typing import List
from instagrapi.types import Media, Comment
from instagrapi import Client
from app.batch.notification import Discord
from app.exception.custom_exception import CommentError, FollowersError, FollowingsError, LikeError, SearchCommentError
from app.model.entity import Producer
from app.logger import get_logger

class Insta:
    def __init__(self, account: Producer):
        self.client = Client()
        self.username = account.username
        self.session_file = f"insta_session/{self.username}.json"
        self.session = json.loads(account.session) if account.session else {}
        self.log = get_logger("root")

    def login(self):
        try:
            self.log.info(f"{self.username}으로 로그인을 시도합니다.")

            if self.session:
                try:
                    self.client.set_settings(self.session)
                except:
                    if os.path.exists(self.session_file):
                        with open(self.session_file, 'r', encoding='utf-8') as f:
                            content = json.load(f)
                            self.client.set_settings(content)
            else:
                raise Exception("계정 재등록 필요.")
            self.log.info(f"===== {self.username}으로 로그인하였습니다. =====")
        except Exception as e:
            self.log(f"{self.username} 계정을 로그인할 수 없습니다: {e}")
            message = "인스타그램 로그인 실패"
            embeds = [
                {
                    "fields": [{"name": "username", "value": self.username, "inline": True}],
                    "color": 1127128
                }
            ]
            Discord().send_message_embeds(message=message, embeds=embeds)
        finally:
            self.client.dump_settings(self.session_file)
    def get_user_id(self) -> str:
        return self.client.user_id

    def get_media_id(self, uri: str) -> str:
        media_pk = self.client.media_pk_from_url(uri)
        return  self.client.media_id(media_pk)

    def get_media(self, media_id: str) -> Media:
        return self.client.media_info(media_id)
    
    def comment(self, media_id: str, comment: str):
        self.log.info(f"[{media_id}]피드에 [{comment}] 댓글을 작성합니다.")
        try:
            sleep(1)
            self.client.media_comment(media_id=media_id, text=comment)
        except Exception as e:
            raise CommentError("댓글을 달지 못했습니다.") from e

    def like(self, media_id: str):
        self.log.info(f"[{media_id}]를 좋아요합니다.")
        try:
            sleep(5)
            self.client.media_like(media_id=media_id)
        except Exception as e:
            raise LikeError("좋아요를 하지 못했습니다.") from e
        
    def search_followers(self):
        try:
            return self.client.user_followers(self.client.user_id)
        except Exception as e:
            self.log.error(f"{self.client.user_id}의 팔로워를 검색할 수 없습니다.")
            raise FollowersError("팔로워 조회를 하지 못했습니다.") from e
    
    def search_followings(self):
        try:
            return self.client.user_following(self.client.user_id)
        except Exception as e:
            self.log.error(f"{self.client.user_id}의 팔로잉을 검색할 수 없습니다.")
            raise FollowingsError("팔로잉 조회를 못했습니다.") from e
        
    def exists_comment(self, media_id: str, username: str) -> bool:
        sleep(5)
        try:
            comments: List[Comment] = self.client.media_comments(media_id=media_id)
            return any(comment.user.username == username for comment in comments)
        except Exception as e:
            raise SearchCommentError("댓글을 조회하지 못했습니다.") from e
        
    def search_user_ids(self, username: str) -> str:
        self.log.info(f"user_id를 조회합니다: {username}")
        try:
            return self.client.user_id_from_username(username=username)
        except Exception as e:
            self.log.error(f"{username}의 user_id를 찾을 수 없습니다: {e}")
        
    def search_feeds(self, user_id: str, amount: int) -> List[Media]:
        self.log.info(f"피드를 조회합니다: {user_id}")
        try:
            return self.client.user_medias(user_id=user_id, amount=amount, sleep=3)
        except Exception as e:
            self.log.error(f"{user_id}의 피드를 찾을 수 없습니다: {e}")
    
    def search_feeds_such_user_id(self, username: str, amount: int) -> List[Media]:
        self.log.info(f"{username}의 최신 피드 {amount}개를 조회합니다.")
        target_user_id = self.search_user_ids(username=username)
        return self.search_feeds(user_id=target_user_id, amount=amount)