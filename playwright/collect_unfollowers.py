"""
Playwright script to collect unfollowers from Instagram.

This script:
1. Fetches all users from unfollower_service_user table
2. Logs into Instagram using Playwright
3. Handles 2FA with TOTP if needed
4. Executes search_unfollower.js script
5. Clicks the search button
6. Collects unfollower data
7. Saves to unfollowers table
"""

import asyncio
import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from core.config import get_settings
from core.db import unfollower_db
from core.crypto import decrypt_data, generate_totp

env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

HEADLESS_MODE = os.getenv("HEADLESS", "false").lower() == "true"


async def login_instagram(
    page, username: str, password: str, totp_secret: str | None = None
):
    """
    Log into Instagram.

    Args:
        page: Playwright page object
        username: Instagram username
        password: Instagram password
        totp_secret: Optional TOTP secret for 2FA
    """
    print(f"[{username}] 인스타그램 로그인 페이지로 이동 중...")
    await page.goto("https://www.instagram.com/accounts/login/")
    await page.wait_for_load_state("networkidle")
    await page.wait_for_selector('input[name="username"]', timeout=10000)

    print(f"[{username}] 계정 정보 입력 중...")
    await page.fill('input[name="username"]', username)
    await page.fill('input[name="password"]', password)
    await page.click('button[type="submit"]')
    await page.wait_for_timeout(3000)

    try:
        two_fa_input = await page.wait_for_selector(
            'input[name="verificationCode"]', timeout=5000
        )

        if two_fa_input and totp_secret:
            print(f"[{username}] 2단계 인증 감지됨, TOTP 코드 생성 중...")
            totp_code = generate_totp(totp_secret)
            print(f"[{username}] 생성된 TOTP 코드: {totp_code}")
            await page.fill('input[name="verificationCode"]', totp_code)
            print(f"[{username}] 확인 버튼 클릭 중...")

            try:
                confirm_button = await page.wait_for_selector(
                    'button:has-text("확인"), button:has-text("Confirm")', timeout=3000
                )
                await confirm_button.click()
            except PlaywrightTimeout:
                await page.click('button[type="submit"]')

            await page.wait_for_timeout(5000)
        elif two_fa_input and not totp_secret:
            print(
                f"[{username}] 오류: 2단계 인증이 필요하지만 TOTP 시크릿이 제공되지 않았습니다"
            )
            return False
    except PlaywrightTimeout:
        print(f"[{username}] 2단계 인증 불필요")

    print(f"[{username}] 로그인 완료 대기 중...")
    await page.wait_for_timeout(3000)

    try:
        print(f"[{username}] '로그인 정보 저장' 팝업 확인 중...")
        save_info_button = await page.wait_for_selector(
            'button:has-text("나중에 하기"), button:has-text("Not Now")', timeout=5000
        )
        if save_info_button:
            print(f"[{username}] '로그인 정보 저장' 팝업 닫는 중...")
            await save_info_button.click()
            await page.wait_for_timeout(2000)
    except PlaywrightTimeout:
        print(f"[{username}] '로그인 정보 저장' 팝업 없음")

    try:
        print(f"[{username}] 알림 팝업 확인 중...")
        notif_button = await page.wait_for_selector(
            'button:has-text("나중에 하기"), button:has-text("Not Now")', timeout=5000
        )
        if notif_button:
            print(f"[{username}] 알림 팝업 닫는 중...")
            await notif_button.click()
            await page.wait_for_timeout(2000)
    except PlaywrightTimeout:
        print(f"[{username}] 알림 팝업 없음")

    current_url = page.url
    print(f"[{username}] 현재 URL: {current_url}")

    if "challenge" in current_url or "login" in current_url:
        print(f"[{username}] 로그인 실패 또는 추가 인증 필요")
        return False

    print(f"[{username}] 로그인 성공!")
    return True


async def inject_unfollower_script(page):
    """
    Inject the search_unfollower.js script into the page.

    Args:
        page: Playwright page object
    """
    script_path = Path(__file__).parent / "script" / "search_unfollower.js"

    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")

    with open(script_path, "r", encoding="utf-8") as f:
        script_content = f.read()

    print("언팔로워 스크립트 주입 중...")
    await page.evaluate(script_content)
    await page.wait_for_timeout(1000)


