# Carbure

Traçabilité et durabilité des biocarburants, de la production à la distribution

## Prérequis

- docker
- docker-compose
- python3
- pipenv
- mysql@8.0 => voir les précisions d'installation ci-dessous
- node
- scalingo `curl -O https://cli-dl.scalingo.com/install && bash install`

## Installation de mysql@8.0

Attention, uniquement la version 8.0 de MYSQL fonctionne sur notre configuration

- supprimez toute autres versions `brew uninstall mysql`.
- reinstallez la bonne version `brew install mysql@8.0`.
- mysql risque de s'installer avec dans le dossier /opt/homebrew/opt/mysql@8.0 au lieu de /opt/homebrew/opt/mysql.
Depuis le dossier d'installation `/opt/homebrew/opt` créez un lien symbolique :
 `ln -s mysql@8.0 mysql`

- Ajouter le binaire au PATH
`export PATH="/opt/homebrew/opt/mysql/bin:$PATH"`

- /!\ Ne pas start mysql sur la machine (ou alors changer les ports si besoin)
Si vous rencontrez cette erreur lors de l'importation de la bdd `NameError: name '_mysql' is not defined` ou
`mysql: [Warning] Using a password on the command line interface can be insecure.`
`ERROR 1045 (28000): Access denied for user 'root'@'localhost' (using password: YES)`
c'est que mysql est lancé en local sur votre ordinateur. Vous pouvez vérifier avec `brew services`, puis fermez-le avec :
 `brew services stop mysql@8.0`

## Configuration et Installation

