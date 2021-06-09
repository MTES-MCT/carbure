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

Je recommande de créer un alias pour charger l'environnement de développement.
par exemple:
- alias carbure='cd /path/du/repository; source loadenv.sh;'

Vous pouvez désormais builder les images docker et lancer le projet:

- docker-compose build
- docker-compose up -d

Le script loadenv.sh permet d'interagir avec les containers.


## Étapes spécifiques pour windows
- setup wsl2: https://docs.microsoft.com/en-us/windows/wsl/install-win10
- installer docker desktop avec les libs WSL extra
- installer ubuntu 20.04: https://www.microsoft.com/fr-fr/p/ubuntu-2004-lts/9n6svws3rx71?activetab=pivot:overviewtab
- installer windows terminal: https://www.microsoft.com/fr-fr/p/windows-terminal/9n0dx20hk701?rtc=1&activetab=pivot:overviewtab
- activer ubuntu dans les options de docker desktop (resources > wsl)
- ouvrir ubuntu dans le windows terminal puis taper:
- `sudo apt-get update`
- `sudo apt-get install python3 python3-dev python3-virtualenv default-libmysqlclient-dev build-essential`

Ensuite, setup normalement le projet:
- ajouter les clé ssh https://docs.gitlab.com/ee/ssh/#generate-an-ssh-key-pair
- dans le terminal ubuntu, taper:
- `git clone git@gitlab.com:la-fabrique-numerique/biocarburants.git carbure`
- `cd carbure`
- `virtualenv -p python3 venv`
- `source venv/bin/activate`
- `pip install -r requirements.txt`
- `docker-compose up --build -d`
- `bash loadenv.sh`
- `code .`