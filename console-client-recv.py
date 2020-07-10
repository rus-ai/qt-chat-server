import requests
import time
import datetime

after = time.time() - 24 * 60 * 60


def format_message(message):
    return f"{message['name']} {datetime.datetime.fromtimestamp(message['time']).strftime('%Y/%m/%d %H:%M:%S')}\n{message['text']}\n"


while True:
    try:
        response = requests.get('http://127.0.0.1:5000/messages', params={'after': after})
        messages = response.json()['messages']
        for message in messages:
            if message['time'] > after:
                after = message['time']
            print(format_message(message))
        time.sleep(1)
    except requests.exceptions.ConnectionError:
        pass


