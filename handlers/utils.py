import datetime, json
import bson.json_util

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


def wrap_as_json_code(s):
    if type(s) in [list, dict]:
        s = bson.json_util.dumps(s)
    s = json.dumps(json.loads(s), indent=4)
    result = f'<pre><code class="language-json">{s}</code></pre>'
    return(result)


def format_number(n):
    n = n.replace('-', '').replace(' ', '')
    if len(n) == 10:
        return '7' + n
    if len(n) == 11:
        return '7' + n[1:]
    if len(n) == 12:
        return '7' + n[2:]
    return None

