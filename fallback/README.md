# Pages d'erreur

Ces pages statiques permettent à Scalingo d'afficher un message lorsque CarbuRe est inaccessible ou qu'une requête est refusée. Elles seront hébergées sur AlwaysData à l'adresse [fallback.carbure.beta.gouv.fr](https://fallback.carbure.beta.gouv.fr/).

## Modifier une page

Chaque fichier JSON dans `pages/` décrit une page :

- `titre_page` : titre de l'onglet du navigateur.
- `titre` : titre affiché sur la page.
- `message` : explication du problème.
- `information` : indication sur la marche à suivre.

Le fichier `template.html` définit la mise en page commune. Pour générer les pages localement après une modification, lancer depuis la racine du projet :

```sh
make fallback
```

Le script génère les pages dans `dist/` avec le même nom que leur fichier JSON : par exemple, `pages/timeout.json` produit `dist/timeout.html`.

## Déploiement automatique

La CI GitLab génère et déploie les pages sur AlwaysData lorsqu'un fichier de `fallback/` change sur `master`.

Notez que les pages supprimées doivent être retirées manuellement du serveur.

Variables GitLab CI/CD :

- `FALLBACK_FTPS_URL` : URL FTPS du répertoire cible.
- `FALLBACK_FTPS_USER` : identifiant FTP.
- `FALLBACK_FTPS_PASSWORD` : mot de passe FTP, masqué et protégé.

## Configurer Scalingo

Une fois les pages hébergées, renseigner leurs URL dans les variables Scalingo correspondantes :

| Variable                      | Fichier                                                |
| ----------------------------- | ------------------------------------------------------ |
| `SCALINGO_NO_FRONT_ERROR_URL` | `https://fallback.carbure.beta.gouv.fr/no-front.html`  |
| `SCALINGO_STOPPED_PAGE_URL`   | `https://fallback.carbure.beta.gouv.fr/stopped.html`   |
| `SCALINGO_APP_ERROR_URL`      | `https://fallback.carbure.beta.gouv.fr/app-error.html` |
| `SCALINGO_TIMEOUT_ERROR_URL`  | `https://fallback.carbure.beta.gouv.fr/timeout.html`   |
| `SCALINGO_FORBIDDEN_PAGE_URL` | `https://fallback.carbure.beta.gouv.fr/forbidden.html` |

Voir la [documentation Scalingo](https://doc.scalingo.com/platform/app/custom-error-page) pour la configuration des pages d'erreur personnalisées.
