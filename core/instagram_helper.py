"""Instagram helper functions using instaloader and instagrapi."""
import os
import pickle
from typing import Optional, List
from datetime import datetime
import instaloader
from instagrapi import Client
from instagrapi.exceptions import LoginRequired

from core.config import settings
from core.security import decrypt_password


class InstagramHelper:
    """Helper class for Instagram operations using instaloader (read-only)."""

    def __init__(self):
        self.loader = instaloader.Instaloader()
        self.session_dir = settings.HELPER_SESSION_DIR
        os.makedirs(self.session_dir, exist_ok=True)

    def login_with_session(self, username: str, session_data: Optional[str] = None) -> bool:
        """
        Login using saved session data.

        Args:
            username: Instagram username
            session_data: Pickled session data (optional)

        Returns:
            True if login successful
        """
        try:
            if session_data:
                # Load session from database
                session_file = os.path.join(self.session_dir, f"{username}_session")
                with open(session_file, 'wb') as f:
                    f.write(session_data.encode() if isinstance(session_data, str) else session_data)

                self.loader.load_session_from_file(username, session_file)
            else:
                # Try to load session from file
                self.loader.load_session_from_file(username)

            return True
        except Exception as e:
            print(f"Failed to login with session: {e}")
            return False

    def login_with_password(self, username: str, password: str) -> tuple[bool, Optional[bytes]]:
        """
        Login with username and password, save session.

        Args:
            username: Instagram username
            password: Instagram password

        Returns:
            Tuple of (success: bool, session_data: bytes)
        """
        try:
            self.loader.login(username, password)

            # Save session
            session_file = os.path.join(self.session_dir, f"{username}_session")
            self.loader.save_session_to_file(session_file)

            # Read session data to save in database
            with open(session_file, 'rb') as f:
                session_data = f.read()

            return True, session_data
        except Exception as e:
            print(f"Failed to login with password: {e}")
            return False, None

    def get_post_comments(self, post_shortcode: str) -> List[dict]:
        """
        Get all comments from a post.

        Args:
            post_shortcode: Instagram post shortcode (from URL)

        Returns:
            List of comment dictionaries with 'username' and 'text'
        """
        try:
            post = instaloader.Post.from_shortcode(self.loader.context, post_shortcode)
            comments = []

            for comment in post.get_comments():
                comments.append({
                    'username': comment.owner.username,
                    'text': comment.text,
                    'created_at': comment.created_at_utc
                })

            return comments
        except Exception as e:
            print(f"Failed to get post comments: {e}")
            return []

    def extract_shortcode_from_url(self, url: str) -> Optional[str]:
        """
        Extract shortcode from Instagram URL.

        Args:
            url: Instagram post URL

        Returns:
            Shortcode or None
        """
        try:
            # URLs like: https://www.instagram.com/p/SHORTCODE/ or /reel/SHORTCODE/
            parts = url.rstrip('/').split('/')
            if 'p' in parts or 'reel' in parts:
                idx = parts.index('p') if 'p' in parts else parts.index('reel')
                return parts[idx + 1]
            return None
        except Exception:
            return None


class InstagramCommentBot:
    """Bot for writing comments using instagrapi."""

    def __init__(self):
        self.client = Client()
        self.session_dir = settings.HELPER_SESSION_DIR
        os.makedirs(self.session_dir, exist_ok=True)

    def login_with_session(self, username: str, session_data: Optional[str] = None) -> bool:
        """Login using saved session."""
        try:
            if session_data:
                session_file = os.path.join(self.session_dir, f"{username}_instagrapi_session.json")
                with open(session_file, 'w') as f:
                    f.write(session_data)

                self.client.load_settings(session_file)
                self.client.login(username, "")  # Login with session

            return True
        except Exception as e:
            print(f"Failed to login with session: {e}")
            return False

    def login_with_password(self, username: str, password: str, verification_code: Optional[str] = None) -> tuple[bool, Optional[str]]:
        """
        Login with username and password.

        Args:
            username: Instagram username
            password: Instagram password (encrypted)
            verification_code: 2FA code if required

        Returns:
            Tuple of (success: bool, session_data: str)
        """
        try:
            decrypted_password = decrypt_password(password)

            if verification_code:
                self.client.login(username, decrypted_password, verification_code=verification_code)
            else:
                self.client.login(username, decrypted_password)

            # Save session
            session_file = os.path.join(self.session_dir, f"{username}_instagrapi_session.json")
            self.client.dump_settings(session_file)

            with open(session_file, 'r') as f:
                session_data = f.read()

            return True, session_data
        except Exception as e:
            print(f"Failed to login: {e}")
            return False, None

    def post_comment(self, post_url: str, comment_text: str) -> bool:
        """
        Post a comment on an Instagram post.

        Args:
            post_url: Instagram post URL
            comment_text: Comment text to post

        Returns:
            True if successful
        """
        try:
            media_pk = self.client.media_pk_from_url(post_url)
            self.client.media_comment(media_pk, comment_text)
            return True
        except Exception as e:
            print(f"Failed to post comment: {e}")
            return False

    def get_unfollowers(self, username: str) -> List[str]:
        """
        Get list of users who unfollowed.

        Args:
            username: Instagram username

        Returns:
            List of unfollower usernames
        """
        try:
            user_id = self.client.user_id_from_username(username)
            followers = set(self.client.user_followers(user_id).keys())
            following = set(self.client.user_following(user_id).keys())

            unfollowers = following - followers

            # Get usernames
            unfollower_usernames = []
            for user_id in unfollowers:
                user_info = self.client.user_info(user_id)
                unfollower_usernames.append(user_info.username)

            return unfollower_usernames
        except Exception as e:
            print(f"Failed to get unfollowers: {e}")
            return []
