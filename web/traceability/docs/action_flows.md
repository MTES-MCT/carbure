# Configurer les flows et les autorisations

Chaque filière configure son handler, qui hérite d'`ActionIndustryHandler`. L'exemple ci-dessous reprend la configuration de [`H2ActionHandler`](../../h2/handlers/action.py).

## Déclarer les créations possibles

`action_creation_flow` contient des liens de la forme `(état du parent, état initial de la nouvelle action)`. Un état est un couple `(type, statut)`.

```python
action_creation_flow = [
    (None, (Action.INIT, ActionStatus.PENDING)),
    ((Action.INIT, ActionStatus.PENDING), (Action.VALORIZE, ActionStatus.CREATED)),
]
```

Le premier lien permet de créer une action `INIT` en `PENDING`, sans parent (`None`). Le second permet de créer une action `VALORIZE` en `CREATED`, avec une action `INIT` actuellement en `PENDING` comme parent.

La création est refusée si aucun lien ne correspond exactement au parent, au type et au statut demandés. Le parent doit aussi appartenir à la même filière.

## Définir qui peut attribuer un statut

`action_status_authorizations` associe chaque couple `(type d'action, statut)` à une fonction d'autorisation.

```python
action_status_authorizations = {
    (Action.INIT, ActionStatus.PENDING): is_hrs_holder,
    (Action.INIT, ActionStatus.ACCEPTED): is_h2_admin,
    (Action.INIT, ActionStatus.REJECTED): is_h2_admin,
    (Action.INIT, ActionStatus.BLOCKED): is_h2_admin,
    (Action.VALORIZE, ActionStatus.CREATED): is_h2_admin,
}
```

Ici, une station HRS peut créer sa propre action `INIT` en `PENDING`. Les statuts `ACCEPTED`, `REJECTED` et `BLOCKED` sont réservés à l'administration H2. La création d'une `VALORIZE` en `CREATED` lui est aussi réservée.

Chaque clé est un tuple contenant le type d'action et le statut à attribuer.

La fonction reçoit trois entités : l'entité qui agit, le détenteur de l'action et le détenteur du parent (`None` sans parent). Par exemple, [`is_hrs_holder`](../../h2/handlers/authorization.py) vérifie que l'entité est une station HRS et agit pour elle-même :

```python
def is_hrs_holder(actor, holder, parent_holder):
    return actor.entity_type == Entity.HRS and holder == actor
```

Sans règle pour le couple `(type, statut)`, ou si la fonction renvoie `False`, l'opération est refusée.

## Changer le statut d'une action existante

Une transition est le passage d'un statut à un autre pour une même action. `ActionStatus.TRANSITIONS`, défini dans [`models/action_status.py`](../models/action_status.py), liste les couples `(statut de départ, statut d'arrivée)` possibles, communs à toutes les filières. Par exemple :

```python
# Extrait de ActionStatus.TRANSITIONS :
(PENDING, ACCEPTED),  # Une action en attente peut être acceptée.
(PENDING, REJECTED),  # Une action en attente peut être rejetée.
```

Le changement de statut vérifie deux conditions : le couple demandé figure dans cette liste et la fonction d'autorisation permet d'attribuer le statut d'arrivée.

```python
# Transition existante pour une action INIT en attente :
ActionStatus.can_transition(ActionStatus.PENDING, ActionStatus.ACCEPTED)  # True
# L'autorisation is_h2_admin est ensuite vérifiée pour INIT / ACCEPTED.
```

`action_creation_flow` sert à créer une nouvelle action. Passer une action existante de `PENDING` à `ACCEPTED` conserve la même action et ajoute une entrée à son historique de statuts.

## Permettre la création par l'API

Le flow et l'autorisation ne suffisent pas : le type doit aussi avoir un serializer de création. La base fournit celui d'`INIT` :

```python
action_creation_serializers = {
    Action.INIT: ConsumptionSerializer,
}
```

La filière peut ajouter ou remplacer des serializers ; les autres entrées de base restent disponibles. Actuellement, `VALORIZE` n'a pas de serializer de création, même si son lien figure dans le flow H2.

Les endpoints de création et de changement de statut exigent aussi la `write_permission` du handler. Dans H2, elle vaut actuellement `HasHRSWriteRights` : autoriser `is_h2_admin` dans les règles ne donne donc pas, à lui seul, accès à ces endpoints aux administrateurs.
