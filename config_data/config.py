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
class Config:
    tg_bot: TgBot
    db: DatabaseConfig


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
        )
    )
