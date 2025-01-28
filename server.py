"""
server.py

Il s'agit d'un serveur Flask qui permet à l'extension Chrome Weda-Helper de communiquer avec un terminal de
paiement électronique (TPE) et de lancer des impressions de documents.

Fonctionnalités principales :
- Vérification de la compatibilité de la version de l'extension Chrome.
- Gestion des requêtes API sécurisées avec une clé API.
- Impression de fichiers PDF.
- Envoi d'instructions au TPE.
- Récupération du dernier fichier téléchargé dans un dossier spécifié.
- Journalisation des requêtes et des événements.
"""

# companion for Weda-Helper
# author : refhi
# allow Weda-Helper to communicate with the TPE and start the printing process
global version
# c'est la version demandée par l'extension Chrome pour vérifier la compatibilité
# pas très propre, mais permettra l'affichage d'un message d'erreur si la version de l'extension n'est pas compatible
version = '1.2'
global authorized_extensions
authorized_extensions = ['.doc', '.docx', '.pdf', '.ppt', '.pptx', '.xls', '.xslx', '.jpg', '.bmp', '.xlsx', '.txt', '.hpm', '.png', '.gif', '.jfif', '.tif', '.jpeg', '.rtf', '.csv', '.xml']

from flask import Flask, request, abort, jsonify, Response
from flask_cors import CORS
from PyQt5.QtCore import QSettings
from datetime import datetime # pour les logs
import os
import glob

import tempfile
import subprocess
import threading 
import time
import base64
from tpe import send_instruction, ProtocolTPE
try:
   from pynput.keyboard import Controller, Key
except ImportError:
   print("pynput can't be loaded, some features will not be available")

from send2trash import send2trash
isWindows = os.name == 'nt'
if isWindows:  # Si le système d'exploitation est Windows
    import win32gui
    import win32com.shell.shell as shell
    import win32com.shell.shellcon as shellcon
    from pynput.keyboard import Controller

def send_to_trash(file_path):
    try:
        # Vérifie si le fichier existe
        if not os.path.exists(file_path):
            raise Exception("File does not exist")

        # Prépare les paramètres pour SHFileOperation
        operation = shell.SHFileOperation(
            (
                0,
                shellcon.FO_DELETE,
                file_path,
                None,
                shellcon.FOF_ALLOWUNDO | shellcon.FOF_NOCONFIRMATION,
                None,
                None
            )
        )

        # Vérifie le résultat de l'opération
        if operation[1] != 0:
            raise Exception("Failed to send file to trash")
    except Exception as e:
        print(f"Error sending file to trash: {e}")


