# Création des actions : flow, autorisation et validation

Chaque filière déclare les créations possibles dans son handler. Un lien de `action_creation_flow` contient l'état du parent, l'état initial de l'enfant et la fonction qui autorise l'opération :

```python
class H2ActionHandler(ActionIndustryHandler):
    action_creation_flow = (
        (None, (Action.INIT, ActionStatus.PENDING), can_create_consumption),
        ((Action.INIT, ActionStatus.PENDING), (Action.VALORIZE, ActionStatus.CREATED), can_create_valorization),
    )
```

Un état est un couple `(type, statut)`. `None` désigne une création sans parent. Le premier lien correspondant au type demandé et à l'état courant du parent est utilisé ; sans lien, la création est refusée.

## Autorisation

Une fonction d'autorisation reçoit l'entité appelante, le détenteur du parent et le futur détenteur. Pour une création sans parent, `parent_holder` vaut `None`.

```python
def can_create_consumption(actor, parent_holder, child_holder):
    return actor.entity_type == Entity.HRS and actor == child_holder
```

`ActionAuthorizationSerializer` résout `parent`, `type` et `holder`, vérifie la filière du parent, recherche le lien et appelle sa fonction d'autorisation. Il fournit aussi le statut initial du lien. Une règle absente ou qui renvoie `False` refuse la création.

## Validation par type d'action

Le handler associe chaque type à son serializer de création. Par défaut :

```python
action_creation_serializers = {
    Action.INIT: ConsumptionSerializer,
}
```

Une filière peut déclarer sa propre map pour ajouter des types ou remplacer un serializer ; les autres entrées par défaut restent disponibles. Le serializer sélectionné valide les champs propres à l'action. Les valeurs d'autorisation sont vérifiées séparément et fournies à la sauvegarde.

## Création par l'API

Pour `POST /api/traceability/actions/?entity_id=…&industry=H2` :

1. Le handler est choisi selon `industry` et sa permission d'écriture est vérifiée.
2. Le serializer d'autorisation vérifie le lien et l'acteur.
3. Le serializer associé au type valide les données de l'action.
4. L'action et son statut initial sont enregistrés dans une même transaction. La réponse `201` contient l'action créée.

Aujourd'hui, seul `INIT` possède un serializer de création. Le lien `VALORIZE` est déclaré, mais ne dispose pas encore de serializer ; la permission d'écriture H2 ne permet pas non plus aux administrateurs d'utiliser ce `POST`. L'import Excel et les actions d'administration suivent leurs propres chemins.
