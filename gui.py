from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import threading
import os
from options import OptionsWindow
from server import *

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

        # Create the menu
        self.menu = QtWidgets.QMenu()
        # self.toggleServiceAction = QtWidgets.QAction("Démarrer le service")
        # self.toggleServiceAction.triggered.connect(self.toggleService)
        # self.menu.addAction(self.toggleServiceAction)

        self.informations = QtWidgets.QAction(f"Companion Weda Helper - {version}")
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

    def showOptions(self):
        self.MainWindow.show()
        self.MainWindow.raise_()
        self.MainWindow.activateWindow()
    # def toggleService(self):
    #     if self.toggleServiceAction.text() == "Démarrer le service":
    #         self.toggleServiceAction.setText("Arrêter le service")
    #     else:
    #         self.toggleServiceAction.setText("Démarrer le service")

if __name__ == "__main__":
    interface = QtWidgets.QApplication(sys.argv)
    interface.setQuitOnLastWindowClosed(False)
    
    window = OptionsWindow()
    menuItem = MenuItem()
    menuItem.setupMenu(window, interface)

    server=Server(__name__)
    serverThread = threading.Thread(target=server.start, daemon=True) # Démarrage du Flask en daemon pour qu'il s'éteigne lorsque l'application est quittée
    serverThread.start()

    sys.exit(interface.exec_())