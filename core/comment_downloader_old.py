"""
instaloader를 활용한 댓글 다운로드 모듈
username 기준으로 bulk 다운로드하여 효율성 향상
"""
import os
import json
import subprocess
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import instaloader


class CommentDownloader:
    """Instaloader를 활용한 댓글 다운로더"""

    def __init__(self, loader: instaloader.Instaloader, helper_username: str):
        """
        Args:
            loader: 로그인된 Instaloader 인스턴스
            helper_username: Helper 계정 username (로그인된 계정)
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
        temp_dir = None
        try:
            # 임시 디렉토리 생성
            temp_dir = tempfile.mkdtemp(prefix=f"instaloader_{target_username}_")

            # 날짜 필터 계산
            filter_date = datetime.utcnow() - timedelta(days=days_back)
            date_filter = f"date_utc >= datetime({filter_date.year}, {filter_date.month}, {filter_date.day})"

            # instaloader 명령 실행 (최근 N일 포스트 전체 다운로드)
            # 최대 50개 포스트만 확인 (최근 7일이면 충분)
            cmd = [
                "instaloader",
                "--login", self.helper_username,
                "--comments",
                "--no-pictures",
                "--no-videos",
                "--no-video-thumbnails",
                "--no-profile-pic",
                "--no-compress-json",  # JSON 압축 비활성화 (shortcode 추출 위해)
                f"--post-filter={date_filter}",
                f"--dirname-pattern={temp_dir}",
                "--count=50",  # 최대 50개 포스트만 확인
                target_username
            ]

            # subprocess로 실행 (타임아웃 50분)
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3000,
                cwd=temp_dir
            )

            # 모든 JSON 파일에서 댓글 파싱
            posts_data = {}

            # *_comments.json 파일 찾기
            comment_files = list(Path(temp_dir).glob("*_comments.json"))

            for json_file in comment_files:
                # 파일명에서 shortcode 추출 (YYYY-MM-DD_HH-MM-SS_UTC_comments.json)
                filename = json_file.stem  # _comments 제외
                # UTC 타임스탬프 이후가 shortcode가 아니라 파일명 형식 재확인 필요
                # 실제로는 전체 파일을 읽고 shortcode를 찾아야 함

                # JSON 파일 읽기
                with open(json_file, 'r', encoding='utf-8') as f:
                    comments = json.load(f)

                # 첫 번째 댓글에서 post shortcode 찾기
                if not comments:
                    continue

                # 댓글 작성자 수집
                commenters = set()
                for comment in comments:
                    if 'owner' in comment and 'username' in comment['owner']:
                        commenters.add(comment['owner']['username'].lower())

                # shortcode는 메타데이터 JSON 파일에서 추출
                # 파일명: YYYY-MM-DD_HH-MM-SS_UTC.json
                base_name = json_file.name.replace('_comments.json', '')
                meta_file = json_file.parent / f"{base_name}.json"

                shortcode = None
                if meta_file.exists():
                    try:
                        with open(meta_file, 'r', encoding='utf-8') as mf:
                            meta = json.load(mf)
                        # instaloader JSON 구조: {"node": {"shortcode": "...", ...}}
                        node = meta.get('node', {})
                        shortcode = node.get('shortcode')
                    except Exception as e:
                        pass

                if not shortcode:
                    continue

                # 좋아요는 API로 조회 (빠르게)
                likers = set()
                try:
                    post = instaloader.Post.from_shortcode(self.loader.context, shortcode)
                    for liker in post.get_likes():
                        likers.add(liker.username.lower())
                except:
                    pass

                posts_data[shortcode] = {
                    'commenters': commenters,
                    'likers': likers
                }

            return posts_data, None

        except subprocess.TimeoutExpired:
            return {}, "다운로드 타임아웃 (50분 초과)"
        except Exception as e:
            return {}, f"다운로드 실패: {str(e)}"
        finally:
            # 임시 디렉토리 삭제
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
