import datetime

from handlers.utils import get_mongodb


async def update_state():
    mongodb = get_mongodb()

    mongodb.lottery_state.drop() 

    current_lottery = mongodb.lotteries.find_one({
        'start': {'$lte': datetime.datetime.now()},
        'end': {'$gt': datetime.datetime.now()}
    })

    if current_lottery:
        n = (current_lottery['end'] - datetime.datetime.now()).days + 1
        gifts = {
            key: value // n for key, value in current_lottery['gifts'].items()
        }
        bonus_points = {
            'quantity': current_lottery['bonus_points']['quantity'] // n,
            'options': current_lottery['bonus_points']['options']
        }
        new_state = {
            'label': current_lottery['label'],
            'gifts': gifts,
            'bonus_points': bonus_points
        }
        mongodb.lottery_state.insert_one(new_state)
        return new_state
