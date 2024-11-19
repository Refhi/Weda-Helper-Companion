"""
gui.py

Ce fichier configure et affiche l'interface graphique pour l'application Weda-Helper-Companion.
Il crée une icône dans la barre système avec un menu contextuel permettant d'accéder aux options de l'application et de quitter l'application.

Classes:
    MenuItem - Configure le menu de la barre système et gère les interactions de base avec l'utilisateur.

Fonctionnalités:
    - Affichage d'une icône dans la barre système.
    - Menu contextuel avec des options pour afficher les options de l'application et quitter l'application.
    - Gestion des clics sur l'icône de la barre système pour afficher la fenêtre des options.
"""

from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import threading
import os
from options import OptionsWindow
from server import *
global true_version
true_version = '1.4.4'

class MenuItem(object):
    def setupMenu(self, MainWindow, interface):
        try:
            # Path pour accéder aux ressources lorsqu'elles sont bundlé par PyInstaller https://stackoverflow.com/questions/7674790/bundling-data-files-with-pyinstaller-onefile
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".") # Path lorsque l'on n'est pas bundlé et en cours de dev
        file_path = os.path.join(base_path, 'icon.png')

        icon = QtGui.QIcon(file_path)

        self.MainWindow = MainWindow

        self.tray = QtWidgets.QSystemTrayIcon()
        self.tray.setIcon(icon)
        self.tray.setVisible(True)
        self.tray.setToolTip(f"Companion Weda Helper - {true_version}")

        # On facilite l'accès aux options, grace à un simple clic gauche
        self.tray.activated.connect(self.showOptions)


        # Create the menu
        self.menu = QtWidgets.QMenu()

        self.informations = QtWidgets.QAction(f"Companion Weda Helper - {true_version}")
        self.informations.setEnabled(False)
        self.menu.addAction(self.informations)

        self.optionsAction = QtWidgets.QAction("Afficher les options")
        self.optionsAction.triggered.connect(self.showOptions)
        self.menu.addAction(self.optionsAction)

        # Add a Quit option to the menu.
        self.quit = QtWidgets.QAction("Quitter")
        self.quit.triggered.connect(interface.quit)
        self.menu.addAction(self.quit)

        # Add the menu to the tray
        self.tray.setContextMenu(self.menu)

    def showOptions(self, reason):
        # ici on vérifie que l'appel de showOptions est bien fait par un clic gauche ou par un clic sur le
        # "option" présent dans le menu contextuel (grace à "or not reason")
        if reason == QtWidgets.QSystemTrayIcon.Trigger or not reason:
            self.MainWindow.show()
            self.MainWindow.raise_()
            self.MainWindow.activateWindow()

if __name__ == "__main__":
    interface = QtWidgets.QApplication(sys.argv)
    interface.setQuitOnLastWindowClosed(False)
    
    window = OptionsWindow()
    menuItem = MenuItem()
    menuItem.setupMenu(window, interface)

    print("""Bienvenue sur le Companion de Weda-Helper,
Utilisez le W dans la barre d'application pour accéder aux options""")
    server=Server(__name__)
    serverThread = threading.Thread(target=server.start, daemon=True) # Démarrage du Flask en daemon pour qu'il s'éteigne lorsque l'application est quittée
    serverThread.start()

    sys.exit(interface.exec_())