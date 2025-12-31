"""
Logging configuration for batch jobs
"""
import logging
import sys
from datetime import datetime


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    배치 작업용 로거를 설정합니다.

    Args:
        name: 로거 이름
        level: 로그 레벨

    Returns:
        설정된 로거 인스턴스
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 핸들러가 이미 있으면 추가하지 않음
    if logger.handlers:
        return logger

    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # 포맷터
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger


def log_batch_start(logger: logging.Logger, batch_name: str):
    """배치 시작 로그"""
    logger.info("=" * 80)
    logger.info(f"🚀 {batch_name} 시작")
    logger.info(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)


def log_batch_end(logger: logging.Logger, batch_name: str, success: bool = True):
    """배치 종료 로그"""
    status = "✅ 성공" if success else "❌ 실패"
    logger.info("=" * 80)
    logger.info(f"{status} {batch_name} 종료")
    logger.info(f"종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)
