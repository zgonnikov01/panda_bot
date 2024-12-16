import datetime

from pymongo import MongoClient

from config_data.config import load_config


config = load_config()


def get_current_date():
    return datetime.datetime.now().strftime('%Y-%m-%d')


def get_mongodb():
    client = MongoClient(
        'mongodb://panda_bot-mongodb-1',
        username=config.mongodb.username,
        password=config.mongodb.password
    )
    mongo = client.database
    return mongo

