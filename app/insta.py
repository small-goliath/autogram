import requests
import json
import os
from time import sleep
from urllib.parse import urlencode
from typing import Dict, List
from instagrapi.types import Media, Comment, UserShort
from instagrapi import Client
from app.batch.notification import Discord
from app.exception.custom_exception import CommentError, FollowersError, FollowingsError, LikeError, SearchCommentError
from app.model.entity import Producer, Unfollower
from app.logger import get_logger
import app.util as util

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

            if os.path.exists(self.session_file):
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    self.client.set_settings(content)
            else:
                self.client.set_settings(self.session)
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
        
    def search_followers(self) -> Dict[str, UserShort]:
        try:
            return self.client.user_followers(self.client.user_id)
        except Exception as e:
            self.log.error(f"{self.client.user_id}의 팔로워를 검색할 수 없습니다.")
            raise FollowersError("팔로워 조회를 하지 못했습니다.") from e
    
    def search_followings(self) -> Dict[str, UserShort]:
        try:
            return self.client.user_following(self.client.user_id)
        except Exception as e:
            self.log.error(f"{self.client.user_id}의 팔로잉을 검색할 수 없습니다.")
            raise FollowingsError("팔로잉 조회를 못했습니다.") from e
        
    def search_followers_by_user_id(self, user_id: int) -> Dict[str, UserShort]:
        self.log.info(f"10초 후 {user_id}의 팔로워를 검색합니다.")
        sleep(10)
        try:
            return self.client.user_followers(user_id)
        except Exception as e:
            self.log.error(f"{user_id}의 팔로워를 검색할 수 없습니다 {e}")
            raise FollowersError(f"팔로워 조회를 하지 못했습니다: {e}") from e
    
    def search_followings_by_user_id(self, user_id: int) -> Dict[str, UserShort]:
        self.log.info(f"10초 후 {user_id}의 팔로잉를 검색합니다.")
        sleep(10)
        try:
            return self.client.user_following(user_id)
        except Exception as e:
            self.log.error(f"{user_id}의 팔로잉을 검색할 수 없습니다: {e}")
            raise FollowingsError(f"팔로잉 조회를 못했습니다: {e}") from e
        
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
    
    def search_unfollowers(self, user_id: int) -> List[Unfollower]:
        base_url = "https://www.instagram.com/graphql/query/"
        query_hash = "3dec7e2c57367ef3da3d987d89f9dbc8"
        variables = {
            "id": str(user_id),
            "include_reel": "true",
            "fetch_mutual": "false",
            "first": "24"
        }
        headers = {
            'authorization': self.client.authorization,
            'accept': '*/*',
            'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'priority': 'u=1, i',
            'referer': 'https://www.instagram.com/',
            'sec-ch-prefers-color-scheme': 'dark',
            'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
            'sec-ch-ua-full-version-list': '"Chromium";v="134.0.6998.89", "Not:A-Brand";v="24.0.0.0", "Google Chrome";v="134.0.6998.89"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-model': '""',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua-platform-version': '"10.0.0"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        }
        params = {
            'query_hash': query_hash,
            'variables': json.dumps(variables, separators=(',', ':'))
        }
        cookies = {
            "sessionid": self.client.sessionid
        }
        
        unfollowers = []
        end_cursor: str = None
        csrftoken: str = None
        count = 0
        sleep_amount = 5
        while True:
            if count > sleep_amount:
                sleep(10)
                count = 0
            if end_cursor:
                variables["after"] = end_cursor
            if csrftoken:
                cookies["csrftoken"] = csrftoken
            count += 1
            self.log.info("=== 언팔로워 조회 ===")
            self.log.info(params)
            self.log.info(cookies)
            response = requests.get(base_url, params=params, headers=headers, cookies=cookies)
            response.raise_for_status()
            csrftoken = response.cookies.get("csrftoken")

            data = response.json()["data"]
            if not data["user"] and not unfollowers:
                raise Exception(f"{user_id}의 언팔로워를 조회할 수 없습니다.")
            
            page_info = util.json_value(data, "user", "edge_follow", "page_info", default={})
            edges = util.json_value(data, "user", "edge_follow", "edges", default=[])
            for edge in edges:
                target_user_id = util.json_value(edge, "node", "id", default=None)
                if not target_user_id:
                    continue
                username = util.json_value(edge, "node", "username", default=None)
                nickname = util.json_value(edge, "node", "full_name", default=None)
                profile_uri = util.json_value(edge, "node", "profile_pic_url", default=None)
                followed_by_viewer = util.json_value(edge, "node", "followed_by_viewer", default=False)
                follows_viewer = util.json_value(edge, "node", "profile_pifollows_viewerc_url", default=False)
                if followed_by_viewer and not follows_viewer:
                    unfollowers.append(Unfollower(target_user_id=target_user_id, username=username, nickname=nickname, profile_uri=profile_uri))
            end_cursor = page_info.get("end_cursor")
            if not page_info.get("has_next_page") or not end_cursor:
                break
            
        return unfollowers