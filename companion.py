# companion for Weda-Helper
# author : refhi
# allow Weda-Helper to communicate with the TPE and start the printing process
# version 1.2
version = '1.1' # version de l'API
from urllib.parse import urlparse
import ipaddress
import os

import tempfile # nécessaire pour l'impression
import subprocess # nécessaire pour l'impression sous linux
# nécessite également import win32print sous windows pour récupérer la liste des imprimantes



try:
    from flask import Flask, request, abort, jsonify
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

@app.route('/print', methods=['POST'])
def send_to_printer():
    if 'application/pdf' not in request.headers.get('Content-Type', ''):
        return jsonify({'error': 'Invalid Content-Type, expected application/pdf'}), 400

    pdf_data = request.data

    # Enregistrer le fichier PDF dans un fichier temporaire
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
        temp.write(pdf_data)
        temp_file_name = temp.name

    # Imprimer le fichier
    if os.name == 'nt':  # Si le système d'exploitation est Windows
        if app.config['print_method'] == "default":
            os.startfile(temp_file_name, "print")
        elif app.config['print_method'] == "ghostscript":
            if app.config['printer'] == "Default":
                import win32print
                printer_name = win32print.GetDefaultPrinter()
            else:
                printer_name = app.config['printer']
            # convertir le pdf en fichier postscript
            subprocess.run(["gswin64c", "-dNOPAUSE", "-dBATCH", "-sDEVICE=mswinpr2", "-sOutputFile=%printer%WEDA-Printer", temp_file_name])

    else:  # Pour les autres systèmes d'exploitation (Linux, MacOS)
        subprocess.run(["lpr", temp_file_name])

    # Supprimer le fichier temporaire
    os.remove(temp_file_name)

    return jsonify({'info':'Impression demandée pour le fichier PDF'}), 200

@app.route('/tpe/<amount>', methods=['GET'])
def send_to_tpe(amount):
    ip = app.config['ipTPE']
    port = app.config['portTPE']
    send_instruction(ip, port, amount)
    return jsonify({'info': f'TPE asked => {amount} cents @ {ip}:{port}'}), 200

@app.route('/<subpath>', methods=['GET'])
def wrong_url(subpath):    
    return jsonify({'error': f'Wrong url asked : {subpath}. it should be /tpe/[amount] or /print suivi de ?apiKey=[apiKey]&versioncheck=[version]'}), 404

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
    required_keys = ['port', 'ipTPE', 'portTPE', 'apiKey', 'print_method', 'printer']
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
    
    # Vérifie que la clé API n'est pas celle par défaut
    if conf['apiKey'] == 'tobechanged':
        print("Erreur: la clé API key ne doit pas rester à sa valeur par défaut. Vérifiez dans les options de Weda-Helper et dans le fichier conf.ini")
        return False

    # vérifie que la méthode d'impression est valide
    if conf['print_method'] not in ['default', 'ghostscript']:
        print("Erreur: la méthode d'impression doit être 'default' ou 'ghostscript'")
        return False
    

    return True

@app.before_request
def limit_remote_addr():
    if request.remote_addr != '127.0.0.1':
        abort(403)
    if 'apiKey' not in request.args or request.args.get('apiKey') != app.config['apiKey']:
        abort(jsonify({
            'error': f'Clé API non fournie ou non conforme. Elle doit être notée dans le fichier conf.ini et dans les options de l\'extension Chrome',
            }), 403)    
    if 'versioncheck' not in request.args or request.args.get('versioncheck') != version:
        version_demandee = request.args.get('versioncheck')
        # abort(403)
        abort(jsonify({
            'error': f'version du Companion {version} incompatible avec la version demandée {version_demandee}. Veuillez mettre à jour Weda-Helper-Companion en téléchargant la dernière version sur https://github.com/Refhi/Weda-Helper-Companion/releases/latest/download/companion.exe',
            }), 403)

defaut_conf = """// Fichier de configuration
// Ce fichier contient les paramètres de configuration pour le Weda Helper Companion.
// L'executable est téléchargeable sur https://github.com/Refhi/Weda-Helper-Companion/releases/latest/download/companion.exe

// Numéro de port pour le serveur
port = 3000

// Adresse IP du TPE
ipTPE = 192.168.1.35
portTPE = 5000

// clé API
apiKey = tobechanged

// Méthode d'impression sous windows. Accepte les arguments suivants :
// - default : utilise le programme par défaut pour imprimer les fichiers PDF. Il est recommandé de mettre acrobat reader par défaut.
// - ghostscript : passe par ghostscript pour imprimer directement sur l'imprimante par défaut.
//                 nécessite d'installer ghostscript sur la machine par exemple via https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/download/gs10021/gs10021w64.exe
print_method = default

// Nom de l'imprimante à utiliser sous windows. Nécessaire si print_method = ghostscript. Mettre à Default pour utiliser l'imprimante par défaut.
printer = Default

"""

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
    app.config['print_method'] = conf['print_method']
    app.config['printer'] = conf['printer']


    print('Bienvenue sur l\'API de l\'application Companion de Weda-Helper. Pour plus d\'informations, rendez-vous sur https://github.com/Refhi/Weda-Helper')
    app.run(host='localhost', port=port)