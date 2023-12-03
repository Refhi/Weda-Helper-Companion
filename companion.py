#!/usr/bin/env python3
# companion for Weda-Helper
# author : refhi
# allow Weda-Helper to communicate with the TPE and start the printing process
from flask import Flask, request
from tpe import send_instruction
try:
    from pynput.keyboard import Controller, Key
except ImportError:
    print('erreur d\'import pyinput')
import time

app = Flask(__name__)
try:
    keyboard = Controller()
except NameError:
    keyboard = None

@app.route('/', methods=['GET'])
def home():
    return "Bienvenue sur l'API de l'application Companion de Weda-Helper. Pour plus d'informations, rendez-vous sur https://github.com/Refhi/Weda-Helper"

@app.route('/<path:subpath>', methods=['GET'])
def analyze_url(subpath):
    # subpath contains the string after the "/"
    
    if subpath == 'print':
        for _ in range(9):
            keyboard.press(Key.tab)
            keyboard.release(Key.tab)
            time.sleep(0.2)
        time.sleep(1)
        for _ in range(2):
            keyboard.press(Key.enter)
            keyboard.release(Key.enter)
            time.sleep(0.2)

    subpath = subpath.split('/')
    if subpath[0] == 'tpe':
        ip = subpath[1]
        port = subpath[2]
        amount = subpath[3]
        send_instruction(amount, ip, port)
    
    # Perform various functions based on the subpath
    
    return f'URL analysis result {subpath}'

if __name__ == '__main__':
    app.run(host='localhost', port=3000)