# Intégration UDB, env local

- Lander docker compose : `docker-compose up -d`
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


