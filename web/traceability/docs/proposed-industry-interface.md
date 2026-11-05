# Création des actions : flow, autorisation et validation

## Proposition d'API

La filière associe chaque type d’action à son serializer de création. Chaque lien du graphe indique l’état du parent, l’état initial de l’enfant et la règle autorisant l’opération :

```python
class H2ActionHandler(ActionIndustryHandler):
    action_creation_serializers = {
        Action.INIT: ConsumptionSerializer,
        Action.VALORIZE: ValorizeSerializer,
        Action.TRANSFER: TransferSerializer,
    }

    action_flow = (
        ((Action.INIT, ACCEPTED), (Action.VALORIZE, CREATED), can_create_valorization),
        ((Action.VALORIZE, CREATED), (Action.TRANSFER, PENDING), can_transfer_certificate),
        ((Action.TRANSFER, ACCEPTED), (Action.TRANSFER, PENDING), can_retransfer_certificate),
    )
```

À la création d’une action :

1. Le serializer d’autorisation trouve le lien correspondant et vérifie sa règle d’autorisation.
2. Le serializer associé au type d’action valide les données de la requête.
3. L’action est créée avec le statut initial indiqué par le lien.


## Autorisation par lien entre action

La règle reçoit uniquement les trois entités participant à l’opération : l’entité qui appelle l'endpoint de création, le détenteur du parent et le détenteur proposé pour l’enfant. Elle reste ainsi centrée sur leur autorisation ; la validation des données de l’action appartient au serializer.

```python## 
# Un administrateur H2 peut attribuer un certificat de fourniture à un consommateur d'H2.
def can_create_valorization(actor, parent_holder, child_holder):
    actor_is_admin = actor.entity_type == Entity.ADMIN
    actor_is_h2_admin = actor.has_external_admin_rights("H2")
    recipient_is_h2_consumer = child_holder.entity_type in H2_CONSUMERS
    
    return (actor_is_admin or actor_is_h2_admin) and recipient_is_h2_consumer


# Un redevable peut retransférer ses propres certificats à un autre redevable.
def can_retransfer_certificate(actor, parent_holder, child_holder):
    actor_is_holder = actor == parent_holder
    sender_is_liable = parent_holder.is_tiruert_liable
    recipient_is_liable = child_holder.is_tiruert_liable
    
    return actor_is_holder and sender_is_liable and recipient_is_liable
```


## Serializer d'autorisation

Ce serializer générique est utilisé par le handler pour une création. Il résout l'action parente et le holder proposés, puis vérifie le lien et sa règle d’autorisation avant la validation propre à l’action :

```python
class ActionAuthorizationSerializer(serializers.Serializer):
    parent = ParentActionField()
    type = ActionTypeField()
    holder = EntityField()

    def validate(self, attrs):
        parent = attrs["parent"]
        holder = attrs["holder"]
        actor = self.context["entity"]
        handler = self.context["handler"]

        edge = find_action_flow(handler.action_flow, parent, attrs["type"])
        if edge is None or not edge.check(actor, parent.holder, holder):
            raise serializers.ValidationError("Opération non autorisée.")

        attrs["initial_status"] = edge.child_status
        return attrs
```

Les champs et la fonction de recherche ci-dessus illustrent l’interface envisagée. Le serializer de création de l’action est ensuite exécuté sur les données de la requête.


## Serializer propre à un type d'action

Chaque type d’action dispose d’un serializer de création. Il définit les champs que l’utilisateur peut renseigner, valide les données et peut imposer des valeurs sur la nouvelle action.

```python
class TransferSerializer(serializers.ModelSerializer):
    quantity = serializers.DecimalField(
        max_digits=13,
        decimal_places=3,
        min_value=Decimal("0.001"),
    )

    class Meta:
        model = Action
        fields = ["parent", "holder", "quantity", "working_date"]

    def validate(self, attrs):
        parent = attrs["parent"]
        holder = attrs["holder"]

        if holder == parent.holder:
            raise serializers.ValidationError("Le destinataire doit être différent du détenteur actuel.")

        attrs["type"] = Action.TRANSFER
        return attrs
```

