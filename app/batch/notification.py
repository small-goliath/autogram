import os
from discord_webhook.webhook import DiscordWebhook
from dotenv import load_dotenv
import tempfile

from app.logger import get_logger

class Discord():
    MAX_MESSAGE_LENGTH = 1999

    def __init__(self):
        load_dotenv()
        self.uri = os.environ.get('WEBHOOK_URI')
        self.log = get_logger("notification")

    def send_message(self, message: str):
        self.log.info(f"discord 알림 발송 중...")
        try:
            if len(message) > self.MAX_MESSAGE_LENGTH:
                with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False, encoding="utf-8") as tmpfile:
                    tmpfile.write(message)
                    tmpfile_path = tmpfile.name

                webhook = DiscordWebhook(url=self.uri)
                with open(tmpfile_path, "rb") as f:
                    webhook.add_file(file=f.read(), filename="message.txt")
                webhook.execute()
                os.remove(tmpfile_path)
            else:
                discord = DiscordWebhook(url=self.uri, content=message)
                discord.execute()
        except Exception as e:
            self.log.error("Failed discord notify!!!")
            self.log.info(message)
            self.log.error(str(e))

    def send_message_embeds(self, message: str, embeds: list):
        self.log.info(f"discord 알림 발송 중...")
        discord = DiscordWebhook(url=self.uri, content=message, embeds=embeds)
        discord.execute()