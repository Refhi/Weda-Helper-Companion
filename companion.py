# companion for Weda-Helper
# author : refhi
# allow Weda-Helper to communicate with the TPE and start the printing process
# version 0.9
from urllib.parse import urlparse

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
CORS(app, origins=['chrome-extension://fnfdbangkcmjacbeaaiongkbacaamnfd','https://secure.weda.fr'])
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

@app.route('/print/<primaryd>/<tabsd>/<tabentd>/<entersd>', methods=['GET'])
def send_to_printer(primaryd, tabsd, tabentd, entersd):
    # subpath contains the string after the "/"
    delay_before_print = float(primaryd) # suggested 0.02
    delay_btw_tabs = float(tabsd) # suggested 0.01
    delay_btw_tab_and_enter = float(tabentd) # 0.01
    delay_btw_enters = float(entersd) # 0.5                
    to_test = [delay_before_print,delay_btw_tabs, delay_btw_tab_and_enter, delay_btw_enters]
    # check that all delays are between 0.0001 and 10, else exit
    for delay in to_test:
        if delay < 0.0001 or delay > 10:
            return f'Wrong delay asked : {delay}. It should be between 0.0001 and 10'
    print('delay before print')
    time.sleep(delay_before_print)
    print('press tab 9 times')
    for _ in range(9):
        print_message_with_timestamp('press tab')
        keyboard.press(Key.tab)
        keyboard.release(Key.tab)
        time.sleep(delay_btw_tabs)
    time.sleep(delay_btw_tab_and_enter)
    for _ in range(2):
        print_message_with_timestamp('press enter')
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
        time.sleep(delay_btw_enters)
    return f'Print asked => 9 tab input ant 2 enter input'

@app.route('/tpe/<ip>/<port>/<amount>', methods=['GET'])
def send_to_tpe(ip, port, amount):
    send_instruction(ip, port, amount)
    return f'TPE asked => {amount} cents @ {ip}:{port}'

@app.route('/<subpath>', methods=['GET'])
def wrong_url(subpath):    
    return f'Wrong url asked : {subpath}. it should be /tpe/[ip]/[port]/[amount] or /print'

def get_port_from_conf_file(filename):
    with open(filename, 'r') as file:
        for line in file:
            if line.startswith('port'):
                return int(line.split('=')[1].strip())

if __name__ == '__main__':
    # get the port from the conf file
    port = get_port_from_conf_file('conf.txt')
    print('Bienvenue sur l\'API de l\'application Companion de Weda-Helper. Pour plus d\'informations, rendez-vous sur https://github.com/Refhi/Weda-Helper')
    app.run(host='localhost', port=port)