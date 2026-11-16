from rest_framework import serializers

from core.models import Entity
from traceability.models import Action, ActionStatus
from traceability.serializers.creation.authorization import AUTHORIZATION_FIELDS, validate_authorization
from traceability.serializers.creation.rules import check_quantity
from traceability.serializers.lookups import CertificateLookupField, MaterialLookupField, SiteLookupField


class ActionCreationSerializer(serializers.ModelSerializer):
    """Creation body shared by every action type.

    ``type``, ``status``, ``holder`` and ``parent`` are always validated, even
    when a child replaces ``Meta.fields``. A child lists the payload fields it
    accepts. ``field_checks`` runs for those fields only. A child overrides
    ``check_<field>`` to replace a shared rule, or extends ``field_checks`` to
    add one. A check raises a message, not a field dict.
    """

    parent = serializers.PrimaryKeyRelatedField(queryset=Action.objects.all(), required=False, allow_null=True)
    type = serializers.ChoiceField(choices=Action.TYPES)
    status = serializers.ChoiceField(choices=ActionStatus.STATUSES)
    holder = serializers.PrimaryKeyRelatedField(queryset=Entity.objects.all())
    material = MaterialLookupField(required=False, allow_null=True)
    certificate = CertificateLookupField(required=False, allow_null=True)
    site = SiteLookupField(required=False, allow_null=True)

    class Meta:
        model = Action
        fields = ["type", "status", "holder", "parent", "material", "certificate", "site"]

    def get_field_names(self, declared_fields, info):
        names = [name for name in super().get_field_names(declared_fields, info) if name not in AUTHORIZATION_FIELDS]
        return [*AUTHORIZATION_FIELDS, *names]

    def field_checks(self):
        return {"quantity": self.check_quantity}

    def check_quantity(self, quantity, attrs):
        return check_quantity(quantity, attrs.get("parent"))

    def validate(self, attrs):
        validate_authorization(attrs, self.context)
        errors = {}
        for field, check in self.field_checks().items():
            if field not in attrs:
                continue
            try:
                attrs[field] = check(attrs[field], attrs)
            except serializers.ValidationError as exc:
                errors[field] = exc.detail
        if errors:
            raise serializers.ValidationError(errors)
        return attrs

    def create(self, validated_data):
        validated_data.pop("status", None)
        validated_data["industry"] = self.context["handler"].industry
        return super().create(validated_data)


class ActionCreateRequestSerializer(ActionCreationSerializer):
    """Schema of the create body. The view validates with the type serializer.

    ``working_date`` is left out: the server fills it. ``industry`` comes from
    the query param. ``pos_id`` follows the model until it becomes optional.
    """

    class Meta(ActionCreationSerializer.Meta):
        fields = [
            "pos_id",
            "material",
            "certificate",
            "quantity",
            "site",
            "shipping_date",
            "shipping_distance",
            "shipping_method",
            "file",
            "eec",
            "el",
            "ei",
            "ep",
            "etd",
            "eu",
            "eccs",
            "esca",
            "eccr",
        ]
