#!/usr/bin/env python3
# companion for Weda-Helper
# author : refhi
# allow Weda-Helper to communicate with the TPE and start the printing process
# version 0.7
try:
    from flask import Flask, request
except ImportError:
    print('erreur d\'import flask, l\'API ne fonctionnera pas')
    print("merci d'installer le module avec la commande suivante : 'pip install flask' dans powershell")
    input("Exiting. Press Enter to continue...")
    quit()
try:
    from tpe import send_instruction
except ImportError:
    print("erreur d'import tpe. La connexion au tpe ne fonctionnera pas")
    print("merci de vérifier que tpe.py est bien dans le même dossier que companion.py")
    input("Press Enter to continue...")
try:
    from pynput.keyboard import Controller, Key
except ImportError:
    print("erreur d'import pyinput, l'impression ne fonctionnera pas")
    print("merci d'installer le module avec la commande suivante : 'pip install pynput' dans powershell")
    input("Press Enter to continue...")
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
        return f'Print asked => 9 tab input ant 2 enter input'

    subpath = subpath.split('/')
    if subpath[0] == 'tpe':
        ip = subpath[1]
        port = subpath[2]
        amount = subpath[3]
        send_instruction(ip, port, amount)
        return f'TPE asked => {amount} cents @ {ip}:{port}'
    
    # Perform various functions based on the subpath
    
    return f'Wrong url asked : {subpath}. it should be /tpe/[ip]/[port]/[amount] or /print'

if __name__ == '__main__':
    app.run(host='localhost', port=3000)