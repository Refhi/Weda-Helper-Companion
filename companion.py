# companion for Weda-Helper
# author : refhi
# allow Weda-Helper to communicate with the TPE and start the printing process
version = '1.2'
from urllib.parse import urlparse
import ipaddress
import os

import tempfile # nécessaire pour l'impression
import subprocess # nécessaire pour l'impression sous linux
import threading 

import win32gui # nécessaire si besoin de travailler sur le vol de focus d'adobe reader



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



def remove_file_after_delay(filename, delay):
    time.sleep(delay)
    try:
        os.remove(filename)
    except Exception as e:
        print(f"Erreur: Je n'ai pas pu supprimer le fichier temporaire (un programme est-il en train de l'utiliser ?) '{filename}': {e}")


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

@app.route('/focus', methods=['GET'])
def get_focus_back():
    print('je demande à récupérer le focus sur la fenêtre de Weda')
    win32gui.SetForegroundWindow(app.config["weda_handle"])

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
        try:
            #pb de vol de focus, cf. https://stackoverflow.com/questions/6312627/windows-7-how-to-bring-a-window-to-the-front-no-matter-what-other-window-has-fo/6324105#6324105
            app.config["weda_handle"] = win32gui.GetForegroundWindow()
            print(f'weda_handle = {app.config["weda_handle"]}')
            os.startfile(temp_file_name, "print")
        except Exception as e:
            errormessage = "Erreur lors de l'impression du fichier PDF. Vérifiez que vous avez bien un logiciel d'impression PDF par défaut (Recommandé = Acrobat Reader)."
            print(errormessage, e)
            return jsonify({'error': errormessage}), 500
    else:  # Pour les autres systèmes d'exploitation (Linux, MacOS)
        subprocess.run(["lpr", temp_file_name])

    # Supprimer le fichier temporaire après 60 secondes
    threading.Thread(target=remove_file_after_delay, args=(temp_file_name, 20)).start()
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
    
    # Vérifie que la clé API n'est pas celle par défaut
    if conf['apiKey'] == 'tobechanged':
        print("Erreur: la clé API key ne doit pas rester à sa valeur par défaut. Vérifiez dans les options de Weda-Helper et dans le fichier conf.ini")
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

// Numéro de port pour le serveur (en général 3000 est ok, mais n'hésitez pas à le changer si ça ne fonctionne pas)
port = 4821

// Adresse IP du TPE (à récupérer auprès de votre installateur de TPE.
// Demandez-leur d'activer la connexion avec un appareil et de préciser le port et l'adresse IP)
ipTPE = 192.168.1.35
portTPE = 5000

// clé API (à récupérer dans les options de l'extension)
apiKey = tobechanged"""

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
        input(f"""Afin de préparer la configuration, un éditeur devrait s'ouvrir automatiquement.
Suivez les instructions dans le fichier puis sauvegardez-le, fermez-le et revenez ici.

En cas de difficulté, vous pourrez éditer manuellement le fichier conf.ini que vous trouverez ici :
{path}
Il suffit de l'éditer avec le bloc-note de Windows ou un éditeur de texte et de le sauvegarder.

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