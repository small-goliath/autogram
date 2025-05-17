import json
import os
from instagrapi.types import Media
from instagrapi import Client
from app.batch.notification import Discord
from app.exception.custom_exception import CommentError, FollowersError, FollowingsError, LikeError
from app.model.entity import InstagramAccount
from app.logger import get_logger

class Insta:
    def __init__(self, account: InstagramAccount):
        self.client = Client()
        self.username = account.username
        self.password = account.password
        self.session_file = f"insta_session/{self.username}.json"
        self.session = json.loads(account.session) if account.session else {}
        self.log = get_logger("root")

    def login(self):
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    self.client.set_settings(content)
            else:
                if self.session:
                    self.client.set_settings(self.session)
                else:
                    self.client.login(self.username, self.password)

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

    def get_media_id(self, uri: str) -> str:
        media_pk = self.client.media_pk_from_url(uri)
        return  self.client.media_id(media_pk)

    def get_media(self, media_id: str) -> Media:
        return self.client.media_info(media_id)
    
    def comment(self, media_id: str, comment: str):
        try:
            self.client.media_comment(media_id=media_id, text=comment)
        except Exception as e:
            raise CommentError("댓글을 달지 못했습니다.") from e

    def like(self, media_id: str):
        try:
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
