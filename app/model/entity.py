from sqlalchemy import Boolean, Column, ForeignKey, String, Integer, Text
from sqlalchemy.orm import relationship
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

class ActionTargetKakaotalk(Base):
    __tablename__ = "action_target_kakaotalk"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(32))
    link = Column(String(255))
    monday = Column(String(32))
    sunday = Column(String(32))

####

class Producer(Base):
    __tablename__ = "producer"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(32), unique=True, index=True)
    enabled = Column(Boolean, default=False, nullable=False)
    group_id = Column(Integer, index=True)
    session = Column(Text, nullable=False)

class Consumer(Base):
    __tablename__ = "consumer"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(32))
    enabled = Column(Boolean, default=False, nullable=False)

class Payment(Base):
    __tablename__ = "payment"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(32), index=True)
    count = Column(Integer, default=0)
    year_month = Column(String(10), index=True)

class UnfollowerUser(Base):
    __tablename__ = "unfollower_user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(32), unique=True, nullable=False)
    enabled = Column(Boolean, nullable=False, default=False)

    unfollowers = relationship("Unfollower", back_populates="target_user", cascade="all, delete")

class Unfollower(Base):
    __tablename__ = "unfollower"

    id = Column(Integer, primary_key=True, autoincrement=True)
    target_user_id = Column(Integer, ForeignKey("unfollower_user.id", ondelete="CASCADE"), nullable=False)
    username = Column(String(32), nullable=False)
    nickname = Column(Text, nullable=True)

    target_user = relationship("UnfollowerUser", back_populates="unfollowers")