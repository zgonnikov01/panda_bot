from dataclasses import dataclass
from environs import Env


@dataclass
class DatabaseConfig:
    url: str
    password: str
    user: str
    port: str
    host: str
    

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
    backup_dir: str


def load_config() -> Config:

    path = ".env"
    env: Env = Env()
    env.read_env(path)

    _password = env.str("PG_PASSWORD")
    _host = env.str("PG_HOST")
    _user = env.str("PG_USER")
    _port = env.str("PG_PORT")

    _url = f"postgresql+psycopg2://{_user}:{_password}@{_host}:{_port}"

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            admin_ids=[int(id) for id in env.list("ADMIN_IDS")]
        ),
        db=DatabaseConfig(
            host=_host,
            user=_user,
            port=_port,
            password=_password,
            url=_url
        ),
        mongodb=MongoDB(
            username = env.str("MONGO_INITDB_ROOT_USERNAME"),
            password = env.str("MONGO_INITDB_ROOT_PASSWORD")
        ),
        bamps=Bamps(
            api_url = env.str("BAMPS_API_URL"),
            api_token = env.str("BAMPS_API_TOKEN")
        ),
        backup_dir=env.str("BACKUP_DIR")
    )

config = load_config()
