from dataclasses import dataclass
from environs import Env


@dataclass
class DatabaseConfig:
    url: str
    

@dataclass
class TgBot:
    token: str
    admin_ids: list[int]

@dataclass
class MongoDB:
    username: str
    password: str

@dataclass
class Bamps:
    api_url: str
    api_token: str

@dataclass
class Config:
    tg_bot: TgBot
    db: DatabaseConfig
    mongodb: MongoDB
    bamps: Bamps


def load_config() -> Config:

    path = '.env'
    env: Env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env.str('BOT_TOKEN'),
            admin_ids=[int(id) for id in env.list('ADMIN_IDS')]
        ),
        db=DatabaseConfig(
            url = env.str('DB_URL')
        ),
        mongodb=MongoDB(
            username = env.str('MONGO_USERNAME'),
            password = env.str('MONGO_PASSWORD')
        ),
        bamps=Bamps(
            api_url = env.str('BAMPS_API_URL'),
            api_token = env.str('BAMPS_API_TOKEN')
        )
    )