- Clonez le repository: git clone <https://github.com/MTES-MCT/carbure.git>
- Créez un fichier `.env` à la racine du dépôt en vous basant sur le fichier `.env.example` disponible dans le dossier (Tu peux retrouver la pluspart des valeurs dans la section "Environnement" de carbure-prod sur scalingo <https://dashboard.scalingo.com/apps/osc-fr1/carbure-prod/environment>)
- créer un accès ssh à ton compte Scalingo (<https://dashboard.scalingo.com/account/keys>) et un API token (dans ton profile scalingo <https://dashboard.scalingo.com/account/tokens>)
- remplir SCALINGO_TOKEN=le token que tu as créé dans tom compte

Installation de pipenv :

- ajouter `export PIPENV_VENV_IN_PROJECT=1` au ~/.bashrc (ou ~/zshrc, etc...)

Ensuite, créez un environnement virtuel pour python 3.10:

- `pipenv install --dev`

- Dans le dossier /front, téléchargez les modules
 `npm install`

- Vous pouvez désormais builder les images docker et lancer le projet:
 `docker-compose build`
 `docker-compose up -d`

## Se placer dans l'environnement python dédié au projet

- Lancer `pipenv shell` pour vous placer dans l'environnement python dédié au projet

Raccourci : Je recommande de créer un alias pour charger l'environnement de développement : `alias carbure='cd /path/du/repository; pipenv shell;'`

## Alimenter la base de données de dev

- se connecter à scalingo `scalingo login --api-token $SCALINGO_TOKEN`
- Lancer `sh scripts/database/restore_db.sh` pour télécharger un dump contenant des données utilisables en local

## Création d'un nom de domaine local personnalisé

- Aller dans le fichier `/etc/hosts` (sur linux et mac)
- Ajouter la ligne `127.0.0.1 carbure.local`
- Vous pouvez maintenant accéder à votre version locale de carbure à l'adresse <http://carbure.local:8090/>

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
- Ensuite aller sur <http://carbure.local:8090/auth/login>
- Utiliser les informations renseignées à l'étape 1 puis valider l'authentification
- Carbure demande d'entrer un code envoyé par email
- Dans la version de dev ce code sera uniquement affiché dans les logs de django, visibles en tapant `docker logs carbure_app`Run all the tests

# Effectuer une migration

Lorsque des changement sont effectué sur la base de donnée :
1 une fois les model ou champs ajouté, pour créer le fichier de migration - `python web/manage.py makemigrations`
2 pour appliquer la migration sur la DB - `python web/manage.py migrate`

# Annuler une migration

il faut revenir à la migration precedent. Par exemple si veux annuler doublecount.0014_change_something
`python web/manage.py migrate doublecount 0013_remove_doublecountingapplication_dgddi_validated_and_more`

# Analyser les performances des requêtes

Lorsqu'un endpoint de l'API est lent, c'est 9 fois sur 10 à cause de problèmes avec la base de données: trop de requêtes successives, trop de résultats en une seule fois, etc.

Pour pouvoir analyser ces problèmes, l'outil `silk` a été mis en place sur le serveur.
On peut y accéder uniquement en local à l'adresse <http://carbure.local:8090/silk>.

La dashboard à cette adresse liste toutes les requêtes envoyées au serveur, et tout une série de métriques comprenant les différentes requêtes envoyées à la base de données ainsi que leur performance.

Pour plus d'information sur `silk`, une documentation est disponible à l'adresse <https://github.com/jazzband/django-silk>

# Lancer les tests backend

- Run all the tests in the api.v5.saf module
`python web/manage.py test api.v5.saf`
- Run just one test
`python web/manage.py test api.v5.saf.airline.tests.tests_ticket_details.SafTicketDetailsTest`
- Pour éviter de reconstruire la db de test à chaque fois, on peut ajouter l'option `--keepdb` à la fin de la commande

# Utiliser la console scalingo

`scalingo -a carbure-[dev/prod/staging] run bash`
`scalingo -a carbure-prod run bash`
`python web/manage.py shell`

example :

```
>>> from core.models import Entity
>>> entities = Entity.objects.filter(registered_address__isnull=False)
>>> entities.count()
```

-for v4 `docker exec -e TEST=1 carbure_app python3 web/manage.py test api.v4.tests_lots_flow`

## Executer un patch en local (script)

-Créer un fichier xxx.py dans le dossier `scripts/batches/` puis entrer dans le shell :
`python web/manage.py shell`
-et copier le code du script

`./scripts/database/reload_iscc_certifs.sh`
contenant un script pouvant etre lancé (ex <https://gitlab.com/la-fabrique-numerique/biocarburants/-/blob/master/web/carbure/scripts/update_iscc_certificates.py?ref_type=heads#L272>) :
`python3 web/carbure/scripts/update_iscc_certificates.py`

## Executer un script gourmand en ressource en prod

En lançant un one-off container (<https://doc.scalingo.com/platform/app/tasks>)
`scalingo --app carbure-prod run --size XXL python web/carbure/scripts/update_iscc_certificates.py`

## Étapes spécifiques pour windows

- setup wsl2: <https://docs.microsoft.com/en-us/windows/wsl/install-win10>
- installer docker desktop avec les libs WSL extra
- installer ubuntu 20.04: <https://www.microsoft.com/fr-fr/p/ubuntu-2004-lts/9n6svws3rx71?activetab=pivot:overviewtab>
- installer windows terminal: <https://www.microsoft.com/fr-fr/p/windows-terminal/9n0dx20hk701?rtc=1&activetab=pivot:overviewtab>
- activer ubuntu dans les options de docker desktop (resources > wsl)
- ouvrir ubuntu dans le windows terminal puis taper:
- `sudo apt-get update`
- `sudo apt-get install python3 python3-dev python3-pip default-libmysqlclient-dev build-essential`
- `pip install --user pipenv`

Ensuite, setup normalement le projet:

- ajouter les clé ssh <https://docs.gitlab.com/ee/ssh/#generate-an-ssh-key-pair>
- dans le terminal ubuntu, taper:
- `git clone git@gitlab.com:la-fabrique-numerique/biocarburants.git carbure`
- `cd carbure`
- `pipenv install`
- `(cd front; npm install)`
- `docker-compose up --build -d`
- `code .`
