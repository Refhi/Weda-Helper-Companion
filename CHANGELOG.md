# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

## [1.6] - 2025-03-01
- Ajout de la possibilité de choisir si le fichier importé via ctrl+U doit être supprimé ou archivé

## [1.5] - 2024-11-20
- ajout du support de sumatraPDF (qui devient recommandé sous windows)
- ajout du support de l'archivage post-upload (nécessite Weda Helper 2.8)

## [1.4.3] - 2024-06-26
- correction d'un bug qui causait un crash au premier lancement

## [1.4.2] - 2024-06-25
- correction d'un bug sur le chargement des options par défaut (nécessaitait un redémarrage, ce n'est plus le cas)

## [1.4.1] - 2024-06-23 - récupération automatique de la clé API
- la clé API est désormais récupérée automatiquement lors du contact avec Weda Helper, si elle est était restée vide.

## [1.4] - 2024-06-16 - merci https://github.com/Abeldvlpr !
- ajout du système d'upload vers Weda
- fix du getFocusBack (cassé dans la 1.3)
- vérification du focus avant de tenter de le récupérer pour rien (évite normalement de se retrouver avec alt appuyé pour rien dans chrome, ce qui sélectionne induement le menu "...")
- ajout d'un système de log, accessible via l'url : localhost:[port]/log?[cléapi]&versioncheck=[numversion]
- ajout d'un message d'erreur spécifique en cas d'appel d'une fonction non disponible.

## [1.3] - 2024-05-20 - Version majeure - merci https://github.com/Abeldvlpr !
- refactoring du code avec ajout d'une interface graphique pour les options 
- ajout d'un autostart sous windows
- ajout d'une icone en systray

## [1.2.1] - 2024-03-21
- correction d'une coquille au niveau de la configuration par défaut (numéro de port)

## [1.2] - 2024-01-14
- ajout d'une capacité de récupération du focus lorsque ce dernier est volé par l'application d'impression

## [1.1.1] - 2024-01-10
- changement du port par défaut vers 4821 (en théorie moins utilisé que le 3000)

## [1.1] - 2024-01-04
- ajout d'un permalien pour l'exe
- ajout de l'impression directe via POST plutôt que par pinput

## [1.0.1] - 2024-01-04
- ajout d'un contrôle de version

## [1.0] - 2024-01-02
- ajout de la nécessité d'une clé API

## [0.10] - 2024-01-01

### Modifié :
- retrait et modification des options correspondants pour l'usage de l'API
- fichier de conf désormais nommé conf.ini
- ajout de l'IP et du Port du TPE dans ce dernier