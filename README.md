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
- scalingo `curl -O https://cli-dl.scalingo.com/install && bash install`

## Configuration et Installation

- Clonez le repository: git clone https://github.com/MTES-MCT/carbure.git
- Créez un fichier `.env` à la racine du dépôt en vous basant sur le fichier `.env.example` disponible dans le dossier (Tu peux retrouver la pluspart des valeurs dans la section "Environnement" de carbure-prod sur scalingo https://dashboard.scalingo.com/apps/osc-fr1/carbure-prod/environment)
- créer un accès ssh à ton compte Scalingo (https://dashboard.scalingo.com/account/keys) et un API token (dans ton profile scalingo https://dashboard.scalingo.com/account/tokens)
- remplir SCALINGO_TOKEN=le token que tu as créé dans tom compte

Installation de pipenv :
- ajouter `export PIPENV_VENV_IN_PROJECT=1` au ~/.bashrc (ou ~/zshrc, etc...)

Ensuite, créez un environnement virtuel pour python 3.10:

- `pipenv install`

Je recommande de créer un alias pour charger l'environnement de développement.
par exemple :

- `alias carbure='cd /path/du/repository; pipenv shell;'`
- lancer l'alias ou `pipenv shell`

Dans le dossier /front, téléchargez les modules
 `npm install`

Vous pouvez désormais builder les images docker et lancer le projet:
 `docker-compose build`
 `docker-compose up -d`

## Alimenter la base de données de dev

- se connecter à scalingo `scalingo login --api-token $SCALINGO_TOKEN`
- Lancer `sh scripts/database/restore_db.sh` pour télécharger un dump contenant des données utilisables en local


## Création d'un nom de domaine local personnalisé

- Aller dans le fichier `/etc/hosts` (sur linux et mac)
- Ajouter la ligne `127.0.0.1 carbure.local`
- Vous pouvez maintenant accéder à votre version locale de carbure à l'adresse http://carbure.local:8090/

## Configurer l'accès à la base de donnée depuis le terminal

- Dans le fichier `.env`, éditer les variables `DATABASE_URL` et `REDIS_URL` et y mettre une valeur qui pointe vers les containers MySQL et Redis
- `DATABASE_URL=mysql://{root_user}:{root_password}@0.0.0.0:3306/carbure-db`
- `REDIS_URL=redis://0.0.0.0:6379`
- Une fois le container MySQL lancé, dans le `pipenv shell`, exécuter `python web/manage.py dbshell`
- S'il n'y a pas d'erreur, c'est ok
- Si cette étape ne marche pas du tout, on peut passer par le container Django pour exécuter `manage.py`
- `docker exec -it carbure_app python3 web/manage.py dbshell` fonctionne à tous les coups

# Authentification à Carbure

- Pour ajouter un nouveau super utilisateur à la db locale, taper `python3 web/manage.py createsuperuser`
- Ensuite aller sur http://carbure.local:8090/auth/login
- Utiliser les informations renseignées à l'étape 1 puis valider l'authentification
- Carbure demande d'entrer un code envoyé par email
- Dans la version de dev ce code sera uniquement affiché dans les logs de django, visibles en tapant `docker logs carbure_app`Run all the tests

# Effectuer une migration
Lorsque des changement sont effectué sur la base de donnée :
1 une fois les model ou champs ajouté, pour créer le fichier de migration - `python web/manage.py makemigrations`
2 pour appliquer la migration sur la DB - `python web/manage.py migrate`

# Lancer les tests backend
- Run all the tests in the api.v5.saf module
`python web/manage.py test api.v5.saf`
- Run just one test
`python web/manage.py test api.v5.saf.airline.tests.tests_ticket_details.SafTicketDetailsTest`
- Pour éviter de reconstruire la db de test à chaque fois, on peut ajouter l'option `--keepdb` à la fin de la commande

# Utiliser la console scalingo
`scalingo -a carbure-{prod|dev|staging} run bash`
`python web/manage.py shell`

example :
```
>>> from core.models import Entity
>>> entities = Entity.objects.filter(registered_address__isnull=False)
>>> entities.count()
```

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