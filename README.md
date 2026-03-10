# Scanner Factures Garage

Application locale de scan de factures pour un garage automobile. Chargez vos factures PDF, l'IA extrait automatiquement les données (client, vehicule, montants) et les classe dans une base de donnees.

## Prerequis

- **Python 3.11+** : [python.org](https://www.python.org/downloads/)
- **Ollama** : [ollama.com](https://ollama.com/download)
- **Modele Qwen 3.5** : telecharger via Ollama

## Installation

### 1. Installer Ollama

Telecharger et installer Ollama depuis [ollama.com](https://ollama.com/download).

### 2. Telecharger le modele Qwen 3.5

```bash
ollama pull qwen3.5
```

Verifier que le modele fonctionne :

```bash
ollama run qwen3.5 "Bonjour"
```

### 3. Lancer l'application

```bash
bash run.sh
```

Le script `run.sh` :
- Cree un virtualenv Python (`.venv`) s'il n'existe pas
- Installe les dependances (`requirements.txt`)
- Demarre le serveur sur `http://localhost:8000`

### Installation manuelle (sans run.sh)

```bash
python -m venv .venv
source .venv/Scripts/activate   # Windows (Git Bash)
# source .venv/bin/activate     # Linux/Mac
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Utilisation

1. Ouvrir `http://localhost:8000` dans le navigateur
2. Glisser-deposer un ou plusieurs fichiers PDF de factures
3. Cliquer sur "Traiter les factures"
4. Consulter les onglets Factures, Clients, Vehicules

## Stack technique

- **Backend** : FastAPI + Uvicorn
- **Base de donnees** : TinyDB (fichier JSON)
- **IA** : Ollama + Qwen 3.5 (lecture native PDF)
- **Frontend** : HTML/JS vanilla + Pico CSS

## Structure du projet

```
app/
  main.py          # Point d'entree FastAPI
  config.py        # Configuration (Ollama, chemins)
  models.py        # Modeles Pydantic
  database.py      # Init TinyDB
  routers/         # Routes API (clients, vehicules, factures, upload)
  services/        # Logique metier (ai_parser, invoice_processor)
  repositories/    # CRUD TinyDB
frontend/
  index.html       # Interface web
  app.js           # Logique frontend
  style.css        # Styles
data/              # Base TinyDB (cree au runtime)
uploads/           # Stockage temporaire PDF
```
