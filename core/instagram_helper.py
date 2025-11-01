"""
Instagram helper functions for instaloader and instagrapi operations.
"""
import json
from datetime import datetime, timedelta
from instaloader import Instaloader, Profile, TwoFactorAuthRequiredException
from instagrapi import Client as InstagrapiClient
from instagrapi.exceptions import (
    LoginRequired,
    ChallengeRequired,
    TwoFactorRequired,
    BadPassword,
    ClientThrottledError,
    ProxyAddressIsBlocked,
    ClientLoginRequired,
    FeedbackRequired,
    PleaseWaitFewMinutes,
    ClientError,
    ClientUnauthorizedError,
)
from .crypto import decrypt_data


class InstaloaderHelper:
    """Helper for instaloader operations (read-only Instagram operations)."""

    def __init__(self, username: str | None = None):
        """
        Initialize Instaloader helper.

        Args:
            username: Instagram username (optional, for loading session)
        """
        self.loader = Instaloader(
            quiet=True,
            download_pictures=False,
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
        )
        self.username = username

    def login(self, username: str, password: str, verification_code: str | None = None) -> bool:
        """
        Login to Instagram using instaloader.

        Args:
            username: Instagram username
            password: Instagram password
            verification_code: 2FA verification code (if required)

        Returns:
            True if login successful

        Raises:
            Exception: If login fails
        """
        try:
            self.loader.login(username, password)
            self.username = username
            return True
        except TwoFactorAuthRequiredException:
            if not verification_code:
                raise Exception("2단계 인증 코드가 필요합니다. verification_code를 입력해주세요.")
            try:
                self.loader.two_factor_login(verification_code)
                self.username = username
                return True
            except Exception as e:
                raise Exception(f"2단계 인증 실패: {str(e)}")
        except Exception as e:
            raise Exception(f"Instaloader login failed: {str(e)}")

    def load_session_from_data(self, username: str, session_data: str) -> bool:
        """
        Load session from encrypted JSON data.

        Args:
            username: Instagram username
            session_data: Encrypted JSON encoded session data

        Returns:
            True if session loaded successfully

        Raises:
            Exception: If session load fails
        """
        try:
            import pickle
            import base64

            if not session_data or not session_data.strip():
                raise Exception("세션 데이터가 비어있습니다")

            # Decrypt and decode session data
            decrypted_data = decrypt_data(session_data)

            if not decrypted_data or not decrypted_data.strip():
                raise Exception("복호화된 세션 데이터가 비어있습니다")

            # Try JSON first (new format)
            try:
                session_dict = json.loads(decrypted_data)
            except json.JSONDecodeError:
                # Fallback: try pickle format (old format - for backward compatibility)
                try:
                    session_dict = pickle.loads(base64.b64decode(decrypted_data))
                except Exception as pickle_err:
                    raise Exception(
                        f"세션 데이터를 JSON 또는 Pickle 형식으로 파싱할 수 없습니다. "
                        f"헬퍼 계정을 관리자 페이지에서 삭제하고 다시 등록해주세요. "
                        f"(JSON 오류: invalid JSON, Pickle 오류: {str(pickle_err)})"
                    )

            # Load session into instaloader (instaloader 4.10+)
            self.loader.load_session(username, session_dict)
            self.username = username
            return True
        except Exception as e:
            raise Exception(f"Failed to load instaloader session: {str(e)}")

    def save_session_to_data(self) -> str:
        """
        Save current session to encrypted JSON data.

        Returns:
            Encrypted JSON encoded session data

        Raises:
            Exception: If no username or session save fails
        """
        if not self.username:
            raise Exception("No username set for session save")

        try:
            # Save session to dict (instaloader 4.10+)
            session_dict = self.loader.save_session()

            # Convert to JSON and encrypt
            from .crypto import encrypt_data
            json_data = json.dumps(session_dict)
            encrypted_data = encrypt_data(json_data)

            return encrypted_data
        except Exception as e:
            raise Exception(f"Failed to save instaloader session: {str(e)}")

    def get_profile(self, username: str) -> Profile:
        """
        Get Instagram profile.

        Args:
            username: Instagram username

        Returns:
            Profile object

        Raises:
            Exception: If profile fetch fails
        """
        try:
            return Profile.from_username(self.loader.context, username)
        except Exception as e:
            raise Exception(f"Failed to get profile {username}: {str(e)}")

    def get_followers(self, username: str) -> list[str]:
        """
        Get list of followers for a user.

        Args:
            username: Instagram username

        Returns:
            List of follower usernames

        Raises:
            Exception: If fetch fails
        """
        try:
            profile = self.get_profile(username)
            return [follower.username for follower in profile.get_followers()]
        except Exception as e:
            raise Exception(f"Failed to get followers: {str(e)}")

    def get_following(self, username: str) -> list[str]:
        """
        Get list of users that a user is following.

        Args:
            username: Instagram username

        Returns:
            List of following usernames

        Raises:
            Exception: If fetch fails
        """
        try:
            profile = self.get_profile(username)
            return [followee.username for followee in profile.get_followees()]
        except Exception as e:
            raise Exception(f"Failed to get following: {str(e)}")

    def check_unfollowers(self, username: str) -> list[str]:
        """
        Check who doesn't follow back.

        Args:
            username: Instagram username

        Returns:
            List of usernames that don't follow back

        Raises:
            Exception: If check fails
        """
        following = set(self.get_following(username))
        followers = set(self.get_followers(username))
        return list(following - followers)


