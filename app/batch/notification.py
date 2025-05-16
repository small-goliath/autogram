import os
from discord_webhook.webhook import DiscordWebhook
from dotenv import load_dotenv

from app.logger import get_logger

class Discord():
    def __init__(self):
        load_dotenv()
        self.uri = os.environ.get('WEBHOOK_URI')
        self.log = get_logger("notification")

    def send_message(self, message: str):
        self.log.info(f"discord 알림 발송 중...")
        discord = DiscordWebhook(url=self.uri, content=message)
        discord.execute()

    def send_message_embeds(self, message: str, embeds: list):
        self.log.info(f"discord 알림 발송 중...")
        message = self._get_message(self.message_format)
        discord = DiscordWebhook(url=self.uri, content=message, embeds=embeds)
        discord.execute()