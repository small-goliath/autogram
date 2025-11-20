"""
instaloader Python API를 직접 사용한 댓글 다운로더
subprocess 대신 API 직접 호출로 속도 향상
"""
import instaloader
from datetime import datetime, timedelta


class CommentDownloader:
    """Instaloader Python API를 활용한 댓글 다운로더"""

    def __init__(self, loader: instaloader.Instaloader, helper_username: str):
        """
        Args:
            loader: 로그인된 Instaloader 인스턴스
            helper_username: Helper 계정 username (로깅용)
        """
        self.loader = loader
        self.helper_username = helper_username

    def download_user_posts_bulk(
        self,
        target_username: str,
        days_back: int = 7
    ) -> tuple[dict[str, dict], str | None]:
        """
        특정 유저의 최근 N일 포스트를 한 번에 다운로드하여 댓글/좋아요 정보 반환

        Args:
            target_username: 대상 Instagram 계정
            days_back: 조회할 과거 일수 (기본 7일)

        Returns:
            ({shortcode: {'commenters': set, 'likers': set}}, 에러 메시지 또는 None)
        """
        try:
            # 프로필 가져오기
            profile = instaloader.Profile.from_username(self.loader.context, target_username)

            # 날짜 기준 (UTC)
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)

            posts_data = {}
            checked_count = 0
            max_posts_to_check = 50  # 최대 50개만 확인

            # 최근 포스트부터 확인
            for post in profile.get_posts():
                checked_count += 1

                if checked_count > max_posts_to_check:
                    break

                # 날짜 확인 (조건에 맞지 않으면 건너뛰기, break 아님)
                if post.date_utc < cutoff_date:
                    continue

                shortcode = post.shortcode

                # 댓글 작성자 수집
                commenters = set()
                try:
                    for comment in post.get_comments():
                        commenters.add(comment.owner.username.lower())
                except Exception:
                    pass

                # 좋아요는 시간이 오래 걸리므로 일단 제외
                likers = set()

                posts_data[shortcode] = {
                    'commenters': commenters,
                    'likers': likers
                }

            return posts_data, None

        except Exception as e:
            return {}, f"다운로드 실패: {str(e)}"
