# Scénario 1 — Hydrogène (H2)

Filière : **H2**  
Entités : **A** (déclarant), **B**, **C**  
Seed POC : `scenario_1` (état **final** après tout le parcours)

---

## Récit utilisateur

1. L'entité **A** crée un stock d'hydrogène de **1000 kg**.
2. À la création, A indique avoir consommé **700 kg** → **300 kg** restent en stock physique.
3. A consomme **150 kg** supplémentaires sur le stock restant → **150 kg** en stock physique.
4. A valide sa **déclaration mensuelle** → les consommations passent en attente DGEC (`PENDING`).
5. La **DGEC valide** → les consommations deviennent des **certificats** (`CONSOMMATION` + `ACCEPTED`).
   - Certificat **A** : 700 kg  
   - Certificat **B** : 150 kg  
6. A envoie **100 kg** du certificat A à **B** (en attente d'acceptation).
7. A envoie **150 kg** du certificat B à **C** (en attente d'acceptation).
8. **B accepte** le transfert de 100 kg.
9. **C refuse** le transfert de 150 kg → les 150 kg redeviennent disponibles sur le certificat B chez A.

---

## Arbre final (seed)

```
CREATION_H2  1000 kg  (owner: A)
├── CONSOMMATION  700 kg  ACCEPTED  ← certificat A
│   └── TRANSFERT  100 kg  ACCEPTED  (owner: B)
└── CONSOMMATION  150 kg  ACCEPTED  ← certificat B
    └── TRANSFERT  150 kg  REFUSED  (owner: C)
```

**Soldes `available` sur l'état final :**

| Nœud | quantity | available | Commentaire |
|------|----------|-----------|-------------|
| CREATION_H2 (A) | 1000 | **150** | 1000 − 700 − 150 |
| Certificat A | 700 | **600** | 700 − 100 (transfert accepté) |
| Certificat B | 150 | **150** | transfert refusé ne réserve pas |
| Transfert → B | 100 | 100 | accepté chez B |
| Transfert → C | 150 | 150 | refusé, visible chez C |

---

## Résultats attendus des requêtes (vérification manuelle)

Après `seed_stock_poc --scenario scenario_1`, lancer `query_stock_poc` sans argument.

| Entité | Requête | Attendu |
|--------|---------|---------|
| A | `consumption` | 1 ligne : CREATION_H2 1000, **available 150** |
| A | `certificates` | 2 lignes : CONSOMMATION 700 **dispo 600**, CONSOMMATION 150 **dispo 150** (ACCEPTED) |
| A | `sent` | 2 lignes : TRANSFERT 100 ACCEPTED, TRANSFERT 150 REFUSED |
| B | `received` | 1 ligne : TRANSFERT 100 ACCEPTED |
| C | `received` | 1 ligne : TRANSFERT 150 REFUSED (historique / refus) |

Commandes :

```bash
uv run python web/manage.py seed_stock_poc --scenario scenario_1
uv run python web/manage.py query_stock_poc
```

---

## Points métier à valider ensemble

- [ ] Le certificat = `CONSOMMATION` + statut `ACCEPTED` (pas de type séparé).
- [ ] Un transfert `REFUSED` libère le solde sur le certificat émetteur.
- [ ] Un transfert refusé reste visible côté destinataire (`received`) — à confirmer pour l'historique produit.
- [ ] Les étapes intermédiaires (PENDING déclaration, transferts en attente) : rejouer à la main et noter les écarts.

---

## Prochaines filières / scénarios

Dupliquer ce format de fiche :

```
docs/scenarios/
  h2-scenario-1.md   ← ce fichier
  h2-scenario-3.md   (à rédiger)
  <filière>-scenario-N.md
```

Chaque fiche = récit + arbre final + tableau de requêtes. Le seed correspondant vit dans `fixtures/scenarios.py`.
