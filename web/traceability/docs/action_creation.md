# Création des actions : flow et validation

Chaque filière déclare les créations possibles dans son handler. Un lien de `action_creation_flow` contient l'état du parent et l'état initial de l'enfant :

```python
class H2ActionHandler(ActionIndustryHandler):
    action_creation_flow = (
        (None, (Action.INIT, ActionStatus.PENDING)),
        ((Action.INIT, ActionStatus.PENDING), (Action.VALORIZE, ActionStatus.CREATED)),
    )
```

Un état est un couple `(type, statut)`. `None` désigne une création sans parent. Le premier lien correspondant au couple `(type, status)` demandé et à l'état courant du parent est utilisé ; sans lien, la création est refusée.

## Validation du flow

`ActionAuthorizationSerializer` résout `parent`, `type`, `status` et `holder`, vérifie la filière du parent et recherche le lien de création. Le statut initial est obligatoire et doit correspondre à un statut connu et au lien demandé.

## Validation par type d'action

Le handler associe chaque type à son serializer de création. Par défaut :

```python
action_creation_serializers = {
    Action.INIT: ConsumptionSerializer,
}
```

Une filière peut déclarer sa propre map pour ajouter des types ou remplacer un serializer ; les autres entrées par défaut restent disponibles. Le serializer sélectionné valide les champs propres à l'action. Les valeurs résolues par `ActionAuthorizationSerializer` sont fournies séparément à la sauvegarde.

## Autorisation du statut initial

`action_status_authorizations` associe chaque type d'action à des groupes de statuts et à leurs prédicats `(actor: Entity, holder: Entity, parent_holder: Entity | None) -> bool`.

`get_action_status_authorizations()` déplie les groupes de statuts et fusionne la configuration d'`ActionIndustryHandler` avec celle de la classe courante, pour produire un dictionnaire `{type: {statut: prédicat}}`. Une règle de filière remplace la règle de base pour le même couple `(type, statut)` ; les autres règles restent disponibles. Par exemple, une règle de base sur `(PENDING, ACCEPTED)` et une surcharge sur `(PENDING,)` conservent la règle de base pour `ACCEPTED`.

Lors de sa validation, `ActionAuthorizationSerializer` appelle le prédicat avec, dans cet ordre, l'entité appelante, le détenteur de l'action à créer et le détenteur du parent (`None` sans parent). La création est refusée si aucune règle ne correspond ou si le prédicat renvoie `False`.

## Création par l'API

Pour `POST /api/traceability/actions/?entity_id=…&industry=H2` :

La requête doit inclure `type`, `status` et `holder`, ainsi que `parent` si nécessaire et les données propres au type d'action. Par exemple, une création H2 sans parent demande `"type": "INIT"` et `"status": "PENDING"`.

1. Le handler est choisi selon `industry` et sa permission d'écriture est vérifiée.
2. `ActionAuthorizationSerializer` vérifie le lien, la filière du parent et le prédicat d'autorisation pour le type et le statut initial demandés.
3. Le serializer associé au type valide les données de l'action.
4. L'action et son statut initial sont enregistrés dans une même transaction. La réponse `201` contient l'action créée.

Aujourd'hui, seul `INIT` possède un serializer de création. Le lien `VALORIZE` est déclaré, mais ne dispose pas encore de serializer ; la permission d'écriture H2 ne permet pas non plus aux administrateurs d'utiliser ce `POST`. L'import Excel et les actions d'administration suivent leurs propres chemins.
