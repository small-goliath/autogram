from contextlib import contextmanager
import os
from typing import List
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
from app.logger import get_logger
from app.model.entity import Action, ActionTarget, Consumer, InstagramAccount, Producer

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
        
class Database():
    def __init__(self):
        self.log = get_logger("root")

    def search_instagram_account(self, session: Session, username: str) -> InstagramAccount:
        return session.query(InstagramAccount).filter_by(username=username).first()

    def search_instagram_accounts(self, session: Session) -> List[InstagramAccount]:
        return session.query(InstagramAccount).filter_by(enabled=True).all()

    def save_action_targets(self, session: Session, targets: List[ActionTarget]):
        try:
            session.bulk_save_objects(targets)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            self.log(f"action targets을 저장할 수 없습니다: {e}")
            raise

    def save_actions(self, session: Session, actions: List[Action]):
        try:
            session.bulk_save_objects(actions)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            self.log(f"actions를 저장할 수 없습니다: {e}")
            raise

    def search_action_targets(self, session: Session, account_id: int) -> List[ActionTarget]:
        try:
            query = (
                session.query(ActionTarget)
                .outerjoin(Action, (ActionTarget.id == Action.action_target_id) & (Action.account_id == account_id))
                .filter(Action.id == None)
                .all()
            )
            return query
        except SQLAlchemyError as e:
            self.log(f"action targets을 조회할 수 없습니다: {e}")
            raise

    def search_action_targets_by_monday(self, session: Session, account_id: int, target_monday: str) -> List[ActionTarget]:
        try:
            query = (
                session.query(ActionTarget)
                .filter(ActionTarget.id == account_id)
                .filter(ActionTarget.monday == target_monday)
                .all()
            )
            return query
        except SQLAlchemyError as e:
            self.log(f"action targets을 조회할 수 없습니다: {e}")
            raise

    def search_producers(self, session: Session) -> List[Producer]:
        return session.query(Producer).filter_by(enabled=True).all()

    def search_consumers(self, session: Session) -> List[Consumer]:
        return session.query(Consumer).filter_by(enabled=True).all()