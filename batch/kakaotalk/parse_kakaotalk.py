"""
KakaoTalk 대화 파일을 파싱하여 request_by_week 테이블에 저장하는 배치
"""
import os
import sys
import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sqlalchemy import select
from core.database import get_session_maker
from core.models import RequestByWeek, SnsRaiseUser
from batch.utils.date_helper import get_target_week_dates, format_date, get_week_start_date
from batch.utils.logger import setup_logger, log_batch_start, log_batch_end
from batch.utils.discord_notifier import DiscordNotifier


logger = setup_logger("parse_kakaotalk")


class KakaoTalk(BaseModel):
    """카카오톡에서 파싱된 데이터"""
    username: str
    link: str


def parse_kakaotalk_file(file_path: str) -> list[KakaoTalk]:
    """
    카카오톡 대화 파일을 파싱합니다.

    Args:
        file_path: 카카오톡 대화 파일 경로

    Returns:
        파싱된 KakaoTalk 리스트
    """
    logger.info(f"📄 파일 처리 중: {file_path}")

    if not os.path.exists(file_path):
        logger.warning(f"⚠️ 파일이 존재하지 않습니다: {file_path}")
        return []

    start_date, end_date = get_target_week_dates()
    formatted_start = format_date(start_date)
    formatted_end = format_date(end_date)
    logger.info(f"📅 타겟 기간: {formatted_start} ~ {formatted_end} 전날까지")

    is_target_week = False
    chat = ""

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if "저장한 날짜 : " in line.strip():
                    continue
                # 타겟 주 내용 수집
                if is_target_week:
                    chat += line
                
                if formatted_start in line.strip():
                    is_target_week = True
                elif formatted_end in line.strip():
                    break

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
            re.MULTILINE | re.VERBOSE
        )

        kakaotalk_parsed = []
        messages = message_pattern.findall(chat)

        for match in messages:
            # match[1]은 닉네임 (예: "John@johndoe" -> "johndoe")
            nickname = str(match[1]).strip()

            # '@' 뒤의 username 추출
            if '@' in nickname:
                username = nickname.split('@')[1]
            else:
                # '@'가 없으면 전체를 username으로 사용
                username = nickname

            link = str(match[2]).strip()

            kakaotalk_parsed.append(KakaoTalk(
                username=username,
                link=link
            ))

            logger.debug(f"  📝 파싱: {username} -> {link}")

        logger.info(f"✅ 총 {len(kakaotalk_parsed)}개의 링크 파싱 완료")
        return kakaotalk_parsed

    except Exception as e:
        logger.error(f"❌ 파일 파싱 중 오류 발생: {e}")
        raise


async def save_to_database(parsed_data: list[KakaoTalk]) -> dict:
    """
    파싱된 데이터를 request_by_week 테이블에 저장합니다.

    Args:
        parsed_data: 파싱된 KakaoTalk 리스트

    Returns:
        결과 통계 딕셔너리
    """
    session_maker = get_session_maker()
    async with session_maker() as session:
        try:
            week_start = get_week_start_date()

            # 유효한 사용자 목록 조회
            result = await session.execute(
                select(SnsRaiseUser.username)
            )
            valid_users = {row[0] for row in result.fetchall()}
            logger.info(f"👥 등록된 사용자 수: {len(valid_users)}")

            saved_count = 0
            skipped_count = 0
            invalid_user_count = 0

            for item in parsed_data:
                # 유효한 사용자인지 확인
                if item.username not in valid_users:
                    logger.warning(f"⚠️ 미등록 사용자: {item.username}")
                    invalid_user_count += 1
                    continue

                # 중복 체크 (같은 주, 같은 username, 같은 link)
                existing = await session.execute(
                    select(RequestByWeek).where(
                        RequestByWeek.username == item.username,
                        RequestByWeek.instagram_link == item.link,
                        RequestByWeek.week_start_date == week_start
                    )
                )

                if existing.scalar_one_or_none():
                    logger.debug(f"  ⏭️ 중복 건너뜀: {item.username} - {item.link[:50]}...")
                    skipped_count += 1
                    continue

                # 새로운 레코드 저장
                request = RequestByWeek(
                    username=item.username,
                    instagram_link=item.link,
                    week_start_date=week_start
                )
                session.add(request)
                saved_count += 1
                logger.debug(f"  💾 저장: {item.username} - {item.link[:50]}...")

            await session.commit()

            logger.info(f"📊 저장 완료: {saved_count}개 저장, {skipped_count}개 중복, {invalid_user_count}개 미등록 사용자")

            return {
                "총 파싱": len(parsed_data),
                "저장 성공": saved_count,
                "중복 건너뜀": skipped_count,
                "미등록 사용자": invalid_user_count
            }
        except Exception:
            await session.rollback()
            raise


async def main():
    """메인 실행 함수"""
    log_batch_start(logger, "KakaoTalk 파싱 배치")

    notifier = DiscordNotifier()
    success = False
    details = {}
    error_message = None

    try:
        # KakaoTalk 파일 경로
        batch_dir = os.path.dirname(os.path.dirname(__file__))
        kakaotalk_file = os.path.join(batch_dir, "kakaotalk", "KakaoTalk_latest.txt")

        # 1. 파일 파싱
        parsed_data = parse_kakaotalk_file(kakaotalk_file)

        if not parsed_data:
            logger.warning("⚠️ 파싱된 데이터가 없습니다.")
            details = {"상태": "파싱된 데이터 없음"}
            success = True
        else:
            # 2. 데이터베이스에 저장
            details = await save_to_database(parsed_data)
            success = True

    except Exception as e:
        logger.error(f"❌ 배치 실행 중 오류 발생: {e}", exc_info=True)
        error_message = str(e)
        details = {"오류": str(e)}

    finally:
        log_batch_end(logger, "KakaoTalk 파싱 배치", success)

        # Discord 알림
        notifier.send_batch_result(
            batch_name="KakaoTalk 파싱",
            success=success,
            details=details,
            error_message=error_message
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
