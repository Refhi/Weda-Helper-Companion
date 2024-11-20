"""
Imprime un PDF directement avec Ghostscript via l'API Python.

:param pdf_path: Chemin vers le fichier PDF
:param printer_name: Nom de l'imprimante
"""

import ghostscript
import sys

def print_pdf_with_ghostscript(pdf_path):
    args = [
        "ghostscript",  # Nom de l'interpréteur Ghostscript
        "-dNOPAUSE",  # Pas de pause entre les pages
        "-dBATCH",  # Quitter automatiquement après le traitement
        "-dSAFER",  # Limite les permissions pour la sécurité
        "-sDEVICE=mswinpr2",  # Pilote d'impression pour Windows
        "-sOutputFile=%printer%",  # Utiliser l'imprimante par défaut
        pdf_path  # Fichier PDF à imprimer
    ]

    try:
        # Appel à Ghostscript via l'API Python
        ghostscript.Ghostscript(*args)
        print(f"Le fichier {pdf_path} a été imprimé sur l'imprimante par défaut.")
    except Exception as e:
        print(f"Erreur lors de l'impression : {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python ghostPrinter.py <pdf_path>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    print_pdf_with_ghostscript(pdf_path)