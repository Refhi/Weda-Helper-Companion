# Weda-Helper-Companion

Companion local app of the extension Weda-Helper

Permet d'activer l'envoi d'instruction au TPE, l'impression complète après ctrl+P, ainsi que l'upload automatique des documents sur Weda avec archivage.

## Installation:
### Windows:
- télécharcher le fichier executable [Télécharger Weda Companion.exe](https://github.com/Refhi/Weda-Helper-Companion/releases/latest/download/Weda.Companion.exe) ou dans le dossier de votre choix, et le démarrer
- windows va probablement afficher un message de prudence concernant les risques d'execution d'un programme extérieur. Je vous rassure : le programme a été fait sans aucun virus/malware/etc. Mais n'hésitez pas à passer un coup d'antivirus pour vous rassurer avant d'autoriser l'exception (vous aurez peut-être besoin de cliquer sur "plus de renseignements" sous windows 11)
- suivre les instructions
- Le Companion se lance dans la barre système (en bas à droite dans Windows) avec l'icone W
- Ensuite :
-- soit vous installez SumatraPDF (recommandé) https://www.sumatrapdfreader.org/download-free-pdf-viewer (version 64bit Installer) => les impressions sont du coup lancées de façon invisible et plus rapide
-- soit vous installez et déclarez Foxit Reader, Adobe Reader ou équivalent comme logiciel par défaut pour l'impression des PDF (attention pose des problèmes de vol de focus avec Adobe Reader, et est un peu plus lent)
- Pour le lien avec le TPE, appelez votre fournisseur pour plus de précisions (cf. FAQ ci-dessous)

### Mac:
- télécharger le fichier .dmg [Télécharger Weda Companion.dmg](https://github.com/Refhi/Weda-Helper-Companion/releases/latest/download/Weda.Companion.dmg)
- copier l'application dans le dossier Applications
- **lors du premier lancement**: vous devez ouvrir l'application en faisant un clic droit sur l'application puis "Ouvrir". L'application n'étant pas signée, une fenêtre va vous demander de confirmer que vous souhaitez bien ouvrir l'application comme ci-dessous, cliquez alors sur "Ouvrir" à nouveau:
![](https://i.ibb.co/zFnXvfB/Capture-d-e-cran-2024-05-28-a-22-08-38-copie.jpg)

Pour les geek :
- vous pouvez directement récupérer le companion (gui.py) et l'executer
- vous pouvez également recompiler vous-même directement le Weda Companion.exe grace au fichier .spec et pyinstaller

## FAQ :
#### Comment activer la liaison avec le TPE ?
- sur le TPE le protocole caisse DOIT être activé, en TCP/IP s'il le propose
- le port de connexion dépend en général du matériel : 5000 pour veriphone, 8888 pour ingenico
- pour tester le lien, cliquez sur l'icone d'extension "W" dans chrome pour cliquer un bouton appelé "TPE Bis". (Weda-Helper >= 2.5).
- Si vous avez des difficultés, vous pouvez faire un ping vers l'IP du TPE. Si ça fonctionne en théorie c'est bon signe (dans une console taper ping [l'ip du TPE] puis entrée)
- normalement le firewall ne gène pas, mais en cas de difficultés vous pouvez TEMPORAIREMENT le desactiver pour tester.

#### Ca ne marche pas, comment je fais ?
- allez sur http://localhost:4821/ si ça affiche "Bienvenue sur l'API de l'application Companion de Weda-Helper." c'est que le Companion est bien lancé
- Sinon, re-essayez en changeant le numéro de port, par exemple 4822 (nécessite un redémarrage du Companion)
- Vous pouvez aussi aller sur http://localhost:4821/log?apiKey=[cléapi]&versioncheck=1.2 (en remplaçant les crochets et leur contenu par la clé API, et en changeant 4821 par le numéro de port utilisé par le Companion si besoin). Vous y trouverez la liste des requêtes "entendues" par le Companion.
- vous pouvez ouvrir un ticket d'incident sur https://github.com/Refhi/Weda-Helper-Companion/issues

#### Comment "compiler" moi-même le Companion ?
(nécessite d'avoir python installé et toutes les dépendances)
- Sous Windows : pyinstaller.exe '.\companionWin.spec' dans le powershell
- Sous Mac : pyinstaller '.\companionMac.spec' dans le terminal

#### Multi-utilisateurs geek :
- si vous utilisez chocolate (https://community.chocolatey.org/) vous pouvez installer SumatraPDF pour tout les utilisateurs via la commande `choco install sumatrapdf.install --ia '/d ""C:\Program Files\SumatraPDF""' `