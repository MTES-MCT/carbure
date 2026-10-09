# TIRUERT — règles métier

Ce document rassemble les règles métier actuellement implémentées dans le module `web/tiruert`. Il est destiné aux personnes qui font évoluer le produit comme aux agents de développement qui doivent comprendre les invariants avant de modifier le code.

> **Portée et autorité.** Cette documentation décrit le comportement du logiciel et ses paramètres, pas une interprétation juridique autonome des textes réglementaires. Les règles dépendant d'une année (objectifs, taux, périodes) sont à lire dans les données configurées pour cette année. En cas d'écart, vérifier d'abord le service propriétaire et ses tests ; ne pas déduire une règle réglementaire d'un ancien import ou d'une commande ponctuelle.

## 1. Repères métier et unités

- Une **opération** inscrit un mouvement de volume de lot entre une entité créditée et/ou débitée. Ses **détails** identifient les lots Carbure consommés ou crédités, leur volume et leur intensité d'émission retenue.
- Une opération de **TENEUR** consomme un volume détenu par l'entité débitée et contribue à sa teneur déclarée ou en attente. Une opération de **CESSION** débite l'expéditeur et crédite le destinataire en conservant la référence aux lots.
- La **MAC** désigne ici une mise à la consommation de carburant fossile (`MacFossilFuel`), utilisée pour calculer l'assiette énergétique des objectifs. Elle est distincte du type d'opération `MAC_BIO`, qui est un crédit de lots biocarburants issus de livraisons RFC.
- Les quantités manipulées sont exprimées en litres pour les volumes de lots, en MJ pour l'énergie et en tCO2 pour les émissions évitées. Les taux d'émission sont en gCO2/MJ ; les taux de pénalité sont des données exprimées en centimes selon l'unité de l'objectif.
- Pour un lot, l'énergie vaut `volume (L) × PCI du biocarburant (MJ/L) × part d'énergie renouvelable`. Les calculs partagés Python/ORM sont dans [`services/energy.py`](services/energy.py).

## 2. Opérations et mouvements de lots

### Types et statut

Les types métier persistés sont définis dans [`models/operation.py`](models/operation.py). Les crédits physiques initiaux sont `INCORPORATION`, `MAC_BIO` et `LIVRAISON_DIRECTE`. Les opérations `CESSION`, `TENEUR`, `TRANSFERT`, `EXPORTATION`, `EXPEDITION`, `DEVALUATION`, `CUSTOMS_CORRECTION`, `EXPIRATION` et `REPORT` représentent des mouvements ou ajustements distincts ; certains sont générés par des traitements internes et ne sont pas créables via l'API standard.

- Les statuts actifs pour les calculs de solde sont `PENDING`, `ACCEPTED`, `VALIDATED`, `DECLARED` et `DRAFT`. `REJECTED` et `CANCELED` sont exclus.
- Une opération créditrice `PENDING` ou `DRAFT` ne crédite pas encore le solde disponible. Un débit actif en attente peut en revanche réserver/réduire le solde calculé. Les opérations `PENDING` et `DRAFT` restent comptées comme opérations en attente.
- Les statuts considérés comme confirmés sont `ACCEPTED`, `VALIDATED` et `DECLARED` ; certains traitements, notamment l'expiration, utilisent cette notion plus restrictive.
- À la création par l'API, `INCORPORATION`, `MAC_BIO`, `LIVRAISON_DIRECTE` et `DEVALUATION` sont automatiquement acceptées par le service de statut. Pour les autres types créables, le statut devient `PENDING`, sauf si un `DRAFT` a été explicitement conservé.
- La création des crédits issus des lots Carbure est un autre chemin : ces opérations sont actuellement créées au statut `VALIDATED`. Le code porte un TODO indiquant une éventuelle validation DGDDI future ; ne pas assimiler ce commentaire à une règle déjà active.
- La liste des types créables/supprimables par l'API est différente de la liste des types persistés : vérifier `API_CREATABLE_TYPES` et `API_DELETABLE_TYPES` avant d'ajouter une opération à un endpoint.

### Création automatique des crédits depuis CarbureLot

[`services/operation.py`](services/operation.py) convertit les lots éligibles en opérations TIRUERT. Les filtres appliqués sont cumulatifs :

1. Le lot doit être `ACCEPTED` ou `FROZEN`.
2. Le type de livraison doit être `BLENDING`, `DIRECT` ou `RFC`. Pour `RFC`, l'usage doit être autorisé (route, agriculture, construction, maritime, voie navigable intérieure ou rail) ou vide.
3. Le site de livraison doit être en France ou absent.
4. Un lot qui possède déjà un détail d'opération TIRUERT n'est pas recréé.

Correspondance des livraisons : `BLENDING` → `INCORPORATION`, `DIRECT` → `LIVRAISON_DIRECTE`, `RFC` → `MAC_BIO`. Les lots sont groupés par type de livraison, catégorie douanière de l'intrant, biocarburant et dépôt ; chaque lot reste une ligne de détail.

Transformations métier avant création :

- La matière première `EP2` est ventilée en 40 % `CONV` et 60 % `EP2AM`.
- Le volume des lots `ETH` est multiplié par `0.995` (conversion en volume correspondant à l'éthanol 15°), puis tronqué à la précision de volume.
- Les biocarburants `EMHV`, `EMHU`, `EMHA` et `B100` sont convertis en `EMAG` pour ces opérations.
- Le taux d'émission du détail provient du GES du lot lors de la création de l'opération.

Les règles d'éligibilité et ces transformations s'appliquent à la génération automatique, pas nécessairement à chaque opération saisie manuellement.

### Secteur et catégorie

Le secteur d'un biocarburant suit l'ordre de priorité du calcul : essence, gazole, carburéacteur (codes SAF), GPL, maritime. À défaut, aucun secteur n'est déduit. Pour une opération `TENEUR`, `objective_sector` peut remplacer le secteur naturel pour l'affectation de l'objectif ; ce champ n'est autorisé que pour ce type d'opération.

La catégorie douanière de l'opération est une donnée portée par l'opération (souvent dérivée de la catégorie de matière première du lot). Les soldes et plafonds catégoriels ne doivent pas agréger des catégories différentes.

## 3. Soldes de biocarburants

Le calcul commun est dans [`services/balance.py`](services/balance.py) et [`services/balance_annotations.py`](services/balance_annotations.py). Les soldes sont calculés pour une entité à partir des opérations et de leurs détails, après application des filtres fournis par l'appelant.

- **Crédit** : volume d'un détail lorsque l'entité est `credited_entity`. **Débit** : volume lorsque l'entité est `debited_entity`. Le solde disponible est la somme signée des opérations actives, avec les crédits positifs et les débits négatifs.
- En litres, la quantité comptabilisée est le `volume` du détail. En MJ, elle inclut le PCI du biocarburant et la part renouvelable de l'opération. Les compteurs de teneur sont en MJ, indépendamment de l'unité d'affichage demandée pour le solde.
- Les regroupements standards sont par secteur, catégorie douanière, biocarburant ou lot. Un solde par lot conserve le volume, les émissions évitées et le taux d'émission associé au détail ; les champs de teneur ne sont pas exposés sur ce regroupement.
- Les contributions de teneur `PENDING` et `DECLARED` sont calculées à part des flux de volume. Elles sont groupées par opération avant agrégation ; l'énergie de chaque opération est tronquée en MJ entiers avant d'être cumulée. Les émissions évitées sont agrégées au niveau des détails.
- Les émissions évitées d'un détail sont `(94 - taux d'émission du détail) × énergie / 1 000 000`, en tCO2. La référence actuelle pour les biocarburants est 94 gCO2/MJ.
- Les filtres de GES, matière première, pays d'origine et période de durabilité s'appliquent au niveau des détails de lot. Pour le filtre de période de durabilité, les lots sont d'abord résolus depuis les opérations créditrices de cette période ; les mouvements ultérieurs portant sur ces mêmes lots restent pris en compte.
- Les volumes négatifs détectés dans la préparation d'une simulation sont signalés puis ramenés à zéro pour l'optimisation ; ce n'est pas une correction persistée du solde.
- Toute correction GHG d'un lot doit rester cohérente entre les valeurs exposées par les propriétés Python et celles utilisées par les annotations et filtres ORM. Lorsqu'une nouvelle lecture ou agrégation GHG est ajoutée, vérifier que les deux chemins reflètent les mêmes données corrigées et couvrir leur cohérence par un test.
- Les dimensions dérivées du lot pour constituer le groupe (catégorie via `lot.feedstock.category`, biocarburant via `lot.biofuel`) doivent provenir du `CarbureLot` référencé, et non d'un ancien `OperationDetail`. La clé complète inclut le type d'opération et l'entité créditée en plus de ces dimensions.
- Les volumes d'un même lot doivent être additionnés avant de vérifier sa disponibilité, y compris lorsque plusieurs groupes de l'import le consomment ; valider chaque groupe isolément ne suffit pas.

Lorsqu'une année de déclaration est donnée, le solde retient les opérations dont la période de durabilité est antérieure à l'année suivante (ou absente) **et** dont l'année de déclaration est au plus celle demandée (ou absente). Sans année explicite, le service utilise l'année de la période déclarative en cours ; s'il n'en existe aucune, il n'applique pas ce bornage. `created_at` n'est pas le critère de ce filtrage métier.

## 4. Objectifs, assiette et pénalités

Les paramètres d'objectifs sont des lignes `Objective` par année et type (`MAIN`, `SECTOR`, `BIOFUEL_CATEGORY`). Les cibles sont des proportions (par exemple `0.50` pour 50 %), et les taux de pénalité sont configurés en centimes. Les formules sont dans [`services/objective.py`](services/objective.py).

### Assiette énergétique des MAC

Pour une entité et une année, l'assiette est calculée sur ses enregistrements `MacFossilFuel` de cette année :

`assiette (MJ) = Σ [volume MAC × PCI de la catégorie fossile × taux de prise en compte de la catégorie pour l'année]`

Le taux de prise en compte est celui associé à la catégorie fossile et à l'année de calcul ; en l'absence de ligne correspondante, le code applique `1`. L'objectif principal et les objectifs par catégorie utilisent l'assiette globale. Chaque objectif sectoriel calcule sa propre assiette avec les MAC de sa catégorie de carburant fossile.

Une cible énergétique vaut `assiette × proportion cible`. Pour l'objectif principal, la cible en MJ est ensuite convertie en tCO2 avec le facteur de référence biocarburant de 94 gCO2/MJ.

### Teneurs retenues et pénalités

- Les objectifs `REACH` et `CAP` sont des types de cible configurés. Le calcul de déficit/pénalité est nul lorsque la teneur atteint ou dépasse la cible ; sinon il porte sur l'écart.
- Pour un objectif en énergie, l'écart en MJ est converti en GJ (division par 1 000) avant application du taux en c€/GJ. Pour un objectif global en tCO2, l'écart n'est pas divisé par 1 000 et le taux s'applique en c€/tCO2.
- L'objectif global additionne les émissions évitées des biocarburants et celles de l'électricité. La conversion de l'électricité utilise 183 gCO2/MJ, distinct du facteur biocarburant de 94 gCO2/MJ.
- Les opérations électriques peuvent être affectées à un secteur pour la teneur sectorielle. Leur solde énergétique disponible reste toutefois un pool électrique global partagé, non cloisonné par secteur.
- Les objectifs sectoriels agrègent aussi les teneurs électriques affectées au secteur, puis recalculent la pénalité sur le total ainsi obtenu.
- Un objectif `CAP` de catégorie sans aucune opération de la catégorie n'est pas renvoyé dans la réponse d'objectifs. Les contrôles de dépassement à la création de TENEUR ne portent que sur les plafonds catégoriels.

Les paramètres chiffrés réglementaires ne sont pas à coder en dur dans cette documentation : consulter les données `Objective`, `FossilFuelCategoryConsiderationRate` et le référentiel fossile pour l'année concernée.

## 5. Teneur : simulation et consommation

La simulation et les contrôles de lots sont portés par [`services/teneur.py`](services/teneur.py) et [`services/operation.py`](services/operation.py).

- Une TENEUR consomme des lots détenus par l'entité débitée. Chaque lot doit être disponible dans le solde de la combinaison biocarburant/catégorie demandée ; les volumes répétés pour un même lot sont additionnés avant contrôle.
- Le volume demandé est tronqué à deux décimales. La simulation ne peut pas demander plus que le volume disponible total. Les volumes imposés (`enforced_volumes`) ne peuvent pas dépasser le disponible de leur lot.
- Une limite `max_n_batches` impose un nombre maximal de lots non nuls. Elle doit être au moins égale au nombre de lots ayant un volume imposé non nul.
- L'optimisation minimise les émissions du mélange sous contrainte du volume cible et du niveau maximal d'émissions correspondant à l'objectif de réduction demandé. Elle utilise une programmation linéaire, ou une programmation mixte lorsque le nombre de lots est limité.
- La sortie est arrondie/tronquée à deux décimales et son total ne doit pas dépasser le volume cible normalisé. L'absence de mélange réalisable, un volume insuffisant ou des volumes imposés incohérents produisent des erreurs métier dédiées.
- Les bornes min/max d'émissions mélangent les lots dans l'ordre des taux d'émission croissants/décroissants et retournent des émissions évitées en tCO2.
- Les filtres de simulation (période de durabilité, GES, intrant, pays d'origine) s'appliquent aux lots disponibles ; ils ne modifient pas les opérations enregistrées.

Avant de créer une opération `TENEUR`, le plafond catégoriel éventuel est vérifié : teneurs déjà `PENDING` et `DECLARED` de la catégorie + teneur proposée ne doivent pas dépasser la cible en MJ. L'égalité au plafond est autorisée. Si aucun plafond n'est configuré (ou si l'assiette permettant de le calculer est absente), ce contrôle ne bloque pas la création.

Pour un import Excel groupant plusieurs TENEUR, le contrôle doit être effectué sur le total des groupes d'une même catégorie, pas seulement groupe par groupe.

## 6. Mises à la consommation fossiles (MAC)

Les modèles et règles de l'assiette sont dans [`models/mac_fossil_fuel.py`](models/mac_fossil_fuel.py), les combustibles et catégories dans [`models/fossil_fuel.py`](models/fossil_fuel.py) et [`models/fossil_fuel_category.py`](models/fossil_fuel_category.py), les taux annuels dans [`models/fossil_fuel_category_consideration_rate.py`](models/fossil_fuel_category_consideration_rate.py).

- Une ligne MAC est rattachée à un opérateur, un combustible, un mois/période et une année, avec un volume, un dépôt éventuel et des dates de début/fin.
- L'unicité métier en base porte sur opérateur + combustible + période. Lors d'une saisie, le mois doit être compris entre 1 et 12 et le volume doit être positif ou nul.
- Le PCI utilisé dans l'assiette est celui de la **catégorie** fossile ; le combustible fournit notamment son rattachement catégoriel.
- Le calcul filtre les MAC sur l'année de l'objectif. Une correction de MAC peut donc modifier l'assiette, les cibles et les pénalités recalculées pour cette année.

Ne pas confondre ces données d'assiette fossile avec `Operation.MAC_BIO`, qui crédite le solde de lots biocarburants.

## 7. Électricité

Les opérations électriques sont stockées séparément dans `ElecOperation` et calculées par [`services/elec_balance.py`](services/elec_balance.py).

- Les types sont `ACQUISITION_FROM_CPO`, `CESSION` et `TENEUR`. Les quantités sont toujours en MJ. Une cession reçue par l'entité est présentée comme une acquisition dans les listes, sans changer son type stocké.
- Une acquisition CPO est un crédit ; une cession peut créditer une entité et débiter l'autre ; une TENEUR est un débit. Les statuts retenus dans le solde sont `PENDING`, `ACCEPTED` et `DECLARED`.
- Le solde disponible est crédits acceptés moins débits actifs. Une TENEUR en attente ou déclarée est exposée séparément. Les teneurs sont ventilées par `objective_sector`, mais le disponible électrique complet demeure utilisable quel que soit le secteur.
- Le contrôle d'une cession sortante compare sa quantité au disponible de l'entité débitée. Une mise à jour réintègre la quantité de l'opération modifiée dans le disponible avant comparaison.
- La synchronisation des acquisitions CPO prend les certificats acceptés non encore utilisés, émis depuis 2025 par un fournisseur CPO à destination de l'opérateur. Les MWh sont convertis en MJ par `× 3600`, puis diminués du total des acquisitions CPO déjà acceptées. Une différence positive crée une acquisition ; zéro ne fait rien ; une différence négative déclenche une erreur.
- Le taux d'émission utilisé pour les conversions électriques vers tCO2 est `183 gCO2/MJ`.

Les règles d'acceptation et de déclaration des opérations sont testées dans `tests/views/elec_operation/` et le calcul du solde dans `tests/services/test_elec_balance.py`.

## 8. Années, clôtures et snapshots

Une période TIRUERT est une période de déclaration configurée (dates de début/fin et année), portée par [`models/declaration_period.py`](models/declaration_period.py). L'année courante est la période contenant la date du jour ; sans période correspondante, le service renvoie `None`.

- Les créations d'opérations API exigent une année de déclaration et la remplissent depuis le contexte de la période courante.
- Les objectifs d'une période prennent les opérations créées au plus tard à la fin de la période et bornent leurs calculs avec l'année de déclaration et la période de durabilité.
- Pour une période passée, l'API des objectifs sert le snapshot de l'entité s'il existe ; sinon elle peut recalculer à partir des données disponibles. Un snapshot contient les objectifs calculés et un solde de volumes/énergie/émissions figé à la clôture.
- Le lendemain de la fin d'une période, `snapshot_objectives` crée ou met à jour les snapshots des entités assujetties (`is_tiruert_liable=True`). Une entité sans période, objectif, MAC ou opérations nécessaires peut être ignorée par le calcul.
- La vue d'administration agrégée lit un cache préparé en amont ; si ce cache n'existe pas pour l'année demandée, l'API répond `503` au lieu de recalculer sur la requête.
- Le lendemain de la clôture, `cancel_closed_period_operations` annule les opérations encore `PENDING` ou `DRAFT` parmi les types supprimables de l'API, pour l'année de déclaration clôturée.
- À la clôture de la période, `set_operations_expired` traite la période de durabilité correspondant à `année de déclaration clôturée - 1`. Il annule les crédits initiaux en attente, puis annule les opérations `PENDING`/`DRAFT` liées aux lots expirés et crée des opérations `EXPIRATION` pour les seuls volumes restants issus de crédits confirmés. Le traitement est idempotent au niveau d'une période déjà expirée.
- Le calcul d'expiration tient compte de la part renouvelable des mouvements source ; le volume expiré est enregistré avec une part renouvelable égale à 1 pour ne pas appliquer ce facteur une seconde fois. Les lots transférés peuvent produire des expirations pour plusieurs entités selon leur solde propre.

Les commandes de clôture sont documentées dans leurs docstrings et doivent être vérifiées avec leurs tests avant toute modification : [`snapshot_objectives.py`](management/commands/snapshot_objectives.py), [`cancel_closed_period_operations.py`](management/commands/cancel_closed_period_operations.py) et [`set_operations_expired.py`](management/commands/set_operations_expired.py).

## 9. Import, corrections et exceptions historiques

- L'import Excel des opérations accepte `TENEUR` et `TRANSFERT`. Les lignes sans volume sont ignorées ; les volumes renseignés doivent être strictement positifs. Un destinataire est obligatoire pour un transfert.
- Les lignes sont regroupées par type, catégorie douanière, biocarburant et entité créditée. Les répétitions d'un lot dans un groupe sont additionnées. Les contrôles recouvrent le volume partagé entre groupes d'un même import et le cumul des plafonds de teneur par catégorie.
- L'import fonctionne en mode `validate` (contrôle sans écriture) ou `create`. Les créations regroupées de TENEUR démarrent `PENDING` ; celles de TRANSFERT démarrent `DRAFT`.
- Les taux d'émission réutilisés lors d'un nouveau mouvement proviennent du détail TIRUERT le plus ancien trouvé pour le lot. Si aucun taux historique n'existe, la création est refusée.
- `CUSTOMS_CORRECTION` porte un ajustement de volume distinct, avec crédit si la correction est positive et débit si elle est négative ; une correction négative ne peut dépasser le volume de l'opération corrigée.
- `REPORT` est un type interne/historique, utilisé notamment par un traitement ponctuel de reliquats pour le passage vers le régime IRICC. Ce traitement crée des opérations acceptées, sur des lots de 2026, avec une année de déclaration 2027. Ne pas extrapoler cette règle temporaire aux créations ordinaires.
- Les commandes `backfill_*`, `repair_operation_categories` et les imports de MAC sont des reprises de données ciblées. Leurs choix de données et valeurs par défaut ne définissent pas nécessairement une règle générale de création.

## 10. Consignes pour faire évoluer les règles

Avant de modifier une règle métier :

1. Identifier le service qui calcule ou valide effectivement la règle ; une vue ou un serializer peut seulement l'orchestrer.
2. Lire le modèle, les consommateurs directs et le test le plus proche. Une formule utilisée à la fois en Python et en ORM doit rester cohérente dans les deux chemins.
3. Déterminer si le changement touche les crédits, les débits, les réservations en attente, les statuts confirmés, l'année de déclaration, la période de durabilité, l'assiette MAC, les objectifs ou les snapshots.
4. Distinguer le comportement pérenne des reprises de données, seeds et traitements ponctuels.
5. Mettre à jour ce README dans le même changement lorsqu'une règle décrite ici change, et ajouter/modifier les tests métier correspondants.

Si une demande métier entre en conflit avec le comportement documenté ou que le code et les tests se contredisent, faire préciser la décision attendue avant de choisir une interprétation. Les valeurs annuelles et leurs sources réglementaires doivent être confirmées avec le métier ; ce README ne leur substitue pas.

## 11. Sources de référence dans le module

- Modèles : [`models/operation.py`](models/operation.py), [`models/operation_detail.py`](models/operation_detail.py), [`models/objective.py`](models/objective.py), [`models/mac_fossil_fuel.py`](models/mac_fossil_fuel.py), [`models/elec_operation.py`](models/elec_operation.py).
- Calculs : [`services/operation.py`](services/operation.py), [`services/balance.py`](services/balance.py), [`services/balance_annotations.py`](services/balance_annotations.py), [`services/teneur.py`](services/teneur.py), [`services/objective.py`](services/objective.py), [`services/objective_snapshot.py`](services/objective_snapshot.py), [`services/elec_balance.py`](services/elec_balance.py).
- Tests : `tests/services/test_operation.py`, `tests/services/test_balance.py`, `tests/services/test_teneur.py`, `tests/services/test_objective.py`, `tests/services/test_elec_balance.py`, `tests/services/test_objective_snapshot.py` et `tests/commands/test_set_operations_expired.py`.