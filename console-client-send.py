import requests

name = input("Enter your name: ")
password = input("Enter your password: ")
while True:
    text = input("> ")
    message = {'name': name, 'text': text, 'password': password}
    requests.post('http://127.0.0.1:5000/send',json=message)
