"""Main batch runner - orchestrates all batch jobs."""
import os
import sys
import asyncio
import logging
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from batch.kakaotalk_parser import main as run_kakaotalk_parser
from batch.comment_verifier import verify_comments
from batch.action_updater import update_actions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def run_all_batches():
    """Run all batch jobs in sequence."""
    start_time = datetime.now()

    logger.info("=" * 70)
    logger.info("AUTOGRAM BATCH JOBS - START")
    logger.info(f"Started at: {start_time}")
    logger.info("=" * 70)

    try:
        # 1. Parse KakaoTalk messages
        logger.info("\n[1/3] Running KakaoTalk Parser...")
        await run_kakaotalk_parser()

        # 2. Verify comments
        logger.info("\n[2/3] Running Comment Verifier...")
        await verify_comments()

        # 3. Update action verifications
        logger.info("\n[3/3] Running Action Updater...")
        await update_actions()

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        logger.info("=" * 70)
        logger.info("AUTOGRAM BATCH JOBS - COMPLETED SUCCESSFULLY")
        logger.info(f"Ended at: {end_time}")
        logger.info(f"Total duration: {duration:.2f} seconds")
        logger.info("=" * 70)

    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        logger.error("=" * 70)
        logger.error("AUTOGRAM BATCH JOBS - FAILED")
        logger.error(f"Error: {str(e)}")
        logger.error(f"Failed at: {end_time}")
        logger.error(f"Duration before failure: {duration:.2f} seconds")
        logger.error("=" * 70)
        raise


if __name__ == "__main__":
    asyncio.run(run_all_batches())
