from flask import Flask, request, abort
from flask_cors import CORS, cross_origin

import datetime as dt
import time

servername = "qt-chat-server"
starttime = dt.datetime.now()

known_clients = set([])

app = Flask(__name__)

# Это нужно, если html клиент запускается с локального диска без загрузки на сервер
# Иначе срабатывает защита от cross-site-scripting
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

messages = []

users = {}


def log_client_ip(ip):
    known_clients.add(ip)


def filter_messages(elements, key, min_value):
    new_elements = []
    for element in elements:
        if element[key] > min_value:
            new_elements.append(element)
    return new_elements


@app.route("/")
def index_view():
    log_client_ip(request.remote_addr)
    return f"Welcome to {servername}.For current status click <a href='/status'>here</a>"


@app.route("/status")
def status_view():
    log_client_ip(request.remote_addr)
    return {'status': True,
            'name': servername,
            'time': time.time(),
            'uptime': str(dt.datetime.now() - starttime)
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
    return {'ok': True}


@app.route("/messages")
def messages_view():
    log_client_ip(request.remote_addr)
    try:
        after = float(request.args['after'])
    except:
        abort(400)
    return {'messages': filter_messages(messages, key='time', min_value=after)}


messages.append({'name': 'qt-chat-server', 'time': time.time(), 'text': 'Server started'})
app.run()