def recoverSumatraPath():
    if not isWindows:
      return None

    possible_paths = [
        os.path.join(os.getenv('LOCALAPPDATA'), 'SumatraPDF', 'SumatraPDF.exe'),
        os.path.join('C:\\', 'Program Files', 'SumatraPDF', 'SumatraPDF.exe')
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    print("SumatraPDF not found. Please install SumatraPDF to enable PDF printing.")
    return None

sumatraPath = recoverSumatraPath()

class Server(Flask):
    def __init__(self, name):
      super().__init__(name)
      self.uploaded_file_path = None
      self.settings = QSettings("weda", "companion")
      self.log = ""
      self.config["weda_handle"] = None

      CORS(self, origins=['chrome-extension://dbdodecalholckdneehnejnipbgalami','https://secure.weda.fr'])

      try:
         kbd = Controller()
      except NameError:
         kbd = None

      @self.before_request
      def limit_remote_addr():
         if request.path == '/':
            return
         if request.remote_addr != '127.0.0.1':
            abort(403)
         if 'apiKey' not in request.args:
            self.add_log('Clé API non fournie')
            abort(jsonify({
               'error': 'Erreur dans la requête de l\'extension, la clé API n\'est pas fournie.'
               }), 403)

         if not self.settings.value("apiKey") and 'apiKey' in request.args:
            self.add_log('Clé API vide, initialisation avec la clé fournie par l\'extension')
            self.settings.setValue("apiKey", request.args.get('apiKey'))

         if self.settings.value("apiKey") is not None and request.args.get('apiKey') != self.settings.value("apiKey"):
            self.add_log('Clé API non valide')
            abort(jsonify({
               'error': 'Clé API non conforme. Vérifiez que la clé API des options de l\'extension corresponde à la clé API des options du Companion'
               }), 403)
         if 'versioncheck' not in request.args or request.args.get('versioncheck') != version:
            version_demandee = request.args.get('versioncheck')
            # abort(403)
            self.add_log(f'version du Companion {version} incompatible avec la version demandée {version_demandee}. Veuillez mettre à jour Weda-Helper-Companion.')
            abort(jsonify({
                  'error': f'version du Companion {version} incompatible avec la version demandée {version_demandee}. Veuillez mettre à jour Weda-Helper-Companion en téléchargant la dernière version sur https://github.com/Refhi/Weda-Helper-Companion/releases/latest/download/companion.exe',
                }), 403)


      @self.route('/', methods=['GET'])
      def home():
         self.add_log('homepage requested')
         return (f"Bienvenue sur l'API de l'application Companion de Weda-Helper.\n Pour plus d'informations, rendez-vous sur https://github.com/Refhi/Weda-Helper \n version {version}")

      @self.route('/focus', methods=['GET'])
      def get_focus_back():
         if sumatraPath is not None:
            self.add_log('Sumatra détecté, récupération de focus non nécessaire')
            return

         if isWindows:  # Si le système d'exploitation est Windows
            current_window = win32gui.GetForegroundWindow()
            self.add_log(f'current window hook = {current_window}')
            if current_window != self.config["weda_handle"]: #Si la fenêtre actuelle est déjà Weda, on ne fait rien
               kbd.press(Key.alt)
               try:
                  win32gui.SetForegroundWindow(self.config["weda_handle"])
               except Exception as e:
                  kbd.release(Key.alt)
                  self.add_log(f"Erreur lors de la récupération du focus sur la fenêtre de Weda. {e}")
                  errormessage = f"Erreur lors de la récupération du focus sur la fenêtre de Weda. {e}"
                  print(errormessage)
                  return jsonify({'error': errormessage}), 500
               finally:
                  kbd.release(Key.alt)            
                  return jsonify({'info':f'focus vers {self.config["weda_handle"]}'}), 200
            else:
               self.add_log('focus déjà sur la fenêtre Weda')
        
         else:
            self.add_log('fonctionnalité non disponible sur ce système d\'exploitation')
            return jsonify({'error': 'fonctionnalité non disponible sur ce système d\'exploitation'}), 500

      @self.route('/print', methods=['POST'])
      def send_to_printer():
         if 'application/pdf' not in request.headers.get('Content-Type', ''):
            return jsonify({'error': 'Invalid Content-Type, expected application/pdf'}), 400

         pdf_data = request.data

         # Enregistrer le fichier PDF dans un fichier temporaire
         with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
            temp.write(pdf_data)
            temp_file_name = temp.name
            self.add_log(f'fichier temporaire créé: {temp_file_name}')
            print(f'temp file name: {temp_file_name}')

         # Imprimer le fichier
         if sumatraPath is not None:
            try:
               subprocess.run([sumatraPath, "-print-to-default", temp_file_name])
            except Exception as e:
               errormessage = "Erreur lors de l'impression du fichier PDF. Vérifiez que vous avez bien SumatraPDF installé."
               self.add_log(f"{errormessage} {e}")
               print(errormessage, e)
               return jsonify({'error': errormessage}), 500
         elif isWindows:
            try:
                  #pb de vol de focus, cf. https://stackoverflow.com/questions/6312627/windows-7-how-to-bring-a-window-to-the-front-no-matter-what-other-window-has-fo/6324105#6324105
                  self.config["weda_handle"] = win32gui.GetForegroundWindow()
                  print(f'weda_handle = {self.config["weda_handle"]}')
                  self.add_log(f'weda_handle = {self.config["weda_handle"]}')
                  os.startfile(temp_file_name, "print")
            except Exception as e:
                  errormessage = "Erreur lors de l'impression du fichier PDF. Vérifiez que vous avez bien un logiciel d'impression PDF par défaut (Recommandé = Acrobat Reader)."
                  self.add_log(f"{errormessage} {e}")
                  print(errormessage, e)
                  return jsonify({'error': errormessage}), 500
         else:  # Pour les autres systèmes d'exploitation (Linux, MacOS)
            subprocess.run(["lpr", temp_file_name])

         threading.Thread(target=remove_file_after_delay, args=(temp_file_name, 20)).start()
         return jsonify({'info':'Impression demandée pour le fichier PDF'}), 200

      @self.route('/tpe/<amount>', methods=['GET'])
      def send_to_tpe(amount):
         ip = self.settings.value('iptpe')
         port = self.settings.value('port_tpe')
         protocol = self.settings.value('protocol_tpe')
         self.add_log(f'TPE asked => {amount} cents @ {ip}:{port}')
         send_instruction(ip, port, amount, protocol)
         return jsonify({'info': f'TPE asked => {amount} cents @ {ip}:{port}'}), 200

      @self.route('/latestFile', methods=['GET'])
      def get_latest_file():
         if self.settings.value('upload_directory') is None:
            self.add_log('Le dossier d\'upload n\'est pas défini dans les options du Companion')
            return jsonify({'error':'Le dossier d\'upload n\'est pas défini dans les options du Companion'}), 500
         folder_path = self.settings.value('upload_directory')+'/*'
         list_files = glob.glob(folder_path)
         list_files.sort(reverse=True, key=os.path.getmtime)
         file_path = ""

         for file in list_files:
            firstpart, file_extension = os.path.splitext(file)
            filename = os.path.basename(file)
            if filename.startswith("~$") or filename.startswith("."): #On retire les fichiers temporaires
               continue
            if file_extension in authorized_extensions:
               file_path=file
               self.add_log(f'Fichier cible: {file_path}')
               break
         if file_path == "":
            self.add_log('Pas de fichier avec une extension autorisée dans le dossier d\'upload')
            return jsonify({'error':'Pas de fichier avec une extension autorisée dans le dossier d\'upload'}), 500

         file = open(file_path, "rb")
         fileContent = file.read()
         self.uploaded_file_path = os.path.normpath(file_path)
         return {'fileName': os.path.basename(file_path),'data':base64.b64encode(fileContent).decode('utf-8')},200
    
      @self.route('/archiveLastUpload', methods=['GET'])
      def archive_last_upload():
         print('Archivage du dernier fichier uploadé')
         # on déplace le dernier fichier uploadé dans un dossier archive, fils du dossier d'upload
         if self.settings.value('upload_directory') is None:
            self.add_log('Le dossier d\'upload n\'est pas défini dans les options du Companion')
            return jsonify({'error':'Le dossier d\'upload n\'est pas défini dans les options du Companion'}), 500

         if self.uploaded_file_path is None:
            self.add_log('Pas de fichier uploadé')
            return jsonify({'error':'Pas de fichier uploadé'}), 500

         archive_folder = self.settings.value('archive_directory')
         if archive_folder is None:
            archive_folder = self.settings.value('upload_directory') + '/archive'
            if not os.path.exists(archive_folder):
               self.add_log(f'Création du dossier d\'archive : {archive_folder}')
               os.makedirs(archive_folder)
         self.add_log(f'Archivage du fichier {os.path.basename(self.uploaded_file_path)}')
         try:
            # on contourne le problème de déplacement de fichier entre disques différents
            destination_path = os.path.join(archive_folder, os.path.basename(self.uploaded_file_path))
            # Copie le fichier
            with open(self.uploaded_file_path, 'rb') as src_file:
                  with open(destination_path, 'wb') as dest_file:
                     dest_file.write(src_file.read())
            # Supprime le fichier original
            os.remove(self.uploaded_file_path)
            self.add_log(f'Fichier archivé : {os.path.basename(self.uploaded_file_path)}')
            jsonify_info = jsonify({'info':f'Fichier archivé : {os.path.basename(self.uploaded_file_path)}'}), 200
            self.uploaded_file_path = None
            return jsonify_info
         except Exception as e:
            self.add_log(f'Erreur lors de l\'archivage du fichier : {e}')
            self.uploaded_file_path = None
            return jsonify({'error':f'Erreur lors de l\'archivage du fichier : {e}'}), 500

      @self.route('/trashLastUpload', methods=['GET'])
      def trash_last_upload():
         print('Mise à la corbeille du dernier fichier uploadé')

         if self.uploaded_file_path is None:
            self.add_log('Pas de fichier uploadé')
            return jsonify({'error':'Pas de fichier uploadé'}), 500

         self.add_log(f'Mise à la corbeille du fichier {os.path.basename(self.uploaded_file_path)}')
         try:
            if isWindows:
               send_to_trash(self.uploaded_file_path)
            else:
               send2trash(self.uploaded_file_path)
            self.add_log(f'Fichier mis à la corbeille : {os.path.basename(self.uploaded_file_path)}')
            jsonify_info = jsonify({'info':f'Fichier mis à la corbeille : {os.path.basename(self.uploaded_file_path)}'}), 200
            self.uploaded_file_path = None
            return jsonify_info
         except Exception as e:
            self.add_log(f'Erreur lors de la mise à la corbeille du fichier : {e}')
            self.uploaded_file_path = None
            return jsonify({'error':f'Erreur lors de la mise à la corbeille du fichier : {e}'}), 500

      @self.after_request
      def log_request(response):
         timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
         self.log += f"\n{timestamp} {request.method} {request.path} {response.status}"
         return response

      @self.route('/log', methods=['GET'])
      def get_log():
         return Response(self.log, mimetype='text/plain'), 200
      
      @self.errorhandler(404)
      def page_not_found(e):
         self.add_log(f'Fonction demandée non existante : 404. Pensez à mettre à jour le Companion. {e}')
         return jsonify({'error': 'Fonction demandée non gérée par le Companion : essayez de le mettre à jour.'}), 404
    
    def start(self):
      port=self.settings.value("port")
      if port is None:
            port = "4821" # Valeur par défaut
      self.run(host='localhost', port=port)

    def add_log(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.log += f"\n{timestamp} {message}"

def remove_file_after_delay(filename, delay):
    time.sleep(delay)
    try:
        os.remove(filename)
    except Exception as e:
        print(f"Erreur: Je n'ai pas pu supprimer le fichier temporaire (un programme est-il en train de l'utiliser ?) '{filename}': {e}")