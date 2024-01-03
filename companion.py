# companion for Weda-Helper
# author : refhi
# allow Weda-Helper to communicate with the TPE and start the printing process
# version 1.0
from urllib.parse import urlparse
import ipaddress
import os



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

def get_conf_from_file(filename):
    conf = {}
    with open(filename, 'r') as file:
        for line in file:
            if line.startswith('//'):
                continue
            # check if the line include a '='
            if '=' in line:
                key, value = line.split('=')
                conf[key.strip()] = value.strip()
            else:
                continue

    if not check_conf(conf):
        print("Error: Fichier de configuration invalide.")
        input("Press Enter to continue...")
        quit()
    return conf


def check_conf(conf):
    # Vérifie la présence des 4 clés nécessaires
    required_keys = ['port', 'ipTPE', 'portTPE', 'apiKey']
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
        port = int(conf['port'])
        portTPE = int(conf['portTPE'])
        if not (1 <= port <= 65535) or not (1 <= portTPE <= 65535):
            print("Error: Port numbers must be between 1 and 65535.")
            return False
    except ValueError:
        print("Error: Port numbers must be integers.")
        return False

    # Vérifie l'adresse IP
    try:
        ipaddress.ip_address(conf['ipTPE'])
    except ValueError:
        print("Error: Invalid IP address.")
        return False

    return True

@app.before_request
def limit_remote_addr():
    if request.remote_addr != '127.0.0.1':
        abort(403)
    if 'apiKey' not in request.args or request.args.get('apiKey') != app.config['apiKey']:
        abort(403)

defaut_conf = """// Fichier de configuration
// Ce fichier contient les paramètres de configuration pour le Weda Helper Companion.


// Numéro de port pour le serveur
port = 3000

// Adresse IP du TPE
ipTPE = 192.168.1.35
portTPE = 5000

// clé API
apiKey = azelkmlsdfpoiert1234"""

if __name__ == '__main__':
    # check if conf.ini exists, if not create it with default values
    try:
        with open('conf.ini', 'r') as file:
            pass
    except FileNotFoundError:
        with open('conf.ini', 'w') as file:
            file.write(defaut_conf)
            print('''Bienvenue dans le companion Weda-Helper.
Un fichier de configuration vient d'être créé avec succès.
''')
        path = os.path.realpath('conf.ini')
        input(f"""l'éditeur devrait s'ouvrir automatiquement.
En général le port 3000 est adapté, mais en cas de difficulté, n'hésitez pas à le modifier (ex. 4561 ou 7320)
Ce port est également à modifier dans les options de l'extension chrome
Si ce n'est pas le cas, ouvrez le fichier conf.ini avec un éditeur de texte et remplissez les paramètres nécessaires.
Le fichier est situé dans {path}
Appuyez sur Entrée pour continuer...""")
        os.system(f'start notepad {path}')
        input("Quand vous avez fini, Appuyez sur Entrée pour continuer...")
    conf = get_conf_from_file('conf.ini')
    if not check_conf(conf):
        print("Error: Fichier de configuration invalide.")
        path = os.path.realpath('conf.ini')
        print(f"Le fichier est situé dans {path}, merci de le vérifier. Pour le remettre à zéro, supprimez-le puis relancez l'application.")
        input("Appuyez sur Entrée pour quitter...")
        quit()
    port = int(conf['port'])
    ipTPE = conf['ipTPE']
    portTPE = int(conf['portTPE'])
    apiKey = conf['apiKey']

    app.config['ipTPE'] = ipTPE
    app.config['portTPE'] = portTPE
    app.config['apiKey'] = apiKey

    print('Bienvenue sur l\'API de l\'application Companion de Weda-Helper. Pour plus d\'informations, rendez-vous sur https://github.com/Refhi/Weda-Helper')
    app.run(host='localhost', port=port)