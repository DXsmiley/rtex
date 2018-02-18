'''

    Used to track internal statictics, such
    as the number of requests, the failrue
    rate, etc.

'''

import json
import time
import itertools
import logs


STORAGE = {}
LAST_SAVE = 0
SAVE_INTERVAL = 60


def current_second():
    return int(time.time())


def current_day():
    return current_second() // 86400


def load():
    try:
        with open('stats.json') as f:
            jd = json.load(f)
            d = {int(k): v for k, v in jd.items()}
            return strip_old_data(d)
    except json.JSONDecodeError:
        logs.info("Error decoding stats.json, will recreate it.")
    except FileNotFoundError:
        logs.info("Could not find stats.json, will create it.")
    else:
        return {}


def save(data):
    with open('stats.json', 'w') as f:
        json.dump(data, f)


def save_maybe(data):
    global LAST_SAVE
    global SAVE_INTERVAL
    now = current_second()
    if now - LAST_SAVE > SAVE_INTERVAL:
        strip_old_data(data)
        save(data)
        LAST_SAVE = now


def strip_old_data(data):
    day = current_day()
    to_remove = [i for i in data if day - i >= 60]
    for i in to_remove:
        del data[i]
    return data


def track_event(name, *extra, count = 1):
    global STORAGE
    for i in itertools.chain([name], extra):
        day = current_day()
        STORAGE[day] = STORAGE.get(day, {})
        STORAGE[day][i] = STORAGE[day].get(i, 0) + count
    save_maybe(STORAGE)


def get_column(name):
    day = current_day()
    return [
        STORAGE.get(i, {}).get(name, 0)
        for i in range(day, day - 60, -1)
    ]


STORAGE = load()