class InstagrapiHelper:
    """Helper for instagrapi operations (write operations like posting comments)."""

    def __init__(self):
        """Initialize Instagrapi helper."""
        self.client = InstagrapiClient()
        # Set delay range for rate limiting (1-3 seconds between requests)
        self.client.delay_range = [1, 3]
        self.last_login_time: datetime | None = None

    def login(self, username: str, password: str, verification_code: str | None = None) -> bool:
        """
        Login to Instagram using instagrapi.

        Args:
            username: Instagram username
            password: Instagram password
            verification_code: 2FA verification code (if required)

        Returns:
            True if login successful

        Raises:
            Exception: If login fails
        """
        try:
            if verification_code:
                self.client.login(username, password, verification_code=verification_code)
            else:
                self.client.login(username, password)

            self.last_login_time = datetime.now()
            return True
        except TwoFactorRequired:
            raise Exception("2단계 인증 코드가 필요합니다. verification_code를 제공해주세요.")
        except BadPassword:
            raise Exception("잘못된 비밀번호입니다. 비밀번호를 확인해주세요.")
        except ChallengeRequired as e:
            raise Exception(f"보안 인증이 필요합니다. Instagram 앱에서 본인 확인을 완료해주세요: {str(e)}")
        except ClientThrottledError:
            raise Exception("요청이 너무 많습니다. 잠시 후 다시 시도해주세요. (HTTP 429)")
        except ProxyAddressIsBlocked:
            raise Exception("IP 주소가 차단되었습니다. 프록시를 사용하거나 네트워크를 변경해주세요.")
        except FeedbackRequired:
            raise Exception("Instagram으로부터 피드백이 요구되었습니다. 계정이 일시적으로 제한되었을 수 있습니다.")
        except PleaseWaitFewMinutes:
            raise Exception("너무 많은 시도로 인해 일시적으로 차단되었습니다. 몇 분 후 다시 시도해주세요.")
        except ClientError as e:
            raise Exception(f"Instagram API 오류: {str(e)}")
        except Exception as e:
            raise Exception(f"Instagrapi login failed: {str(e)}")

    def load_session_from_data(self, username: str, password: str, session_data: str) -> bool:
        """
        Load session from encrypted JSON settings.

        Args:
            username: Instagram username
            password: Instagram password
            session_data: Encrypted JSON settings string

        Returns:
            True if session loaded successfully

        Raises:
            Exception: If session load fails
        """
        try:
            # Decrypt session data
            decrypted_data = decrypt_data(session_data)
            settings_dict = json.loads(decrypted_data)

            # Load settings into client
            self.client.set_settings(settings_dict)

            # Login with existing session (won't create new session if valid)
            self.client.login(username, password)

            # Validate session by checking timeline feed
            self.client.get_timeline_feed()

            self.last_login_time = datetime.now()
            return True
        except (LoginRequired, ClientLoginRequired):
            raise Exception("세션이 만료되었습니다. 재로그인이 필요합니다.")
        except ClientUnauthorizedError:
            raise Exception("인증 정보가 유효하지 않습니다. 세션이 만료되었거나 비밀번호가 변경되었을 수 있습니다.")
        except TwoFactorRequired:
            raise Exception("2단계 인증 코드가 필요합니다. verification_code를 제공해주세요.")
        except ChallengeRequired as e:
            raise Exception(f"보안 인증이 필요합니다. Instagram 앱에서 본인 확인을 완료해주세요: {str(e)}")
        except ClientThrottledError:
            raise Exception("요청이 너무 많습니다. 잠시 후 다시 시도해주세요. (HTTP 429)")
        except ProxyAddressIsBlocked:
            raise Exception("IP 주소가 차단되었습니다. 프록시를 사용하거나 네트워크를 변경해주세요.")
        except FeedbackRequired:
            raise Exception("Instagram으로부터 피드백이 요구되었습니다. 계정이 일시적으로 제한되었을 수 있습니다.")
        except PleaseWaitFewMinutes:
            raise Exception("너무 많은 시도로 인해 일시적으로 차단되었습니다. 몇 분 후 다시 시도해주세요.")
        except ClientError as e:
            raise Exception(f"Instagram API 오류: {str(e)}")
        except json.JSONDecodeError:
            raise Exception("세션 데이터 형식이 올바르지 않습니다.")
        except Exception as e:
            raise Exception(f"Failed to load instagrapi session: {str(e)}")

    def save_session_to_data(self) -> str:
        """
        Save current session to encrypted JSON settings.

        Returns:
            Encrypted JSON settings string

        Raises:
            Exception: If session save fails
        """
        try:
            from .crypto import encrypt_data

            # Get settings as dict
            settings_dict = self.client.get_settings()

            # Convert to JSON and encrypt
            json_data = json.dumps(settings_dict)
            encrypted_data = encrypt_data(json_data)

            return encrypted_data
        except Exception as e:
            raise Exception(f"Failed to save instagrapi session: {str(e)}")

    def post_comment(self, media_id: str, text: str) -> bool:
        """
        Post a comment on an Instagram post.

        Args:
            media_id: Instagram media ID
            text: Comment text

        Returns:
            True if comment posted successfully

        Raises:
            Exception: If posting fails
        """
        try:
            self.client.media_comment(media_id, text)
            return True
        except Exception as e:
            raise Exception(f"Failed to post comment: {str(e)}")

    def get_media_id_from_url(self, url: str) -> str:
        """
        Extract media ID from Instagram URL.

        Args:
            url: Instagram post URL

        Returns:
            Media ID

        Raises:
            Exception: If extraction fails
        """
        try:
            return self.client.media_pk_from_url(url)
        except Exception as e:
            raise Exception(f"Failed to extract media ID: {str(e)}")

    def is_session_valid(self) -> bool:
        """
        Check if current session is valid.

        Returns:
            True if session is valid, False otherwise
        """
        try:
            # Try to fetch timeline to verify session
            self.client.get_timeline_feed()
            return True
        except (LoginRequired, ClientLoginRequired, ClientUnauthorizedError):
            return False
        except Exception:
            # For other errors, assume session might still be valid
            return True

    def should_refresh_session(self, max_session_age_hours: int = 24) -> bool:
        """
        Check if session should be refreshed based on age.

        Args:
            max_session_age_hours: Maximum session age in hours before refresh (default: 24)

        Returns:
            True if session should be refreshed
        """
        if not self.last_login_time:
            return True

        session_age = datetime.now() - self.last_login_time
        return session_age > timedelta(hours=max_session_age_hours)

    def validate_and_refresh_if_needed(
        self, username: str, password: str, verification_code: str | None = None
    ) -> bool:
        """
        Validate session and refresh if expired or invalid.

        Args:
            username: Instagram username
            password: Instagram password
            verification_code: 2FA verification code (if required)

        Returns:
            True if session is valid or successfully refreshed

        Raises:
            Exception: If refresh fails
        """
        # Check if session is too old (proactive refresh)
        if self.should_refresh_session():
            try:
                self.login(username, password, verification_code)
                return True
            except Exception as e:
                raise Exception(f"세션 갱신 실패: {str(e)}")

        # Check if session is still valid
        if not self.is_session_valid():
            try:
                self.login(username, password, verification_code)
                return True
            except Exception as e:
                raise Exception(f"세션 재로그인 실패: {str(e)}")

        return True


