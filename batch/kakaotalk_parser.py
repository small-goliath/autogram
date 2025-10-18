"""KakaoTalk parser batch job."""
import os
import re
import sys
import asyncio
import logging
from datetime import datetime, timedelta
from pydantic import BaseModel

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import AsyncSessionLocal
from core.models import RequestByWeek, SnsRaiseUser
from sqlalchemy import select

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KakaoTalk(BaseModel):
    """Parsed KakaoTalk message."""
    username: str
    link: str
    date: str


def get_target_week_dates() -> tuple[datetime, datetime]:
    """
    Get the target week dates (last Monday to last Sunday).

    Returns:
        Tuple of (start_date, end_date)
    """
    today = datetime.now()
    # Get last Monday
    days_since_monday = (today.weekday() + 7) % 7
    if days_since_monday == 0:
        days_since_monday = 7
    last_monday = today - timedelta(days=days_since_monday)
    last_monday = last_monday.replace(hour=0, minute=0, second=0, microsecond=0)

    # Get last Sunday
    last_sunday = last_monday + timedelta(days=6)
    last_sunday = last_sunday.replace(hour=23, minute=59, second=59, microsecond=999999)

    return last_monday, last_sunday


def format_date(date: datetime) -> str:
    """Format date for Korean format."""
    return date.strftime("%Y. %-m. %-d")


def parse_kakaotalk_file(file_path: str) -> list[KakaoTalk]:
    """
    Parse KakaoTalk export file and extract Instagram links.

    Args:
        file_path: Path to KakaoTalk_latest.txt

    Returns:
        List of parsed KakaoTalk messages
    """
    logger.info(f"Processing file: {file_path}")

    if not os.path.exists(file_path):
        logger.warning("KakaoTalk file not found")
        return []

    start_date, end_date = get_target_week_dates()
    formatted_start = format_date(start_date)
    formatted_end = format_date(end_date)
    logger.info(f"Target period: {formatted_start} to {formatted_end}")

    is_target_week = False
    chat = ""

    try:
        # Read file and extract target week content
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip() == formatted_start:
                    is_target_week = True
                    logger.info(f"Found start date: {formatted_start}")

                if is_target_week:
                    chat += line

                if line.strip() == formatted_end:
                    logger.info(f"Found end date: {formatted_end}")
                    break

        if not chat:
            logger.warning("No content found for target week")
            return []

        # Parse Instagram links
        message_pattern = re.compile(
            r"""^
            (20\d{2}\.\s*\d{1,2}\.\s*\d{1,2})         # Date
            (?:.*?)                                     # Any characters
            ,\s                                         # Comma and space
            (.*?)                                       # Username
            \s*:\s                                      # Colon
            (?:(?!20\d{2}\.\s*\d{1,2}\.\s*\d{1,2}).)*?  # Any characters except date
            (https://www\.instagram\.com/[^\s\n]+)      # Instagram link
            """,
            re.MULTILINE | re.VERBOSE
        )

        kakaotalk_parsed = []
        messages = message_pattern.findall(chat)

        logger.info(f"Found {len(messages)} messages with Instagram links")

        for match in messages:
            date_str = match[0]
            username_raw = match[1]
            link = match[2].strip()

            # Extract username (format: "Name@username")
            if '@' in username_raw:
                username = username_raw.split('@')[1].strip()
            else:
                username = username_raw.strip()

            kakaotalk_parsed.append(KakaoTalk(
                username=username,
                link=link,
                date=date_str
            ))

            logger.debug(f"Parsed: {username} - {link}")

        return kakaotalk_parsed

    except Exception as e:
        logger.error(f"Error parsing KakaoTalk file: {e}")
        return []


async def save_to_database(messages: list[KakaoTalk]) -> int:
    """
    Save parsed messages to database.

    Args:
        messages: List of parsed KakaoTalk messages

    Returns:
        Number of saved records
    """
    if not messages:
        logger.info("No messages to save")
        return 0

    saved_count = 0
    start_date, end_date = get_target_week_dates()

    async with AsyncSessionLocal() as db:
        try:
            for message in messages:
                # Find user by username
                result = await db.execute(
                    select(SnsRaiseUser).where(SnsRaiseUser.username == message.username)
                )
                user = result.scalar_one_or_none()

                if not user:
                    logger.warning(f"User not found: {message.username}")
                    continue

                # Check if request already exists
                result = await db.execute(
                    select(RequestByWeek).where(
                        RequestByWeek.user_id == user.id,
                        RequestByWeek.week_start_date == start_date
                    )
                )
                existing = result.scalar_one_or_none()

                if existing:
                    logger.info(f"Request already exists for user: {message.username}")
                    continue

                # Create new request
                request = RequestByWeek(
                    user_id=user.id,
                    instagram_link=message.link,
                    request_date=datetime.now(),
                    week_start_date=start_date,
                    week_end_date=end_date,
                    status="pending",
                    comment_count=0
                )

                db.add(request)
                saved_count += 1
                logger.info(f"Saved request for user: {message.username}")

            await db.commit()
            logger.info(f"Successfully saved {saved_count} requests")

        except Exception as e:
            await db.rollback()
            logger.error(f"Error saving to database: {e}")
            raise

    return saved_count


async def main():
    """Main batch job function."""
    logger.info("="* 50)
    logger.info("KakaoTalk Parser Batch Job Started")
    logger.info("=" * 50)

    file_path = os.path.join(
        os.path.dirname(__file__),
        "kakaotalk",
        "KakaoTalk_latest.txt"
    )

    # Parse KakaoTalk file
    messages = parse_kakaotalk_file(file_path)
    logger.info(f"Parsed {len(messages)} messages")

    # Save to database
    saved_count = await save_to_database(messages)

    logger.info("=" * 50)
    logger.info(f"Batch Job Completed - Saved {saved_count} requests")
    logger.info("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
