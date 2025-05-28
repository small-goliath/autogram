import sys

from app.batch.notification import Discord
from app.core import action
from app.logger import get_logger

log = get_logger("auto_activer")
discord = Discord()

# 서비스를 제공해주는 사람들(Producer)로부터 서비스를 받는 사람들(Consumer)에게 좋아요와 댓글 자동화
def main():
    try:
        action()
    except Exception as e:
        log.error(f"배치 실패: {e}")
        discord.send_message(f"배치 실패: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()