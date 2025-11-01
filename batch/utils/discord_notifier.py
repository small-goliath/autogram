"""
Discord webhook notification utility
"""
import os
import requests
from typing import Optional
from datetime import datetime


class DiscordNotifier:
    """Discord webhook 알림을 전송하는 클래스"""

    def __init__(self, webhook_url: Optional[str] = None):
        """
        Args:
            webhook_url: Discord webhook URL (환경변수에서 가져오거나 직접 지정)
        """
        self.webhook_url = webhook_url or os.getenv("DISCORD_WEBHOOK_URL")

    def send_message(
        self,
        title: str,
        description: str,
        color: int = 0x5865F2,  # Discord Blurple
        fields: Optional[list[dict]] = None,
        success: bool = True
    ) -> bool:
        """
        Discord로 메시지를 전송합니다.

        Args:
            title: 임베드 제목
            description: 임베드 설명
            color: 임베드 색상 (hex)
            fields: 추가 필드 리스트 [{"name": "필드명", "value": "값", "inline": True}, ...]
            success: 성공 여부 (성공=초록색, 실패=빨간색)

        Returns:
            전송 성공 여부
        """
        if not self.webhook_url:
            print("⚠️ Discord webhook URL이 설정되지 않았습니다.")
            return False

        # 성공/실패에 따라 색상 변경
        if success:
            color = 0x57F287  # Green
        else:
            color = 0xED4245  # Red

        embed = {
            "title": title,
            "description": description,
            "color": color,
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {
                "text": "Autogram Batch System"
            }
        }

        if fields:
            embed["fields"] = fields

        payload = {
            "username": "Autogram Bot",
            "embeds": [embed]
        }

        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            print(f"✅ Discord 알림 전송 완료: {title}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ Discord 알림 전송 실패: {e}")
            return False

    def send_batch_result(
        self,
        batch_name: str,
        success: bool,
        details: dict,
        error_message: Optional[str] = None
    ) -> bool:
        """
        배치 작업 결과를 Discord로 전송합니다.

        Args:
            batch_name: 배치 작업 이름
            success: 성공 여부
            details: 상세 정보 딕셔너리
            error_message: 에러 메시지 (실패 시)

        Returns:
            전송 성공 여부
        """
        if success:
            title = f"✅ {batch_name} 완료"
            description = "배치 작업이 성공적으로 완료되었습니다."
        else:
            title = f"❌ {batch_name} 실패"
            description = f"배치 작업 중 오류가 발생했습니다.\n```{error_message}```"

        fields = []
        for key, value in details.items():
            fields.append({
                "name": key,
                "value": str(value),
                "inline": True
            })

        return self.send_message(
            title=title,
            description=description,
            fields=fields,
            success=success
        )
