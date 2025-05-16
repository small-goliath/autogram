import os
from typing import List
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
from app.logger import get_logger
from app.model.entity import Action, ActionTarget, InstagramAccount

class Database():
    def __init__(self):
        load_dotenv()
        database_url = os.environ.get('DATABASE_URL')
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)
        self.log = get_logger("root")

    def search_instagram_accounts(self):
        session = self.Session()
        try:
            return session.query(InstagramAccount).filter_by(enabled=True).all()
        finally:
            session.close()

    def save_action_targets(self, targets: List[ActionTarget]):
        session = self.Session()
        try:
            session.bulk_save_objects(targets)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            self.log(f"action targets을 저장할 수 없습니다: {e}")
            raise
        finally:
            session.close()

    def save_actions(self, actions: List[Action]):
        session = self.Session()
        try:
            session.bulk_save_objects(actions)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            self.log(f"actions를 저장할 수 없습니다: {e}")
            raise
        finally:
            session.close()

    def search_action_targets(self, account_id: int) -> List[ActionTarget]:
        session = self.Session()
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
        finally:
            session.close()