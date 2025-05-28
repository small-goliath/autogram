import sys

from app.batch.notification import Discord
from app.core import save_unfollowers
from app.logger import get_logger

log = get_logger("auto_activer")
discord = Discord()

# 언팔로워 조회 배치
def main():
    try:
        save_unfollowers()
    except Exception as e:
        log.error(f"언팔로워 조회 배치 실패: {e}")
        discord.send_message(f"언팔로워 조회 배치 실패: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()