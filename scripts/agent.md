# Environnement local pour un agent

Deux checkouts du repo peuvent tourner en même temps : le tien sur `http://carbure.local:8090`, celui d'un agent (autre worktree git) sur `http://carbure.local:8190`.

MySQL, Redis et le mock S3 ne sont pas dupliqués. L'agent a son propre Django, son propre Vite et son propre nginx. Sa base s'appelle `carbure_agent`, sur le même serveur MySQL que la tienne.

Ton environnement doit déjà tourner (`make up`) avant `make agent-up`.

## Fichiers

| Fichier | Rôle |
|---|---|
| `docker-compose.yml` | Le modèle des services. Les valeurs entre `${...:-...}` ont un défaut, celui de ton environnement. |
| `docker-compose.agent.env` | Uniquement ce qui doit différer pour l'agent. |
| `docker-compose.agent.yml` | Deux réglages qu'une variable ne peut pas exprimer. |
| `gateway/default.conf.template` | Le nginx, partagé. Le nom des conteneurs est injecté au démarrage. |
| `scripts/agent.sh` | Crée la base, puis lance le second environnement. |
| `Makefile` | `make agent-up`, `agent-down`, `agent-logs` appellent ce script. |

## Ce qui change pour l'agent

`docker-compose.agent.env` :

| Variable | Le tien (défaut) | Agent |
|---|---|---|
| `CARBURE_FRONTEND_CONTAINER` | `carbure_frontend` | `carbure_agent_frontend` |
| `CARBURE_APP_CONTAINER` | `carbure_app` | `carbure_agent_app` |
| `CARBURE_PROXY_CONTAINER` | `carbure_web` | `carbure_agent_web` |
| `WEB_PORT` | `8090` | `8190` |
| `CARBURE_DATABASE` | la base de ton `.env` | `carbure_agent` |
| `REDIS_DB` | `0` | `1` |
| `AWS_ENV_FOLDER_NAME` | `carbure-local` | `carbure-agent` |
| `UPLOADED_FILES_VOLUME` | `carbure_uploadedfiles` | `carbure_agent_uploadedfiles` |

Les noms de conteneurs doivent différer : Docker n'autorise qu'un conteneur de chaque nom sur la machine. Le port aussi, sinon les deux nginx voudraient `8090`.

Redis `1` est un index logique du même Redis, pour que les clés de session de l'agent ne mélangent pas les tiennes. Le dossier S3 et le volume de fichiers suivent la même idée.

Dans `docker-compose.yml`, une écriture comme `${WEB_PORT:-8090}` veut dire : prendre `WEB_PORT` s'il est défini, sinon `8090`. `make up` ne définit pas ces variables, donc ton environnement ne change pas.

## Pourquoi `docker-compose.agent.yml` existe

`scripts/agent.sh` charge les deux fichiers compose. Le second ne fait que surcharger le premier.

`depends_on: !reset []` retire la dépendance de Django vers MySQL et Redis. Sans ça, `up` essaierait de recréer `carbure_mysql`, déjà utilisé par ton environnement.

`networks.carbure.external` branche les conteneurs de l'agent sur le réseau déjà créé par ton environnement (`carbure_default`). C'est ce réseau qui permet à son Django de joindre l'hôte `carbure-mysql`.

## Nginx

`gateway/default.conf.template` est l'ancienne config. Les hôtes `carbure_frontend` et `carbure_app` sont devenus `${CARBURE_FRONTEND_HOST}` et `${CARBURE_BACKEND_HOST}`. L'image nginx les remplace au démarrage du conteneur.

Chez toi, le résultat est identique à avant : le proxy envoie `/` vers `carbure_frontend:3000` et `/api` vers `carbure_app:8000`. Pour l'agent, les mêmes règles visent `carbure_agent_frontend` et `carbure_agent_app`.

## `scripts/agent.sh`

`make agent-up` appelle `./scripts/agent.sh up`.

1. Il crée la base `carbure_agent` sur le MySQL déjà lancé, si elle n'existe pas. Les migrations partent ensuite toutes seules au démarrage du conteneur Django, comme pour ton environnement.
2. Il lance seulement `carbure-frontend`, `carbure-django` et `carbure-web-proxy`, sous le nom `carbure-agent` (`-p` dans la commande Docker).

Ce nom sert de groupe. `make agent-down` ne s'arrête que sur les conteneurs de ce groupe, pas sur les tiens. Les deux ne se voient pas, à part le réseau et MySQL qu'on a explicitement partagés.

Le script recharge `docker-compose.agent.env` dans le shell avant d'appeler Compose. Le Makefile exporte déjà ton `.env` : sans ce rechargement, des variables comme `AWS_ENV_FOLDER_NAME` garderaient la valeur de ton environnement.

`make agent-down` arrête les conteneurs de l'agent. Ton environnement et la base `carbure_agent` restent.

## Utilisateurs

Ce montage ne crée pas de compte. La base `carbure_agent` est vide, hors référentiel chargé par le démarrage Django (pays, matières, régions). Les comptes se ajoutent au cas par cas, selon la feature.