async def collect_unfollowers(page, username: str):
    """
    Collect unfollowers from the page.

    Args:
        page: Playwright page object
        username: Instagram username

    Returns:
        List of unfollower dicts
    """
    print(f"[{username}] 언팔로워 UI 대기 중...")

    try:
        await page.wait_for_selector("button.run-scan", timeout=10000)
    except PlaywrightTimeout:
        print(f"[{username}] 오류: 조회 버튼을 찾을 수 없습니다")
        return []

    print(f"[{username}] 조회 버튼 클릭 중...")
    await page.click("button.run-scan")
    print(
        f"[{username}] 데이터 로딩 대기 중 (팔로워 수가 많을 경우 시간이 오래 걸릴 수 있습니다)..."
    )

    try:
        await page.wait_for_selector(".progressbar", timeout=5000)
        print(f"[{username}] 로딩 시작됨...")
    except PlaywrightTimeout:
        print(f"[{username}] 프로그레스바 감지되지 않음")

    try:
        await page.wait_for_selector(
            '.toast:has-text("수집이 성공적으로 종료되었습니다!")', timeout=3600000
        )  # 1 hour max
        print(f"[{username}] 스캔 완료!")
    except PlaywrightTimeout:
        print(f"[{username}] 오류: 1시간 이내에 스캔이 완료되지 않았습니다")
        return []

    print(f"[{username}] 모든 항목 렌더링 대기 중...")
    await page.wait_for_timeout(2000)

    print(f"[{username}] 언팔로워 데이터 수집 중...")
    unfollowers_data = await page.evaluate("""
        () => {
            const results = [];
            const resultItems = document.querySelectorAll('.result-item');

            // Skip first item (creator: doto.ri_)
            resultItems.forEach((item, index) => {
                if (index === 0) return; // Skip first item

                const usernameEl = item.querySelector('a.fs-xlarge, a[href^="/"]');
                const fullnameEl = item.querySelector('span.fs-medium');
                const avatarEl = item.querySelector('img.avatar');

                if (usernameEl && fullnameEl && avatarEl) {
                    const username = usernameEl.textContent.trim();
                    const fullname = fullnameEl.textContent.trim();
                    const profileUrl = avatarEl.src;

                    results.push({
                        unfollower_username: username,
                        unfollower_fullname: fullname,
                        unfollower_profile_url: profileUrl
                    });
                }
            });

            return results;
        }
    """)

    print(f"[{username}] {len(unfollowers_data)}명의 언팔로워 발견")
    return unfollowers_data


async def process_user(
    username: str, password: str, totp_secret: str | None, db_session
):
    """
    Process a single user: login, collect unfollowers, save to DB.
    Retries login up to 5 times with browser restart on each attempt.

    Args:
        username: Instagram username
        password: Decrypted Instagram password
        totp_secret: Decrypted TOTP secret (optional)
        db_session: Database session
    """
    async with async_playwright() as p:
        print(f"\n{'=' * 60}")
        print(f"사용자 처리 중: {username}")
        print(f"{'=' * 60}\n")

        max_retries = 5
        login_success = False
        browser = None
        page = None

        for attempt in range(1, max_retries + 1):
            try:
                print(f"[{username}] 로그인 시도 {attempt}/{max_retries}")

                if browser:
                    await browser.close()
                    print(f"[{username}] 이전 브라우저 인스턴스 종료됨")
                    await asyncio.sleep(2)

                browser = await p.chromium.launch(headless=HEADLESS_MODE)
                context = await browser.new_context(
                    viewport={"width": 1280, "height": 720},
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                )
                page = await context.new_page()

                login_success = await login_instagram(
                    page, username, password, totp_secret
                )

                if login_success:
                    print(f"[{username}] {attempt}번째 시도에서 로그인 성공")
                    break
                else:
                    print(f"[{username}] {attempt}번째 시도에서 로그인 실패")
                    if attempt < max_retries:
                        print(f"[{username}] 새 브라우저로 재시도 중...")

            except Exception as e:
                print(f"[{username}] 로그인 시도 {attempt} 중 오류 발생: {str(e)}")
                if attempt < max_retries:
                    print(f"[{username}] 재시도 중...")

        if not login_success:
            print(f"[{username}] {max_retries}번의 시도 후 로그인 실패로 건너뜀")
            if browser:
                await browser.close()
            return

        try:
            print(f"[{username}] 프로필로 이동 중...")
            await page.goto(f"https://www.instagram.com/{username}/")
            await page.wait_for_load_state("networkidle")
            await inject_unfollower_script(page)

            unfollowers_data = await collect_unfollowers(page, username)

            if unfollowers_data:
                print(
                    f"[{username}] {len(unfollowers_data)}명의 언팔로워를 데이터베이스에 저장 중..."
                )
                count = await unfollower_db.upsert_unfollowers(
                    db_session, username, unfollowers_data
                )
                await db_session.commit()
                print(f"[{username}] {count}명의 언팔로워 저장 완료")
            else:
                print(f"[{username}] 언팔로워를 찾을 수 없습니다")

        except Exception as e:
            print(f"[{username}] 오류: {str(e)}")
            await db_session.rollback()
        finally:
            if browser:
                await browser.close()


async def main():
    print("=" * 60)
    print("언팔로워 수집 스크립트")
    print("=" * 60)

    # Setup database
    settings = get_settings()
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        # Fetch all unfollower service users
        print("\n언팔로워 서비스 사용자 조회 중...")
        from sqlalchemy import select
        from core.models import UnfollowerServiceUser

        result = await session.execute(select(UnfollowerServiceUser))
        users = result.scalars().all()

        if not users:
            print("unfollower_service_user 테이블에서 사용자를 찾을 수 없습니다")
            return

        print(f"처리할 사용자 {len(users)}명 발견\n")

        for user in users:
            try:
                password = decrypt_data(user.password)
                totp_secret = (
                    decrypt_data(user.totp_secret) if user.totp_secret else None
                )

                await process_user(user.username, password, totp_secret, session)

            except Exception as e:
                print(f"[{user.username}] 사용자 처리 중 오류 발생: {str(e)}")
                continue

    print("\n" + "=" * 60)
    print("스크립트 완료")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