async def get_instaloader_with_helper(session) -> tuple[Instaloader, "Helper"] | tuple[None, None]:
    """
    Get an Instaloader instance with an active helper account from database.

    Args:
        session: Database AsyncSession

    Returns:
        Tuple of (Instaloader instance, Helper object) or (None, None) if no active helper available
    """
    from sqlalchemy import select
    from .models import Helper

    # Get active helper from database
    result = await session.execute(
        select(Helper)
        .where(Helper.is_active == True)
        .order_by(Helper.last_used_at.asc().nulls_first())
        .limit(1)
    )
    helper = result.scalar_one_or_none()

    if not helper:
        return None, None

    # Create InstaloaderHelper instance
    helper_instance = InstaloaderHelper(helper.instagram_username)

    # Try to load session if available
    if helper.session_data:
        try:
            helper_instance.load_session_from_data(
                helper.instagram_username,
                helper.session_data
            )
        except Exception as e:
            # Session load failed - cannot automatically re-login in batch environment
            # Admin needs to re-register the helper account
            raise Exception(
                f"헬퍼 계정 '{helper.instagram_username}'의 세션이 만료되었습니다. "
                f"관리자 페이지에서 헬퍼 계정을 다시 등록해주세요. "
                f"(원본 오류: {str(e)})"
            )
    else:
        # No session available - admin needs to register helper with valid session
        raise Exception(
            f"헬퍼 계정 '{helper.instagram_username}'에 저장된 세션이 없습니다. "
            f"관리자 페이지에서 헬퍼 계정을 다시 등록해주세요."
        )

    # Update last_used_at and commit
    from .utils import get_kst_now
    helper.last_used_at = get_kst_now()
    await session.commit()

    return helper_instance.loader, helper


def get_active_helper_session() -> InstaloaderHelper | None:
    """
    Get an active helper session from database.
    This function should be implemented to load from database.

    Returns:
        InstaloaderHelper instance or None if no active helper available
    """
    # This will be implemented in services layer
    # For now, return None
    return None


def get_active_producer_session() -> InstagrapiHelper | None:
    """
    Get an active producer session from database.
    This function should be implemented to load from database.

    Returns:
        InstagrapiHelper instance or None if no active producer available
    """
    # This will be implemented in services layer
    # For now, return None
    return None
