"""
KakaoTalk 대화 파일을 파싱하여 request_by_week 테이블에 저장하는 배치
"""

import os
import sys
import re
from pydantic import BaseModel
from sqlalchemy import select, delete

from core.database import get_session_maker
from core.models import RequestByWeek, SnsRaiseUser
from date_helper import get_target_week_dates, format_date, get_week_start_date
from logger import setup_logger

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

logger = setup_logger("parse_kakaotalk")


class KakaoTalk(BaseModel):
    """카카오톡에서 파싱된 데이터"""

    username: str
    link: str


def parse_kakaotalk_content(content: str) -> list[KakaoTalk]:
    """
    카카오톡 대화 내용을 파싱합니다.

    Args:
        content: 카카오톡 대화 내용 문자열

    Returns:
        파싱된 KakaoTalk 리스트
    """
    start_date, end_date = get_target_week_dates()
    formatted_start = format_date(start_date)
    formatted_end = format_date(end_date)
    logger.info(f"📅 타겟 기간: {formatted_start} ~ {formatted_end} 전날까지")

    is_target_week = False
    chat = ""

    try:
        for line in content.split("\n"):
            if "저장한 날짜 : " in line.strip():
                continue

            if formatted_start in line.strip():
                is_target_week = True
            elif formatted_end in line.strip():
                break

            # 타겟 주 내용 수집
            if is_target_week:
                chat += line + "\n"

        if not is_target_week:
            logger.warning(f"⚠️ 타겟 주({formatted_start})를 찾을 수 없습니다.")
            return []

        # 정규식 패턴으로 인스타그램 링크 추출
        message_pattern = re.compile(
            r"""^
            (20\d{2}\.\s*\d{1,2}\.\s*\d{1,2})         # 날짜
            (?:.*?)                                     # 0개 이상의 문자
            ,\s                                       # 콤마와 공백
            (.*?)                                     # 닉네임
            \s*:\s                                    # 공백과 콜론
            (?:(?!20\d{2}\.\s*\d{1,2}\.\s*\d{1,2}).)*?  # 날짜가 아닌 0개 이상의 문자열
            (https://www\.instagram\.com/[^\s\n]+)    # 인스타그램 링크
            \n+                                       # 1개 이상의 줄바꿈
            (?:(?!20\d{2}\.\s*\d{1,2}\.\s*\d{1,2}).)*?  # 날짜가 아닌 0개 이상의 문자열
            /(?P<digit>\d+)
            """,
            re.MULTILINE | re.VERBOSE,
        )

        kakaotalk_parsed = []
        messages = message_pattern.findall(chat)

        for match in messages:
            # match[1]은 닉네임 (예: "John@johndoe" -> "johndoe")
            nickname = str(match[1]).strip()

            # '@' 뒤의 username 추출
            if "@" in nickname:
                username = nickname.split("@")[1]
            else:
                # '@'가 없으면 전체를 username으로 사용
                username = nickname

            link = str(match[2]).strip()

            kakaotalk_parsed.append(KakaoTalk(username=username, link=link))

            logger.debug(f"  📝 파싱: {username} -> {link}")

        logger.info(f"✅ 총 {len(kakaotalk_parsed)}개의 링크 파싱 완료")
        return kakaotalk_parsed

    except Exception as e:
        logger.error(f"❌ 내용 파싱 중 오류 발생: {e}")
        raise


async def save_to_database(parsed_data: list[KakaoTalk]) -> dict:
    """
    파싱된 데이터를 request_by_week 테이블에 저장합니다.
    기존 주차 데이터를 모두 삭제하고 새로 저장합니다.

    Args:
        parsed_data: 파싱된 KakaoTalk 리스트

    Returns:
        결과 통계 딕셔너리
    """
    session_maker = get_session_maker()
    async with session_maker() as session:
        try:
            week_start = get_week_start_date()

            # 1. 이번 주 기존 데이터 모두 삭제
            delete_result = await session.execute(delete(RequestByWeek))
            deleted_count = delete_result.rowcount

            logger.info(f"🗑️ 이번 주 기존 데이터 {deleted_count}개 삭제")

            # 2. 유효한 사용자 목록 조회
            result = await session.execute(select(SnsRaiseUser.username))
            valid_users = {row[0] for row in result.fetchall()}
            logger.info(f"👥 등록된 사용자 수: {len(valid_users)}")

            saved_count = 0
            invalid_user_count = 0

            # 3. 새로운 데이터 저장
            for item in parsed_data:
                # 유효한 사용자인지 확인
                if item.username not in valid_users:
                    logger.warning(f"⚠️ 미등록 사용자: {item.username}")
                    invalid_user_count += 1
                    continue

                # 새로운 레코드 저장
                request = RequestByWeek(
                    username=item.username,
                    instagram_link=item.link,
                    week_start_date=week_start,
                )
                session.add(request)
                saved_count += 1
                logger.debug(f"  💾 저장: {item.username} - {item.link[:50]}...")

            await session.commit()

            logger.info(
                f"📊 저장 완료: {deleted_count}개 삭제, {saved_count}개 저장, {invalid_user_count}개 미등록 사용자"
            )

            return {
                "총 파싱": len(parsed_data),
                "삭제된 기존 데이터": deleted_count,
                "저장 성공": saved_count,
                "미등록 사용자": invalid_user_count,
            }
        except Exception:
            await session.rollback()
            raise
