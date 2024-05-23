
# companion for Weda-Helper
# author : refhi
# allow Weda-Helper to communicate with the TPE and start the printing process
global version
version = '1.2'
global authorized_extensions
authorized_extensions = ['.doc', '.docx', '.pdf', '.ppt', '.pptx', '.xls', '.xslx', '.jpg', '.bmp', '.xlsx', '.txt', '.hpm', '.png', '.gif', '.jfif', '.tif', '.jpeg', '.rtf', '.csv', '.xml']

from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from PyQt5.QtCore import QSettings
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

if os.name == 'nt':  # Si le système d'exploitation est Windows
    import win32gui 
    from pynput.keyboard import Controller

class Server(Flask):
    def __init__(self, name):
      super().__init__(name)

      self.settings = QSettings("weda", "companion")

      CORS(self, origins=['chrome-extension://dbdodecalholckdneehnejnipbgalami','https://secure.weda.fr'])

      try:
         keyboard = Controller()
      except NameError:
         keyboard = None

      @self.before_request
      def limit_remote_addr():
         if request.remote_addr != '127.0.0.1':
            abort(403)
         if 'apiKey' not in request.args or request.args.get('apiKey') != self.settings.value("apiKey"):
            abort(jsonify({
               'error': f'Clé API non fournie ou non conforme. Elle doit être notée dans le fichier conf.ini et dans les options de l\'extension Chrome',
               }), 403)    
         if 'versioncheck' not in request.args or request.args.get('versioncheck') != version:
            version_demandee = request.args.get('versioncheck')
            # abort(403)
            abort(jsonify({
                  'error': f'version du Companion {version} incompatible avec la version demandée {version_demandee}. Veuillez mettre à jour Weda-Helper-Companion en téléchargant la dernière version sur https://github.com/Refhi/Weda-Helper-Companion/releases/latest/download/companion.exe',
                }), 403)


      @self.route('/', methods=['GET'])
      def home():
         return (f"Bienvenue sur l'API de l'application Companion de Weda-Helper.\n Pour plus d'informations, rendez-vous sur https://github.com/Refhi/Weda-Helper \n version {version}")

      @self.route('/focus', methods=['GET'])
      def get_focus_back():
         if os.name == 'nt':  # Si le système d'exploitation est Windows

            kbd.press(Key.alt)
            try:
               win32gui.SetForegroundWindow(self.config["weda_handle"])
            except Exception as e:

               kbd.release(Key.alt)
               errormessage = f"Erreur lors de la récupération du focus sur la fenêtre de Weda. {e}"
               print(errormessage)
               return jsonify({'error': errormessage}), 500
            finally:
               kbd.release(Key.alt)            
               return jsonify({'info':f'focus vers {self.config["weda_handle"]}'}), 200
        
         else:
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
            print(f'temp file name: {temp_file_name}')

         # Imprimer le fichier
         if os.name == 'nt':  # Si le système d'exploitation est Windows
            try:
                  #pb de vol de focus, cf. https://stackoverflow.com/questions/6312627/windows-7-how-to-bring-a-window-to-the-front-no-matter-what-other-window-has-fo/6324105#6324105
                  self.config["weda_handle"] = win32gui.GetForegroundWindow()
                  print(f'weda_handle = {self.config["weda_handle"]}')
                  os.startfile(temp_file_name, "print")
            except Exception as e:
                  errormessage = "Erreur lors de l'impression du fichier PDF. Vérifiez que vous avez bien un logiciel d'impression PDF par défaut (Recommandé = Acrobat Reader)."
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
         send_instruction(ip, port, amount, protocol)
         return jsonify({'info': f'TPE asked => {amount} cents @ {ip}:{port}'}), 200

      @self.route('/latestFile', methods=['GET'])
      def get_latest_file():
         if self.settings.value('upload_directory') is None:
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
               break
         if file_path == "":
            return jsonify({'error':'Pas de fichier avec une extension autorisée dans le dossier d\'upload'}), 500

         file = open(file_path, "rb")
         fileContent = file.read();
         return {'fileName': os.path.basename(file_path),'data':base64.b64encode(fileContent).decode('utf-8')},200;
    
    def start(self):
      port=self.settings.value("port")
      if port is None:
            port = "4821" # Valeur par défaut
      self.run(host='localhost', port=port)

def remove_file_after_delay(filename, delay):
    time.sleep(delay)
    try:
        os.remove(filename)
    except Exception as e:
        print(f"Erreur: Je n'ai pas pu supprimer le fichier temporaire (un programme est-il en train de l'utiliser ?) '{filename}': {e}")