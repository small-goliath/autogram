"""Business logic for Instagram operations."""
from sqlalchemy.ext.asyncio import AsyncSession
from core.instagram_helper import InstaloaderHelper, InstagrapiHelper
from core.crypto import encrypt_data, decrypt_data
from core.db import helper_db, producer_db


async def check_unfollowers(
    db: AsyncSession,
    username: str,
    password: str,
    verification_code: str | None = None,
    use_helper: bool = True
) -> list[str]:
    """
    Check unfollowers for a user.

    Args:
        db: Database session
        username: Instagram username
        password: Instagram password
        verification_code: Optional 2FA verification code
        use_helper: Whether to try using helper account first

    Returns:
        List of usernames that don't follow back

    Raises:
        Exception: If check fails
    """
    helper = InstaloaderHelper()

    # Try to use existing helper account first
    if use_helper:
        helper_account = await helper_db.get_active_helper(db)
        if helper_account and helper_account.session_data:
            try:
                helper.load_session_from_data(
                    helper_account.instagram_username,
                    helper_account.session_data
                )
                unfollowers = helper.check_unfollowers(username)
                await helper_db.update_helper_last_used(db, helper_account.id)
                return unfollowers
            except Exception:
                # If helper fails, fall back to direct login
                pass

    # Direct login
    helper.login(username, password, verification_code)
    unfollowers = helper.check_unfollowers(username)
    return unfollowers


async def register_helper_account(
    db: AsyncSession,
    username: str,
    password: str,
    verification_code: str | None = None
) -> dict:
    """
    Register a new helper account.

    Args:
        db: Database session
        username: Instagram username
        password: Instagram password
        verification_code: Optional 2FA verification code

    Returns:
        Created helper info dict

    Raises:
        Exception: If login or registration fails
    """
    # Check if helper already exists
    existing = await helper_db.get_helper_by_username(db, username)
    if existing:
        raise Exception("Helper account already exists")

    # Try to login and save session
    helper = InstaloaderHelper()
    helper.login(username, password, verification_code)

    # Save session data
    session_data = helper.save_session_to_data()

    # Encrypt password
    encrypted_password = encrypt_data(password)

    # Create helper record
    helper_record = await helper_db.create_helper(
        db,
        instagram_username=username,
        instagram_password=encrypted_password,
        session_data=session_data
    )

    return {
        "id": helper_record.id,
        "instagram_username": helper_record.instagram_username,
        "is_active": helper_record.is_active
    }


async def register_producer_account(
    db: AsyncSession,
    username: str,
    password: str,
    verification_code: str | None = None
) -> dict:
    """
    Register a new producer account.

    Args:
        db: Database session
        username: Instagram username
        password: Instagram password
        verification_code: Optional 2FA verification code

    Returns:
        Created producer info dict

    Raises:
        Exception: If login or registration fails
    """
    # Check if producer already exists
    existing = await producer_db.get_producer_by_username(db, username)
    if existing:
        raise Exception("Producer account already exists")

    # Try to login and save session
    client = InstagrapiHelper()
    client.login(username, password, verification_code)

    # Save session data
    session_data = client.save_session_to_data()

    # Encrypt password
    encrypted_password = encrypt_data(password)

    # Create producer record
    producer_record = await producer_db.create_producer(
        db,
        instagram_username=username,
        instagram_password=encrypted_password,
        verification_code=verification_code,
        session_data=session_data
    )

    return {
        "id": producer_record.id,
        "instagram_username": producer_record.instagram_username,
        "status": producer_record.status
    }


async def get_helper_client(db: AsyncSession, helper_id: int) -> InstaloaderHelper:
    """
    Get InstaloaderHelper client for a helper account.

    Args:
        db: Database session
        helper_id: Helper account ID

    Returns:
        InstaloaderHelper instance

    Raises:
        Exception: If helper not found or session load fails
    """
    helper = await helper_db.get_helper_by_id(db, helper_id)
    if not helper:
        raise Exception("Helper account not found")

    client = InstaloaderHelper()
    if helper.session_data:
        client.load_session_from_data(helper.instagram_username, helper.session_data)
    else:
        # Fallback: login with password
        password = decrypt_data(helper.instagram_password)
        client.login(helper.instagram_username, password)
        # Save new session
        session_data = client.save_session_to_data()
        await helper_db.update_helper_session(db, helper_id, session_data)

    return client


async def get_producer_client(db: AsyncSession, producer_id: int) -> InstagrapiHelper:
    """
    Get InstagrapiHelper client for a producer account with proactive session management.

    Args:
        db: Database session
        producer_id: Producer account ID

    Returns:
        InstagrapiHelper instance

    Raises:
        Exception: If producer not found or session load fails
    """
    producer = await producer_db.get_producer_by_username(db, str(producer_id))
    if not producer:
        raise Exception("Producer account not found")

    # Decrypt password first (needed for both session load and fallback)
    password = decrypt_data(producer.instagram_password)

    client = InstagrapiHelper()
    session_updated = False

    if producer.session_data:
        try:
            # Try to load existing session
            client.load_session_from_data(producer.instagram_username, password, producer.session_data)

            # Proactive session validation and refresh if needed
            try:
                client.validate_and_refresh_if_needed(
                    producer.instagram_username,
                    password,
                    producer.verification_code
                )
                session_updated = True
            except Exception:
                # If validation/refresh fails, continue with current session
                pass

        except Exception:
            # Fallback: login with password if session is invalid
            client.login(producer.instagram_username, password, producer.verification_code)
            session_updated = True
    else:
        # No session: login with password
        client.login(producer.instagram_username, password, producer.verification_code)
        session_updated = True

    # Save session if it was updated
    if session_updated:
        try:
            session_data = client.save_session_to_data()
            await producer_db.update_producer_session(db, producer_id, session_data)
        except Exception:
            # Session save failed, but client is still usable
            pass

    return client
