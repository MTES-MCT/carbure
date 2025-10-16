# Carbure

Traçabilité et durabilité des biocarburants, de la production à la distribution

## Documentation

### Frontend
- [Documentation complète du frontend](./front/README.md) - Structure, commandes, tests et architecture du frontend


## Prérequis

Il est nécessaire d'avoir installé sur le poste local
- [Git](https://git-scm.com/)
- [docker compose](https://docs.docker.com/engine/install/)


## Configuration et Installation

Récupérer le code source depuis Github et aller dans le répertoire créé.

```bash
$ git clone https://github.com/MTES-MCT/carbure.git && cd carbure
```

Créer un fichier `.env` en se basant sur le fichier `.env.example`. Renseigner les valeurs des variables d'environnement.

Lancer l'application.

```bash
$ docker compose up
```


## Création d'un nom de domaine local personnalisé

Dans le fichier `/etc/hosts` ajouter la ligne `127.0.0.1 carbure.local`

Il est maintenant possible d'accéder à la version locale de CarbuRe à l'adresse `http://carbure.local:8090`.


# Authentification à Carbure

Bien vérifier que la variable d'environnement `IMAGE_TAG` est à `local` afin de désactiver la vérification de token CSRF.

Ajouter un nouveau super utilisateur CarbuRe dans la db locale :

```bash
docker compose exec carbure-django pipenv run python3 web/manage.py createsuperuser
```

… et renseigner les informations demandées. Aller ensuite sur `http://carbure.local:8090/auth/login` et compléter le formulaire d'authentification. CarbuRe demande d'entrer un code envoyé par eMail. Dans la version de dev toutefois, la fonctionnalité d'envoi d'eMail est bouchonnée et le code apparaît dans les logs de Django (consultable par la commande `docker compose logs carbure-django`).


# Migrations de données

## Créer un fichier de migration

Une fois les modèles ou champs modifiés, créer un fichier de migration par la commande `docker compose exec carbure-django pipenv run python3 web/manage.py makemigrations`

## Effectuer une migration

Appliquer les migrations sur la base de données par la commande `docker compose exec carbure-django pipenv run python3 web/manage.py migrate`

## Annuler une migration

Il faut parfois revenir à la migration précédente. Par exemple si on veut annuler `doublecount.0014_change_something` :

`python web/manage.py migrate doublecount 0013_remove_doublecountingapplication_dgddi_validated_and_more`


# Analyser les performances des requêtes

Lorsqu'un endpoint de l'API est lent, c'est 9 fois sur 10 à cause de problèmes avec la base de données: trop de requêtes successives, trop de résultats en une seule fois, etc.

Pour pouvoir analyser ces problèmes, l'outil `silk` a été mis en place sur le serveur.
On peut y accéder uniquement en local à l'adresse <http://carbure.local:8090/silk>.

La dashboard à cette adresse liste toutes les requêtes envoyées au serveur, et tout une série de métriques comprenant les différentes requêtes envoyées à la base de données ainsi que leur performance.

Pour plus d'information sur `silk`, une documentation est disponible à l'adresse <https://github.com/jazzband/django-silk>


# Lancer les tests backend

Pour lancer tous les tests : `docker compose run --rm carbure-test`

Pour lancer tous les tests d'un module : `docker compose run --rm carbure-test pipenv run test <nom_du_module>`

Pour lancer un seul test : `docker compose run --rm carbure-test pipenv run  test api.v5.saf.airline.tests.tests_ticket_details.SafTicketDetailsTest`
