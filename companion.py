# companion for Weda-Helper
# author : refhi
# allow Weda-Helper to communicate with the TPE and start the printing process
# version 0.10
from urllib.parse import urlparse
import ipaddress
import os
import json
import inputimeout

try:
    from flask import Flask, request, abort
    from flask_cors import CORS

except ImportError:
    print('erreur d\'import flask ou flask_cors, l\'API ne fonctionnera pas')
    print("merci d'installer le module avec la commande suivante : 'pip install flask' et 'pip install flask_cors' dans powershell")
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
try:
    import time
except ImportError:
    print("erreur d'import time")
    input("Press Enter to continue...")

def print_message_with_timestamp(message):
    timestamp = time.time()

    print(f"[{timestamp}] {message}")

app = Flask(__name__)
CORS(app, origins=['chrome-extension://dbdodecalholckdneehnejnipbgalami','https://secure.weda.fr'])
try:
    keyboard = Controller()
except NameError:
    keyboard = None

@app.before_request
def limit_remote_addr():
    if request.remote_addr != '127.0.0.1':
        abort(403)


@app.route('/', methods=['GET'])
def home():
    return ("Bienvenue sur l'API de l'application Companion de Weda-Helper.\n Pour plus d'informations, rendez-vous sur https://github.com/Refhi/Weda-Helper")

@app.route('/print', methods=['GET'])
def send_to_printer():
    # subpath contains the string after the "/"
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)
    return f'Print asked => j\'appuie une fois sur Entrée'

@app.route('/tpe/<amount>', methods=['GET'])
def send_to_tpe(amount):
    ip = app.config['ipTPE']
    port = app.config['portTPE']
    send_instruction(ip, port, amount)
    return f'TPE asked => {amount} cents @ {ip}:{port}'

@app.route('/<subpath>', methods=['GET'])
def wrong_url(subpath):    
    return f'Wrong url asked : {subpath}. it should be /tpe/[amount] or /print'




@app.before_request
def limit_remote_addr():
    if request.remote_addr != '127.0.0.1':
        abort(403)
    if 'apiKey' not in request.args or request.args.get('apiKey') != app.config['apiKey']:
        abort(403)

defaut_config = {
            "server_port": 3000,
            "tpe_ip": "192.168.0.0",
            "tpe_port": 5000,
            "api_key": ""
    }

config_file = "conf.json"

def check_conf(conf):
    # Vérifie la présence des 4 clés nécessaires
    required_keys = ['server_port', 'tpe_ip', 'tpe_port', 'api_key']
    for key in required_keys:
        if key not in conf:
            print(f"Error: Missing key '{key}' in configuration.")
            return False
        
    # Vérifie qu'il n'y a pas de paramètres en trop
    if len(conf) > len(required_keys):
        print("Error: Too many parameters in configuration.")
        return False

    # Vérifie les ports
    try:
        port = int(conf['server_port'])
        portTPE = int(conf['tpe_port'])
        if not (1 <= port <= 65535) or not (1 <= portTPE <= 65535):
            print("Error: Port numbers must be between 1 and 65535.")
            return False
    except ValueError:
        print("Error: Port numbers must be integers.")
        return False

    # Vérifie l'adresse IP
    try:
        ipaddress.ip_address(conf['tpe_ip'])
    except ValueError:
        print("Error: Invalid IP address.")
        return False

    return True

def get_conf_from_file(filename):
    with open(filename, 'r') as file:
        conf = json.load(file)
    return conf

def user_change_conf(conf, defaut_config):
    print('Veuillez entrer les paramètres de configuration de l\'API. "Entrée" pour garder la valeur actuelle.')
    for key in conf:
        new_value = input(f'{key} (Actuellement : {conf[key]}, Par default: {defaut_config[key]}): ')
        if new_value != '':
            conf[key] = new_value
        else:
            print(f'{key} = {conf[key]}')
    
    if check_conf(conf):
        with open(config_file, 'w') as file:
            json.dump(conf, file, indent=4)
        print('La configuration a été sauvegardée.')
        return conf
    else:
        print('La configuration est invalide, veuillez recommencer.')
        user_change_conf(conf, defaut_config)

from inputimeout import inputimeout, TimeoutOccurred

def wait_for_input_or_timeout(conf, defaut_config, timeout=10):
    try:
        print(f'la configuration actuelle est : {conf}')
        user_input = inputimeout(prompt=f'Appuyez sur "Entrée" pour continuer, ou "e" + "Entrée" pour éditer la configuration. Sinon je démarre dans {timeout} secondes. \n', timeout=timeout)
        if user_input.lower() == 'e':
            user_change_conf(conf, defaut_config)
    except TimeoutOccurred:
        print('Je démarre sur le fichier de conf existant.')

if __name__ == '__main__':
    try:
        conf = get_conf_from_file(config_file)
    except FileNotFoundError:
        conf = defaut_config
        conf = user_change_conf(conf, defaut_config)
    if not check_conf(conf):
        print('La configuration est invalide, veuillez recommencer.')
        conf = user_change_conf(conf, defaut_config)

    wait_for_input_or_timeout(conf, defaut_config, 5)

    port = int(conf['server_port'])
    ipTPE = conf['tpe_ip']
    portTPE = int(conf['tpe_port'])
    apiKey = conf['api_key']

    app.config['ipTPE'] = ipTPE
    app.config['portTPE'] = portTPE
    app.config['apiKey'] = apiKey

    print('Bienvenue sur l\'API de l\'application Companion de Weda-Helper. Pour plus d\'informations, rendez-vous sur https://github.com/Refhi/Weda-Helper')
    app.run(host='localhost', port=port)