from contextlib import contextmanager
import os
from typing import List, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
from app.logger import get_logger
from app.model.entity import Consumer, InstagramAccount, Payment, Producer, SNSRaiseUser, UserActionVerification

load_dotenv()
database_url = os.environ.get('DATABASE_URL')
engine = create_engine(database_url)

@contextmanager
def transactional():
    session = sessionmaker(autocommit=False, autoflush=False, bind=engine)()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()

@contextmanager
def read_only_transactional():
    session = sessionmaker(autocommit=False, autoflush=False, bind=engine)()
    try:
        yield session
        session.rollback()
    finally:
        session.close()

class Database():
    def __init__(self):
        self.log = get_logger("root")

    def search_instagram_account(self, session: Session, username: str) -> InstagramAccount:
        return session.query(InstagramAccount).filter_by(username=username).first()

    def search_instagram_accounts(self, session: Session) -> List[InstagramAccount]:
        return session.query(InstagramAccount).filter_by(enabled=True).all()

    def search_producers(self, session: Session) -> List[Producer]:
        return session.query(Producer).filter_by(enabled=True).all()
    
    def search_producer(self, username: str, session: Session) -> Producer:
        return session.query(Producer).filter_by(username=username).first()

    def search_consumers(self, session: Session) -> List[Consumer]:
        return session.query(Consumer).filter_by(enabled=True).all()
    
    def search_payment(self, session: Session, username: str, year_month: str) -> Payment:
        return session.query(Payment).filter_by(username=username).filter_by(year_month=year_month).first()
    
    def create_payment(self, session: Session, username: str, count: int, year_month: str) -> Payment:
        paument = Payment(username=username, count=count, year_month=year_month)
        return session.add(paument)
    
    def search_sns_raise_users(self, session: Session) -> List[SNSRaiseUser]:
        return session.query(SNSRaiseUser).all()
    
    def save_user_action_verifications(self, session: Session, user_action_verifications: List[UserActionVerification]):
        if user_action_verifications:
            session.add_all(user_action_verifications)

    def save_user_action_verification(self, session: Session, user_action_verification: UserActionVerification):
        if user_action_verification:
            session.add(user_action_verification)

    def search_user_action_verifications(self, session: Session) -> List[UserActionVerification]:
        return session.query(UserActionVerification).all()
    
    def delete_user_action_verification(
        self,
        session: Session, 
        username: Optional[str] = None, 
        link: Optional[str] = None
    ) -> int:
        query = session.query(UserActionVerification)
        filters = {}
        if username:
            filters['username'] = username
        if link:
            filters['link'] = link
        if not filters:
            raise ValueError("username와 link 모두 값이 없습니다.")
        deleted_count = query.filter_by(**filters).delete()
        session.commit()
        return deleted_count