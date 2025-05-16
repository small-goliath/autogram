from sqlalchemy import Boolean, Column, String, Integer, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class InstagramAccount(Base):
    __tablename__ = "instagram_account"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(32), unique=True, index=True)
    password = Column(String(32), nullable=False)
    enabled = Column(Boolean, default=False, nullable=False)
    session = Column(Text, nullable=False)

class ActionTarget(Base):
    __tablename__ = "action_target"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(32), index=True)
    link = Column(String(255), nullable=False)
    monday = Column(String(32), nullable=False, index=True)
    sunday = Column(String(32), nullable=False, index=True)

class Action(Base):
    __tablename__ = "action"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    action_target_id = Column(Integer, index=True, nullable=False)
    account_id = Column(Integer, index=True, nullable=False)