"""
Gmail에서 카카오톡 채팅 파일을 다운로드하고 파싱하여 DB에 저장하는 통합 배치 스크립트
"""
import os
import sys
import base64
import zipfile
import io
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from batch.kakaotalk.parse_kakaotalk import parse_kakaotalk_content, save_to_database
from batch.utils.logger import setup_logger, log_batch_start, log_batch_end
from batch.utils.discord_notifier import DiscordNotifier


logger = setup_logger("fetch_and_parse_kakaotalk")


def get_gmail_service():
    """Gmail API 서비스 생성"""
    creds_json = os.environ.get('GMAIL_CREDENTIALS')
    token_json = os.environ.get('GMAIL_TOKEN')

    if not creds_json or not token_json:
        raise Exception("Gmail credentials not found in environment variables")

    creds = Credentials.from_authorized_user_info(eval(token_json))

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        print(f"::set-output name=new_token::{creds.to_json()}")

    return build('gmail', 'v1', credentials=creds)


def search_latest_kakaotalk_email(service):
    """최근 일주일 내 카카오톡 채팅 메일 검색"""
    week_ago = datetime.now() - timedelta(days=7)
    query = f'subject:"Kakaotalk_Chat_sns키우기" after:{week_ago.strftime("%Y/%m/%d")}'

    results = service.users().messages().list(
        userId='me',
        q=query,
        maxResults=1
    ).execute()

    messages = results.get('messages', [])
    if not messages:
        logger.warning("⚠️ 최근 카카오톡 메일을 찾을 수 없습니다")
        return None

    return messages[0]['id']


def download_attachment(service, message_id):
    """메일에서 zip 첨부파일 다운로드"""
    message = service.users().messages().get(
        userId='me',
        id=message_id
    ).execute()

    for part in message['payload'].get('parts', []):
        if part.get('filename', '').endswith('.zip'):
            attachment_id = part['body'].get('attachmentId')
            if attachment_id:
                attachment = service.users().messages().attachments().get(
                    userId='me',
                    messageId=message_id,
                    id=attachment_id
                ).execute()

                data = attachment['data']
                file_data = base64.urlsafe_b64decode(data)
                return file_data

    raise Exception("No zip attachment found in email")


def extract_txt_from_zip(zip_data):
    """zip 파일에서 txt 파일 추출"""
    with zipfile.ZipFile(io.BytesIO(zip_data)) as zip_file:
        file_list = zip_file.namelist()
        txt_files = [f for f in file_list if f.endswith('.txt')]

        if not txt_files:
            raise Exception("No txt file found in zip")

        txt_filename = txt_files[0]
        txt_content = zip_file.read(txt_filename)

        return txt_content.decode('utf-8')




async def main():
    """메인 실행 함수"""
    log_batch_start(logger, "카카오톡 가져오기 및 파싱 배치")

    notifier = DiscordNotifier()
    success = False
    details = {}
    error_message = None

    try:
        # 1. Gmail에서 카카오톡 파일 가져오기
        logger.info("📧 Gmail API 연결 중...")
        service = get_gmail_service()

        logger.info("🔍 카카오톡 메일 검색 중...")
        message_id = search_latest_kakaotalk_email(service)

        if not message_id:
            logger.warning("⚠️ 카카오톡 메일을 찾을 수 없습니다")
            details = {"상태": "메일을 찾을 수 없음"}
            success = True  # 에러는 아니므로 success로 처리
            return

        logger.info(f"✉️ 메일 발견: {message_id}")

        logger.info("📥 첨부파일 다운로드 중...")
        zip_data = download_attachment(service, message_id)

        logger.info("📦 ZIP 파일에서 TXT 추출 중...")
        txt_content = extract_txt_from_zip(zip_data)

        # 2. 메모리에서 바로 파싱
        logger.info("📄 카카오톡 내용 파싱 중...")
        parsed_data = parse_kakaotalk_content(txt_content)

        if not parsed_data:
            logger.warning("⚠️ 파싱된 데이터가 없습니다")
            details = {"상태": "파싱된 데이터 없음"}
            success = True
        else:
            # 3. 데이터베이스에 저장
            logger.info("💾 데이터베이스에 저장 중...")
            details = await save_to_database(parsed_data)
            success = True

        logger.info("✅ 모든 작업 완료!")

    except Exception as e:
        logger.error(f"❌ 배치 실행 중 오류 발생: {e}", exc_info=True)
        error_message = str(e)
        details = {"오류": str(e)}

    finally:
        log_batch_end(logger, "카카오톡 가져오기 및 파싱 배치", success)

        # Discord 알림
        notifier.send_batch_result(
            batch_name="카카오톡 가져오기 및 파싱",
            success=success,
            details=details,
            error_message=error_message
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
