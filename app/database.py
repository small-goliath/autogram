from contextlib import contextmanager
import os
from typing import List
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
from app.logger import get_logger
from app.model.entity import Action, ActionTarget, Consumer, InstagramAccount, Payment, Producer, Unfollower, UnfollowerUser

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

    def save_unfollowers(self, session: Session, unfollowers: List[Unfollower]):
        session.bulk_save_objects(unfollowers)

    def search_producers(self, session: Session) -> List[Producer]:
        return session.query(Producer).filter_by(enabled=True).all()
    
    def search_producer(self, username: str, session: Session) -> Producer:
        return session.query(Producer).filter_by(username=username).first()

    def search_consumers(self, session: Session) -> List[Consumer]:
        return session.query(Consumer).filter_by(enabled=True).all()
    
    def search_payment(self, session: Session, username: str, year_month: str) -> Payment:
        return session.query(Payment).filter_by(username=username).filter_by(year_month=year_month).first()

    def search_unfollower_users(self, session: Session) -> List[UnfollowerUser]:
        unfollowerUsers = session.query(UnfollowerUser).filter_by(enabled=True).all()
        return [{"id": unfollowerUser.id, "username": unfollowerUser.username} for unfollowerUser in unfollowerUsers]