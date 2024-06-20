import sys
import os
from PyQt5.QtWidgets import QCheckBox, QApplication, QWidget, QLabel, QLineEdit, QComboBox, QPushButton, QVBoxLayout, QGridLayout, QMessageBox, QFileDialog
from PyQt5.QtCore import QSettings, Qt
import re
from tpe import ProtocolTPE

RUN_PATH = "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"

class OptionsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Options")
        
        # Create text input fields
        self.apiKey_input = QLineEdit()
        self.port_input = QLineEdit()
        self.iptpe_input = QLineEdit()
        self.port_tpe_input = QLineEdit()
        self.protocol_tpe_input = QComboBox()
        self.protocol_tpe_input.addItems(["Défaut", "Concert V3"]) #Nommer correctement le protocole "Défaut"
        self.choose_upload_directory = QPushButton("Sélectionner un dossier")
        self.choose_upload_directory.clicked.connect(self.show_folder_dialog)
        self.upload_directory_label = QLabel()
        self.upload_directory_label.setAlignment(Qt.AlignCenter)
        self.start_at_boot_checkbox = QCheckBox("Démarrage automatique au lancement de Windows")
        
        # Create save button
        self.save_button = QPushButton("Enregistrer")
        self.save_button.clicked.connect(self.save_options)
        
        # Set up layout
        layout = QVBoxLayout()
        form_layout = QGridLayout()
        form_layout.addWidget(QLabel("Clé API:"), 0,0, alignment=Qt.AlignmentFlag.AlignRight)
        form_layout.addWidget(self.apiKey_input, 0,1)

        form_layout.addWidget(QLabel('<i>Doit correspondre à la clé API des options de l\'extension, laisser vide pour qu\'elle soit automatiquement récupérée</i>'), 1,0,1,2, Qt.AlignmentFlag.AlignCenter)
        # url_label = QLabel("chrome-extension://dbdodecalholckdneehnejnipbgalami/options.html")
        # url_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        # form_layout.addWidget(url_label, 2,0,1,2, Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(QLabel(), 3,0)
        form_layout.addWidget(QLabel("Port:"), 4,0, alignment=Qt.AlignmentFlag.AlignRight)
        form_layout.addWidget(self.port_input, 4,1)
        form_layout.addWidget(QLabel('<i>A récupérer dans les options de l\'extension \n 4821 par défaut</i>'), 5,0,1,2, Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(QLabel(), 6,0)
        form_layout.addWidget(QLabel("IP TPE:"), 7,0, alignment=Qt.AlignmentFlag.AlignRight)
        form_layout.addWidget(self.iptpe_input, 7,1)
        form_layout.addWidget(QLabel("Port TPE:"), 8,0, alignment=Qt.AlignmentFlag.AlignRight)
        form_layout.addWidget(self.port_tpe_input, 8,1)
        form_layout.addWidget(QLabel('<i>A récupérer auprès de votre installateur de TPE <br>(en général 5000 pour verifone et 8888 pour ingenico)</i>'), 9,0,1,2, Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(QLabel(), 10,0)
        form_layout.addWidget(QLabel("Protocole TPE:"), 11,0, alignment=Qt.AlignmentFlag.AlignRight)
        form_layout.addWidget(self.protocol_tpe_input, 11,1)
        # pour windows
        if os.name == 'nt':
            form_layout.addWidget(QLabel("Autostart:"), 12,0, alignment=Qt.AlignmentFlag.AlignRight)
            form_layout.addWidget(self.start_at_boot_checkbox, 12,1)
            
        #Dossier d'upload
        form_layout.addWidget(QLabel(), 13,0)
        form_layout.addWidget(QLabel("Dossier d'upload:"), 14,0, alignment=Qt.AlignmentFlag.AlignRight)
        form_layout.addWidget(self.choose_upload_directory, 14,1)

        form_layout.addWidget(self.upload_directory_label, 15,0,1,2, Qt.AlignmentFlag.AlignCenter)
        upload_information_label = QLabel('<i>Dossier dont le dernier fichier sera uploadé lors de l\'utilisation du raccourci dans l\'extension</i>')
        upload_information_label.setAlignment(Qt.AlignCenter)
        upload_information_label.setWordWrap(True)
        form_layout.addWidget(upload_information_label, 16,0,1,2)

        layout.addLayout(form_layout)
        layout.addWidget(self.save_button)
        self.setLayout(layout)
        
        # Load saved options
        self.load_options()

        settings = QSettings("weda", "companion")
        if settings.value("alreadyLaunched") == None:
            print("First launch")
            self.show()
            self.first_launch_information()
            settings.setValue("alreadyLaunched", True)

    def showEvent(self, event):
        super().showEvent(event)
        self.load_options() # Mets à jours les options avant d'afficher la fenêtre
        
    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message',
                                    "Voulez-vous enregistrer les modifications ?", QMessageBox.Yes | 
                                    QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.save_options()
        else:
            self.load_options()
            event.accept()
    
    def show_folder_dialog(self):
        folder_dialog = QFileDialog(self)
        folder_dialog.setWindowTitle('Sélectionner un dossier')
        folder_dialog.setFileMode(QFileDialog.Directory)
        folder_dialog.setOption(QFileDialog.ShowDirsOnly, True)
        folder_dialog.setOption(QFileDialog.ReadOnly, False)
        if folder_dialog.exec_() == QFileDialog.Accepted:
            selected_folder = folder_dialog.selectedFiles()[0]
            self.upload_directory_label.setText(selected_folder)

    
    
    def save_options(self):
        # Get values from input fields
        apiKey = self.apiKey_input.text()
        port = self.port_input.text()
        iptpe = self.iptpe_input.text()
        port_tpe = self.port_tpe_input.text()
        protocol_tpe = self.protocol_tpe_input.currentIndex()
        start_at_boot = self.start_at_boot_checkbox.isChecked()
        upload_directory = self.upload_directory_label.text()

        if  not port.isdigit() or not (1 <= int(port) <= 65535):
            self.show_error("Le port n'est pas valide")
            return
        if  not port_tpe.isdigit() or not (1 <= int(port_tpe) <= 65535):
            self.show_error("Le port TPE n'est pas valide")
            return
        if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", iptpe):
            self.show_error("L'adresse IP du TPE n'est pas valide.")
            return
        if not upload_directory or upload_directory == "Non défini":
            upload_directory = None
        

        # Save options to settings
        settings = QSettings("weda", "companion")
        settings.setValue("apiKey", apiKey)
        settings.setValue("port", port)
        settings.setValue("iptpe", iptpe)
        settings.setValue("port_tpe", port_tpe)
        settings.setValue('protocol_tpe', protocol_tpe)
        settings.setValue('upload_directory', upload_directory)

        if os.name == 'nt':
            register_settings = QSettings(RUN_PATH, QSettings.NativeFormat)
            if self.start_at_boot_checkbox.isChecked(): # Save startup information to register on Windows
                register_settings.setValue("WedaCompanionHelper",sys.argv[0]);
            else:
                register_settings.remove("WedaCompanionHelper");
            
        
        print("Options saved!")
        self.restart_information()
    
    def load_options(self):
        # Load options from settings
        settings = QSettings("weda", "companion")
        apiKey = settings.value("apiKey")
        port = settings.value("port")
        iptpe = settings.value("iptpe")
        port_tpe = settings.value("port_tpe")
        protocol_tpe = settings.value("protocol_tpe")
        upload_directory = settings.value("upload_directory")

        if port is None:
            port = "4821" # Valeur par défaut
        if port_tpe is None:
            port_tpe = "5000"
        if iptpe is None:
            iptpe = "192.168.1.35"
        if protocol_tpe is None:
            protocol_tpe = ProtocolTPE.DEFAUT
        if upload_directory is None:
            upload_directory = "Non défini"
        
        # Set values in input fields
        self.apiKey_input.setText(apiKey)
        self.port_input.setText(port)
        self.iptpe_input.setText(iptpe)
        self.port_tpe_input.setText(port_tpe)
        self.protocol_tpe_input.setCurrentIndex(int(protocol_tpe))
        self.upload_directory_label.setText(upload_directory)

        if os.name == 'nt':
            register_settings = QSettings(RUN_PATH, QSettings.NativeFormat)
            self.start_at_boot_checkbox.setChecked(register_settings.contains("WedaCompanionHelper"))# Load startup from register on Windows


    def show_error(self, error):

        # Crée une boîte de dialogue d'erreur
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setText("Erreur")
        msg_box.setInformativeText(error)
        msg_box.setWindowTitle("Erreur")
        msg_box.exec_()

    def restart_information(self):

        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setText("Information")
        msg_box.setInformativeText("Vos options ont étés sauvegardées, l'application va quitter pour prendre en compte vos nouvelles options, vous pouvez la relancer par la suite")
        msg_box.setWindowTitle("Information")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.buttonClicked.connect(self.quit)
        msg_box.exec_()

    def first_launch_information(self):

        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setText("Information")
        msg_box.setInformativeText("Bienvenue dans le Comanion Weda Helper. Afin de fonctionner correctement, vous devez saisir une la clé API qui se trouve dans les options de l'extension")
        msg_box.setWindowTitle("Information")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def quit(self):
        # os.execl(sys.executable, sys.executable, *sys.argv) #Redémarre l'application. Fonctionne mais redémarre trop vite et le port est toujours utilisé lors du nouveau lancement
        sys.exit()
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OptionsWindow()
    window.show()
    sys.exit(app.exec_())
