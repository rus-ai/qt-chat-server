from flask import Flask, request, abort, send_from_directory

import datetime as dt
import time

import re
import random

import logging

# add filemode="w" to overwrite
# logging.basicConfig(filename="server.log", level=logging.INFO)

# logging.debug("This is a debug message")
# logging.info("Informational message")
# logging.error("An error has happened!")

servername = "qt-chat-server"
starttime = dt.datetime.now()

# По умолчанию бот активен, можно поставить False тогда он включится только по команде

bot_active = True

ip_base_filename = '.\ip.csv'

try:
    known_ip = set(map(str.strip, open(ip_base_filename)))
except:
    known_ip = set()

ip_base = open(ip_base_filename, "a+")


app = Flask(__name__)

messages = []

users = {}


def log_client_ip(ip):
    ip_learned = len(known_ip)
    known_ip.add(ip)
    if ip_learned != len(known_ip):
        ip_base.write(str(ip)+'\n')
        ip_base.flush()


# Функция логики бота вызывается после каждого сообщени пользователей,
# если ответить нечего возвращает пустую строку
def chat_bot(text):
    # Глобальная переменная активность бота, задается в конфиге
    # По умолчанию True
    global bot_active
    # Бот отвечает только если он активен
    if bot_active is True:
        # Чат-бот работает по ключевым словам, но использует стоп слова,
        # чтобы в ответ на "спасибо не булькает" не отвечать "Пожалуйста"
        # на каждый сценарий предусмотрен случайный выбор ответа из списка
        # поиск нечувствителен к регистру
        # на "здоров" отвечает приветствием на "здоровье" не отвечаем
        if re.search('(?i)доброй|спокойной', text) and re.search('(?i)ночи|ночки', text):
            return random.choice(['Сладких снов!', 'Доброй ночи!', 'Спокойной ночи!'])
        if re.search('(?i)добрый|доброго|хорошего', text) and re.search('(?i)дня|день|вечер|вечера|утро|утра', text):
            return random.choice(['Доброго времени суток!', text])
        if re.search('(?i)привет|здравс|здоров|прива|хай|хэлоу', text) and not re.search('(?i)здоровье|приват', text):
            return random.choice(['Привет!', 'Мое почтение!', 'Здравствуйте!', 'Салют!'])
        if re.search('(?i)апхчи|чхи', text):
            return random.choice(['Будь здоров!', 'Будь здоров! Рости большой!', 'У вас коронавирус?', 'Простудились?'])
        if re.search('(?i)спасибо', text) and not re.search('(?i)не булькает|на хлеб не намажешь', text):
            return random.choice(['Пожалуйста!', 'Не за что!', 'На здоровье', 'Не стоит благодарности'])
        # Если уточнят что сказать любое или случайное, то так и быть
        # Если изначально сказали загадать или придумать, то запускаем рандом
        if ((re.search('(?i)скажи', text) and re.search('(?i)случайное|любое', text)) or re.search(
                '(?i)загадай|придумай|сгенерируй', text)) and re.search('(?i)число', text):
            return random.choice(['Загадал: ', 'Придумал: ', 'Пусть будет: ', 'Ну например: ']) + str(
                random.randint(0, 100))
        # Если просят сказать число то включаем дурачка, уточняем
        if re.search('(?i)скажи', text) and re.search('(?i)число', text):
            return random.choice(['Какое число сказать?', 'В смысле?', 'Случайное или как?', 'Мое любимое?'])
        # Если бот достал, то его можно попросить заткнуться
        if re.search('(?i)останови|заткни|выключи|выруби', text) and re.search('(?i)бота|трепло|киборг', text):
            bot_active = False
            return random.choice(['Молчу!', 'Выключил.', 'Отключаюсь', 'Умолкаю'])
    else:
        # Если бот неактивен слушаем просьбы включить
        # Прямой приказ
        if re.search('(?i)запусти|активируй|включи|вруби', text) and re.search('(?i)бота|трепло|киборг|собеседник',
                                                                               text):
            bot_active = True
            return random.choice(['Бот запущен', 'Скайнет активирован', 'Готов поболтать', 'О чем поговорим?'])
        # На намек что скучно тоже реагируем
        if re.search('(?i)что то|что-то|чтото', text) and re.search('(?i)скучно|грустно', text):
            bot_active = True
            return random.choice(['Бот запущен', 'Скайнет активирован', 'Готов поболтать', 'О чем поговорим?'])
    return ''


def filter_messages(elements, key, min_value):
    new_elements = []
    for element in elements:
        if element[key] > min_value:
            new_elements.append(element)
    return new_elements


@app.route("/")
def index_view():
    log_client_ip(request.remote_addr)
    return f"Welcome to {servername}. For current status click <a href='/status'>here</a><br/>For web-client click <a href='/webclient'>here</a>"


@app.route("/webclient")
def webclient_view():
    log_client_ip(request.remote_addr)
    return send_from_directory(directory=".", filename='web-client.html')


@app.route("/status")
def status_view():
    log_client_ip(request.remote_addr)
    return {'status': True,
            'name': servername,
            'time': time.time(),
            'uptime': str(dt.datetime.now() - starttime),
            'client-ip': request.remote_addr,
            'clients-ip-served': len(known_ip),
            'users-registered': len(users),
            'messages-count': len(messages)
            }


@app.route("/send", methods=['POST'])
def send_view():
    log_client_ip(request.remote_addr)
    name = request.json.get('name')
    password = request.json.get('password')
    text = request.json.get('text')
    for token in [name, password, text]:
        if not (isinstance(token, str) and (len(token) > 0) and (len(token) < 1024)):
            abort(400)
    if name in users:
        if users[name] != password:
            abort(401)
    else:
        users[name] = password
    messages.append({'name': name, 'time': time.time(), 'text': text})
    reply = chat_bot(text)
    if reply != '':
        messages.append({'name': servername, 'time': time.time(), 'text': reply})

    return {'ok': True}


@app.route("/messages")
def messages_view():
    log_client_ip(request.remote_addr)
    try:
        after = float(request.args['after'])
    except:
        abort(400)
    return {'messages': filter_messages(messages, key='time', min_value=after)}


messages.append({'name': servername, 'time': time.time(), 'text': 'Server started'})
app.run(host='0.0.0.0')
