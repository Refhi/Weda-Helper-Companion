import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QFormLayout, QMessageBox
from PyQt5.QtCore import QSettings
import re

class OptionsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Options")
        
        # Create text input fields
        self.apiKey_input = QLineEdit()
        self.port_input = QLineEdit()
        self.iptpe_input = QLineEdit()
        self.port_tpe_input = QLineEdit()
        
        # Create save button
        self.save_button = QPushButton("Enregistrer")
        self.save_button.clicked.connect(self.save_options)
        
        # Set up layout
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        form_layout.addRow("API Key:", self.apiKey_input)
        form_layout.addRow("Port:", self.port_input)
        form_layout.addRow("IP TPE:", self.iptpe_input)
        form_layout.addRow("Port TPE:", self.port_tpe_input)
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

    def closeEvent(self, event):
        event.ignore() # On ignore la fermeture de la fenetre pour forcer à passer par le bouton Enregistrer et effectuer la vérification des options

    def save_options(self):
        # Get values from input fields
        apiKey = self.apiKey_input.text()
        port = self.port_input.text()
        iptpe = self.iptpe_input.text()
        port_tpe = self.port_tpe_input.text()
        
        # Validate input
        if  not apiKey:
            self.show_error("La clé API est vide")
            return
        if  not port.isdigit() or not (1 <= int(port) <= 65535):
            self.show_error("Le port n'est pas valide")
            return
        if  not port_tpe.isdigit() or not (1 <= int(port_tpe) <= 65535):
            self.show_error("Le port TPE n'est pas valide")
            return
        if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", iptpe):
            self.show_error("L'adresse IP du TPE n'est pas valide.")
            return
        

        # Save options to settings
        settings = QSettings("weda", "companion")
        settings.setValue("apiKey", apiKey)
        settings.setValue("port", port)
        settings.setValue("iptpe", iptpe)
        settings.setValue("port_tpe", port_tpe)
        
        print("Options saved!")
        self.restart_information()
    
    def load_options(self):
        # Load options from settings
        settings = QSettings("weda", "companion")
        apiKey = settings.value("apiKey")
        port = settings.value("port")
        iptpe = settings.value("iptpe")
        port_tpe = settings.value("port_tpe")

        if port is None:
            port = "4821" # Valeur par défaut
        if port_tpe is None:
            port_tpe = "5000"
        if iptpe is None:
            iptpe = "192.168.1.35"
        
        # Set values in input fields
        self.apiKey_input.setText(apiKey)
        self.port_input.setText(port)
        self.iptpe_input.setText(iptpe)
        self.port_tpe_input.setText(port_tpe)

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
        #os.execl(sys.executable, sys.executable, *sys.argv) #Redémarre l'application. Fonctionne mais redémarre trop vite et le port est toujours utilisé lors du nouveau lancement
        sys.exit()
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OptionsWindow()
    window.show()
    sys.exit(app.exec_())
