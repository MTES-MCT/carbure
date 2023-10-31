> Note: Les scripts disponibles dans ce dossier sont pensés pour être lancés depuis le dossier `/app` d'un container Docker ou Scalingo, ou bien depuis le dossier `[carbure]/udb` sur l'env local d'un développeur.

# Intégration UDB, env local

- Lancer docker compose : `docker-compose up -d`
- Construire le nouveau container docker pour `blue` : `docker-compose build carbure-udb-blue`
- Répéter pour `red` : `docker-compose build carbure-udb-red`
- Redémarrer l'env docker : `docker-compose down && docker-compose up -d`
- Lancer les migrations sur la db pour `blue`: `docker exec -it carbure_udb_blue bash migrate.sh`
- Répéter pour `red` : `docker exec -it carbure_udb_red bash migrate.sh`
- Redémarrer le container domibus: `docker-compose restart carbure-udb-blue carbure-udb-red`
- Aller dans les logs de `carbure-udb-blue` et `carbure-udb-red` et trouver la ligne mentionnant "Default password for user [admin] is ***"
- Dans un navigateur, aller sur la page `http://localhost:8080/domibus` pour `blue` (ou `http://localhost:8081/domibus` pour `red`) et utiliser le mot de passe obtenu avec le username `admin`
- On vous invitera à changer de mot de passe
- Pour `red` et `blue` aller dans leur console d'administration Menu 'PMode' et uploader les fichiers `domibus-gw-sample-pmode-*.xml` correspondants.


# Préparation de la base de données pour scalingo

Les scripts d'initialisation de la db domibus sont incompatibles avec la configuration des db scalingo. Il faut donc passer par une étape de transformation pour pouvoir générer un script qui fonctionne.

- Dans l'environnement de dev local, lancer une instance de domibus (voir au dessus)
- Exécuter le script de dump de la db: `docker exec -it carbure_udb_blue bash ./database/generate_scalingo_migration.sh`
- Un fichier `scalingo_migration.sql` a été généré à l'intérieur du container, il faut le copier sur le host: `docker cp carbure_udb_blue:/app/database/scalingo_migration.sql ./database/scalingo_migration.sql`
- Dans le fichier `scalingo_migration.sql`, changer le nom de base de donnée utilisé pour correspondre au nom du schéma utilisé sur scalingo.
- Facultatif: il peut y avoir des problèmes dans le fichier, une modification de `scalingo_migration.sql` est possiblement requise (ajout de primary key par exemple)
- Se connecter à scalingo en joignant le dump: `scalingo --region osc-secnum-fr1 -a carbure-domibus run --file ./scalingo_migration.sql bash`
- Charger le dump dans la db: `mysql --user=$DOMIBUS_DATASOURCE_USER --password=$DOMIBUS_DATASOURCE_PASSWORD --host=$DOMIBUS_DATABASE_SERVERNAME --port=$DOMIBUS_DATABASE_PORT $DOMIBUS_DATABASE_SCHEMA < /tmp/uploads/scalingo_migration.sql`

> Note: pour éviter de répéter cette opération, il est préférable de commit le fichier `scalingo_migration.sql`, mais uniquement si ce fichier ne cause pas de problème sur scalingo.

> Note 2: Cette opération n'est normalement nécessaire que lors de la création d'une nouvelle db pour domibus sur scalingo. Pour une db existante, les scripts de migration officiels fournis par domibus devraient fonctionner.


# Partager des fichiers privés avec scalingo

Pour fonctionner, domibus a besoin d'au moins 2 fichiers contenant des données privées: `gateway_keystore.jks` et `gateway_truststore.jks`. Ces fichiers ne doivent surtout pas être commit dans le repo git étant donné qu'ils contiennent des clés privées.

Pour pouvoir les déployer sur scalingo, il faut utiliser des variables d'environnement, voir le guide suivant: [https://doc.scalingo.com/platform/app/secret-file-in-app]()

> Note: Les variables d'environnement de scalingo ont une limite de 8192 caractères

> Le nom utilisé pour ces fichiers peut être configuré à travers les variables d'environnement `DOMIBUS_SCEURITY_KEYSTORE` et `DOMIBUS_SCEURITY_TRUSTSTORE`.
> Exemple: si `DOMIBUS_SECURITY_KEYSTORE=carbure`, le fichier correspondant sera `carbure_keystore.jks`.
