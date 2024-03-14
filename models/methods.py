from sqlalchemy import create_engine, select, delete
from sqlalchemy.orm import Session
from config_data.config import load_config

from models.models import Base, Game, User, Promo, GameResult, Giveaway

#sqlite_file_name = "models/database.db"
#sqlite_url = f'sqlite:///{sqlite_file_name}'


config = load_config()
db_url = config.db.url


engine = create_engine(db_url, echo=False)

def create_db_and_tables():
    Base.metadata.create_all(engine)
    # connection = engine.connect()

    # cursor = connection.cursor()
    # cursor.execute('create database db')

def save_game_result(game_result: GameResult):
    with Session(engine) as session:
        session.add(game_result)
        session.commit()

def get_game_results(username=None, label=None, sequence_label=None, is_correct=None) -> list[GameResult]:
    statement = select(GameResult)
    if username != None:
        statement = statement.where(GameResult.username == username)
    if label != None:
        statement = statement.where(GameResult.label == label)
    if sequence_label != None:
        statement = statement.where(GameResult.sequence_label == sequence_label)
    if is_correct != None:
        statement = statement.where(GameResult.is_correct == is_correct)

    with Session(engine) as session:
        game_results = session.scalars(statement).all()
    return game_results

def save_game(game: Game):
    with Session(engine) as session:
        session.add(game)
        session.commit()


def update_game(label: str, updates: dict):
    with Session(engine) as session:
        session.query(Game).\
            filter(Game.label == label).\
            update(updates)
        session.commit()


def get_games():
    with Session(engine) as session:
        statement = select(Game)
        games = session.execute(statement)
    return games

def get_game(label=None, sequence_label=None):
    with Session(engine) as session:
        statement = select(Game)
        if label != None:
            statement = statement.where(Game.label == label)
        if sequence_label != None:
            statement = statement.where(Game.sequence_label == sequence_label)
        game = session.scalars(statement).first()
    return game


def get_giveaways():
    with Session(engine) as session:
        statement = select(Giveaway)
        giveaways = session.scalars(statement).all()
    return giveaways

def get_giveaway(label, user_id=None):
    with Session(engine) as session:
        statement = select(Giveaway).where(Giveaway.label == label)
        if user_id != None:
            statement = statement.where(Giveaway.user_id == user_id)
        giveaway = session.scalars(statement).first()
    return giveaway


def save_giveaway(giveaway: Giveaway):
    with Session(engine) as session:
        session.add(giveaway)
        session.commit()


def save_user(user: User):
    with Session(engine) as session:
        user.is_admin = user.user_id in config.tg_bot.admin_ids
        session.add(user)
        session.commit()


def update_user(user_id: int, updates: dict):
    with Session(engine) as session:
        session.query(User).\
            filter(User.user_id == user_id).\
            update(updates)
        session.commit()


def get_users(is_admin=False):
    with Session(engine) as session:
        statement = select(User)
        if is_admin:
            statement = statement.where(User.is_admin)
        users = session.scalars(statement).all()
    return users


def get_user(user_id: int):
    with Session(engine) as session:
        statement = select(User).where(User.user_id == user_id)
        user = session.scalars(statement).first()
    return user


def get_user_by_username(username: str):
    with Session(engine) as session:
        statement = select(User).where(User.username == username)
        user = session.scalars(statement).first()
    return user


def get_promos(active=False):
    with Session(engine) as session:
        if active:
            statement = select(Promo).where(Promo.status == 'active')
        else:
            statement = select(Promo)
        promos = session.scalars(statement).all()
    return promos


def get_promo(label: str):
    with Session(engine) as session:
        statement = select(Promo).where(Promo.label == label)
        promo = session.scalars(statement).first()
    return promo


def save_promo(promo: Promo):
    with Session(engine) as session:
        session.add(promo)
        session.commit()


def toggle_promo(label: str):
    with Session(engine) as session:
        statement = select(Promo).where(Promo.label == label)
        promo: Promo = session.scalars(statement).first()
        if promo.status == 'active':
            promo.status = 'inactive'
        else:
            promo.status = 'active'
        session.commit()


def delete_promo(label: str):
    with Session(engine) as session:
        promo = get_promo(label)
        session.delete(promo)
        session.commit()
