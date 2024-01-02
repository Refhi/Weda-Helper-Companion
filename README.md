# Weda-Helper-Companion

Companion local app of the extension Weda-Helper

Permet d'activer l'envoi d'instruction au TPE, ainsi que l'impression complète après ctrl+P

Instructions d'installation manuelles :
- télécharger l'ensemble des fichiers dans le dossier de votre choix
- éditer avec un éditeur de texte le fichier conf.ini pour y modifier si besoin le port d'écoute du companion. Il est également possible de préciser l'adresse IP du TPE et le port du TPE (appeler votre fournisseur de TPE pour le paramétrer et obtenir ces informations).
- installer les dépendances :
- - python3
- - les packets flask, flask-cors et pynput
- il est possible de mettre un raccourcis dans le dossier démarrage du menu démarrer (win+R et taper shell:startup pour y accéder facilement) ou de démarre manuellement le companion à chaque fois

Via windows store :
- aller sur le windows store et rechercher weda-helper-companion
- après installation, aller dans le dossier d'installation et y éditer le fichier conf.ini