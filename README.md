# Carbure
Traçabilité et durabilité des biocarburants, de la production à la distribution

## Prérequis
- docker
- docker-compose
- python3
- pipenv
- mysql
- mysql-client
- node

## Configuration et Installation

- Clonez le repository: git clone https://github.com/MTES-MCT/carbure.git
- Créez un fichier `.env` à la racine du dépôt en vous basant sur le fichier `.env.example` disponible dans le dossier

Ensuite, créez un environnement virtuel pour python 3.10:

- `pipenv install`

Je recommande de créer un alias pour charger l'environnement de développement.
par exemple :

- `alias carbure='cd /path/du/repository; pipenv shell;'`

Dans le dossier /front, téléchargez les modules
- `npm install`

Vous pouvez désormais builder les images docker et lancer le projet:

- `docker-compose build`
- `docker-compose up -d`


## Alimenter la base de données de dev

Lancer `sh scripts/database/restore_db.sh` pour télécharger un dump contenant des données utilisables en local

## Création d'un nom de domaine local personnalisé

- Aller dans le fichier `/etc/hosts` (sur linux et mac)
- Ajouter la ligne `127.0.0.1 carbure.local`
- Vous pouvez maintenant accéder à votre version locale de carbure à l'adresse http://carbure.local:8090/


# Authentification à Carbure

- Pour ajouter un nouveau super utilisateur à la db locale, taper `docker exec -it carbure_app python3 web/manage.py createsuperuser`
- Ensuite aller sur http://carbure.local:8090/auth/login
- Utiliser les informations renseignées à l'étape 1 puis valider l'authentification
- Carbure demande d'entrer un code envoyé par email
- Dans la version de dev ce code sera uniquement affiché dans les logs de django, visibles en tapant `docker logs carbure_app`


## Étapes spécifiques pour windows
- setup wsl2: https://docs.microsoft.com/en-us/windows/wsl/install-win10
- installer docker desktop avec les libs WSL extra
- installer ubuntu 20.04: https://www.microsoft.com/fr-fr/p/ubuntu-2004-lts/9n6svws3rx71?activetab=pivot:overviewtab
- installer windows terminal: https://www.microsoft.com/fr-fr/p/windows-terminal/9n0dx20hk701?rtc=1&activetab=pivot:overviewtab
- activer ubuntu dans les options de docker desktop (resources > wsl)
- ouvrir ubuntu dans le windows terminal puis taper:
- `sudo apt-get update`
- `sudo apt-get install python3 python3-dev python3-pip default-libmysqlclient-dev build-essential`
- `pip install --user pipenv`

Ensuite, setup normalement le projet:
- ajouter les clé ssh https://docs.gitlab.com/ee/ssh/#generate-an-ssh-key-pair
- dans le terminal ubuntu, taper:
- `git clone git@gitlab.com:la-fabrique-numerique/biocarburants.git carbure`
- `cd carbure`
- `pipenv install`
- `(cd front; npm install)`
- `docker-compose up --build -d`
- `code .`