from sqlalchemy import Column, Integer, String, DateTime, Boolean, BigInteger

# from sqlalchemy.types import ARRAY
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(
        Integer, nullable=False, unique=True, primary_key=True, autoincrement=True
    )
    user_id = Column(BigInteger, index=True)
    name = Column(String)
    phone = Column(String)
    # city = Column(String)
    points = Column(Integer)
    is_admin = Column(Boolean)
    username = Column(String)
    mail = Column(String)
    last_call = Column(
        String
    )  # latest message "Давай поиграем?" id to delete it on /game_stop
    last_call_giveaway = Column(String)
    last_call_long = Column(String)


class Game(Base):
    __tablename__ = "games"
    id = Column(
        Integer, nullable=False, unique=True, primary_key=True, autoincrement=True
    )
    text = Column(String)
    type = Column(String)
    sequence_label = Column(String)
    label = Column(String, index=True)
    options = Column(String)
    answers = Column(String)
    images = Column(String)
    full_answer = Column(String)
    final_message = Column(String)
    # scheduled_time = Column(DateTime)


class Promo(Base):
    __tablename__ = "promos"
    id = Column(
        Integer, nullable=False, unique=True, primary_key=True, autoincrement=True
    )
    label = Column(String, index=True, unique=True)
    description = Column(String)
    image = Column(String)
    status = Column(String)


class GameResult(Base):
    __tablename__ = "game_results"
    id = Column(
        Integer, nullable=False, unique=True, primary_key=True, autoincrement=True
    )
    username = Column(String)
    label = Column(String, index=True)
    sequence_label = Column(String, index=True)
    is_correct = Column(Boolean)


class Giveaway(Base):
    __tablename__ = "giveaways"
    id = Column(
        Integer, nullable=False, unique=True, primary_key=True, autoincrement=True
    )
    label = Column(String)
    username = Column(String)
    user_id = Column(BigInteger, index=True)
