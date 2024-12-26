import json, requests

from config_data.config import load_config


config = load_config()

BAMPS_API_URL = config.bamps.api_url
BAMPS_API_TOKEN = config.bamps.api_token


async def get_balance(phone_number: str) -> str:
    r = requests.post(
        url=BAMPS_API_URL + 'balance',
        headers={
            'x-access-token': BAMPS_API_TOKEN
        },
        json={
            'phone_number': phone_number
        }
    )
    return json.loads(r.text)['data']['bonus_point_amount']


async def refill(phone_number: str, amount: str) -> None:
    r = requests.post(
        url=BAMPS_API_URL + 'refill',
        headers={
            'x-access-token': BAMPS_API_TOKEN
        },
        json={
            'phone_number': phone_number,
            'amount': amount
        }
    )

