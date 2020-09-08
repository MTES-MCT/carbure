# Carbure
Traçabilité et durabilité des biocarburants, de la production à la distribution

## Prérequis
- docker
- docker-compose
- python3
- virtualenv

## Configuration et Installation

- Clonez le repository: git clone https://github.com/MTES-MCT/carbure.git
- Créez un fichier `.env` à la racine du dépôt en vous basant sur le fichier `.env.example` disponible dans le dossier


Ensuite, créez un environnement virtuel pour python3:

- virtualenv -p python3 venv
- source venv/bin/activate
- pip install -r requirements.txt

Vous pouvez désormais builder les images docker et lancer le projet:

- docker-compose build
- docker-compose up -d


