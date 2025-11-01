"""
Gmail에서 카카오톡 채팅 파일을 자동으로 다운로드하는 스크립트
"""
import os
import base64
import zipfile
import io
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request


def get_gmail_service():
    """Gmail API 서비스 생성"""
    # GitHub Secrets에서 credentials 가져오기
    creds_json = os.environ.get('GMAIL_CREDENTIALS')
    token_json = os.environ.get('GMAIL_TOKEN')

    if not creds_json or not token_json:
        raise Exception("Gmail credentials not found in environment variables")

    # Credentials 객체 생성
    creds = Credentials.from_authorized_user_info(eval(token_json))

    # 토큰 갱신 필요 시
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        # 갱신된 토큰을 출력 (GitHub Secrets 업데이트용)
        print(f"::set-output name=new_token::{creds.to_json()}")

    return build('gmail', 'v1', credentials=creds)


def search_latest_kakaotalk_email(service):
    """최근 일주일 내 카카오톡 채팅 메일 검색"""
    # 일주일 전 날짜
    week_ago = datetime.now() - timedelta(days=7)
    query = f'subject:"Kakaotalk_Chat_sns키우기" after:{week_ago.strftime("%Y/%m/%d")}'

    results = service.users().messages().list(
        userId='me',
        q=query,
        maxResults=1
    ).execute()

    messages = results.get('messages', [])
    if not messages:
        print("No recent KakaoTalk email found")
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
        # zip 내의 모든 파일 목록
        file_list = zip_file.namelist()

        # .txt 파일 찾기
        txt_files = [f for f in file_list if f.endswith('.txt')]
        if not txt_files:
            raise Exception("No txt file found in zip")

        # 첫 번째 txt 파일 읽기
        txt_filename = txt_files[0]
        txt_content = zip_file.read(txt_filename)

        return txt_content.decode('utf-8')


def save_to_file(content, output_path):
    """파일로 저장"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Saved to {output_path}")


def main():
    """메인 실행"""
    try:
        print("Connecting to Gmail API...")
        service = get_gmail_service()

        print("Searching for KakaoTalk email...")
        message_id = search_latest_kakaotalk_email(service)
        if not message_id:
            print("No email found. Exiting.")
            return False

        print(f"Found message: {message_id}")
        print("Downloading attachment...")
        zip_data = download_attachment(service, message_id)

        print("Extracting txt file from zip...")
        txt_content = extract_txt_from_zip(zip_data)

        print("Saving to file...")
        output_path = "batch/kakaotalk/KakaoTalk_latest.txt"
        save_to_file(txt_content, output_path)

        print("✅ Successfully processed KakaoTalk email!")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
