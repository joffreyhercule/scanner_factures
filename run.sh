#!/bin/bash
set -e

# Créer le venv s'il n'existe pas
if [ ! -d ".venv" ]; then
    echo "Création du virtualenv..."
    python -m venv .venv
fi

# Activer le venv
source .venv/Scripts/activate

# Installer les dépendances
echo "Installation des dépendances..."
pip install -r requirements.txt --quiet

# Lancer le serveur
echo "Démarrage du serveur sur http://localhost:8000"
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
