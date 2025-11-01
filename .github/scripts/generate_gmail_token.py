"""
Gmail API 인증 토큰을 로컬에서 생성하는 스크립트
"""
import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Gmail API 스코프
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]


def generate_token():
    """Gmail API 토큰 생성"""
    creds = None

    # credentials.json 파일 확인
    if not os.path.exists('credentials.json'):
        print("❌ credentials.json 파일이 없습니다.")
        print("\n다음 단계를 따라주세요:")
        print("1. Google Cloud Console에서 OAuth 2.0 클라이언트 ID 생성")
        print("2. credentials.json 다운로드")
        print("3. 이 스크립트와 같은 디렉토리에 저장")
        print("\n자세한 내용은 docs/GMAIL_API_SETUP.md 참조")
        return False

    # 기존 토큰이 있으면 로드
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # 유효한 토큰이 없으면 새로 생성
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("토큰 갱신 중...")
            creds.refresh(Request())
        else:
            print("새 토큰 생성 중...")
            print("브라우저가 열립니다. Google 계정으로 로그인하세요.")
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES
            )
            creds = flow.run_local_server(port=0)

        # 토큰을 token.json에 저장
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    print("\n✅ 토큰 생성 완료!")
    print("\n" + "="*60)
    print("다음 내용을 GitHub Secrets에 등록하세요:")
    print("="*60)

    # GMAIL_CREDENTIALS 출력
    print("\n[1] GMAIL_CREDENTIALS")
    print("-" * 60)
    with open('credentials.json', 'r') as f:
        print(f.read())

    # GMAIL_TOKEN 출력
    print("\n[2] GMAIL_TOKEN")
    print("-" * 60)
    print(creds.to_json())

    print("\n" + "="*60)
    print("\n📝 GitHub 저장소 → Settings → Secrets and variables → Actions")
    print("   → New repository secret 에 위 내용을 각각 추가하세요.")
    print("\n자세한 내용은 docs/GMAIL_API_SETUP.md 참조")

    return True


if __name__ == '__main__':
    try:
        success = generate_token()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
