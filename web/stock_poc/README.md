# Stock POC — arborescence de gestion de stocks

POC isolé dans Carbure pour explorer la modélisation **stock → consommation → certificat → transfert** sous forme d’**arbre d’actions**, avant de figer le design produit et les requêtes métier.

---

## Objectif

Comprendre et valider ensemble :

1. **Comment modéliser** les flux de stock (physique et « comptable ») en nœuds liés par un parent.
2. **Comment calculer** ce qui est encore disponible sur un nœud (`available`).
3. **Quelles requêtes** seront nécessaires côté produit (consommable, certificats, transferts émis/reçus, historique…).

---

## Modèle de données

Une seule table : `stock_poc_action` (`Action`).

| Champ | Rôle |
|-------|------|
| `type` | Nature de l’action (voir ci-dessous) |
| `quantity` | Quantité portée par ce nœud |
| `owner` | Entité propriétaire |
| `parent` | Action parente (auto-référence → arbre) |
| `status` | Workflow (`PENDING`, `ACCEPTED`, `REFUSED`, ou `null`) |
| `available` | **Calculé** : solde encore disponible sur ce nœud |

### Types d’action

| Type | Rôle métier (POC) |
|------|-------------------|
| `CREATION_H2` | Entrée de stock hydrogène |
| `CONSOMMATION` | Quantité consommée ; une fois validée par l’admin, **joue le rôle de certificat** |
| `TRANSFERT` | Envoi d’une part de certificat vers une autre entité |
| `PERTE` | Reliquat déclaré perdu (plus utilisable) |

### Règle de solde (`available`)

```
available = quantity − Σ(enfants directs qui réservent)
```

Un enfant **réserve** sa quantité **sauf** si `status = REFUSED`.  
Les enfants sans statut (ex. `PERTE`) **réservent** quand même.

---

## Scénarios métier (fiches)

Les parcours utilisateur sont documentés en **markdown** (récit + arbre final + tableau de vérification manuelle).

| Fiche | Seed | Filière |
|-------|------|---------|
| [h2-scenario-1.md](docs/scenarios/h2-scenario-1.md) | `scenario_1` | H2 |
| *(à rédiger)* | `scenario_3` | H2 |

Les données de seed (arbre final) sont dans `fixtures/scenarios.py`.

---

## Architecture

```
web/stock_poc/
  docs/scenarios/           # Fiches métier (collègues)
  fixtures/scenarios.py     # Arbres finaux par scénario
  services/
    balance.py              # Calcul available
    queries.py              # Requêtes CLI
    seed.py
  management/commands/
    seed_stock_poc.py
    query_stock_poc.py
front/src/stock-poc/        # UI arborescence + CRUD minimal
```

---

## Utilisation locale

### Migrations

```bash
make migrate
```

### Charger un scénario (état final)

```bash
uv run python web/manage.py seed_stock_poc --list
uv run python web/manage.py seed_stock_poc --scenario scenario_1
```

Crée les entités `POC Stock Entity A/B/C` si besoin, puis l’arbre final du scénario.

### Vérifier les requêtes (manuel)

```bash
uv run python web/manage.py seed_stock_poc --scenario scenario_1
uv run python web/manage.py query_stock_poc
```

Sans argument, exécute tous les scénarios de requête pour les entités POC.

L’interface web affiche les mêmes scénarios (section « Requêtes métier »), avec un sélecteur d’entité (`query_entity_id`).

```bash
uv run python web/manage.py query_stock_poc --list
uv run python web/manage.py query_stock_poc --scenario certificates --entity-id <id>
```

Ajouter une entrée dans `services/queries.py` → visible en CLI et en UI automatiquement.

Requêtes disponibles : `consumption`, `certificates`, `owned`, `sent`, `received`, `all`.

### Interface web

Page **Stock POC (arborescence)** : visualiser l’arbre, créer/modifier/supprimer des actions, reset global.

---

## Plan de travail

### Phase actuelle

- [ ] Rédiger une fiche markdown par scénario / filière
- [ ] Seed état final dans `fixtures/scenarios.py`
- [ ] Valider les requêtes à la main (`query_stock_poc` + tableau de la fiche)
- [ ] Affiner `services/queries.py` si les résultats ne matchent pas

### Phase suivante (quand le métier est stable)

- [ ] Scénarios impératifs avec refs sémantiques (`root`, `cert_a`, …)
- [ ] Assertions automatiques (optionnel)

---

## Conventions POC

- Pas de tests automatisés tant que le métier bouge.
- **Fiche markdown = source de vérité humaine** ; seed = snapshot final.
- Entités test : `POC Stock Entity A/B/C`.
