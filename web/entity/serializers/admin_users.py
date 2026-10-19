import re

from rest_framework import serializers

from core.models import Entity, UserRights


class AdminEntityIdsSerializer(serializers.Serializer):
    entity_ids = serializers.CharField(required=False, allow_blank=True)

    def validate_entity_ids(self, value):
        if not value:
            return None
        return [int(token) for token in re.findall(r"\d+", value)]


class AdminUserRowSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email")
    is_active = serializers.BooleanField(source="user.is_active")
    entity_name = serializers.CharField(source="entity.name")
    entity_type = serializers.ChoiceField(choices=Entity.ENTITY_TYPES, source="entity.entity_type")
    role = serializers.ChoiceField(choices=UserRights.ROLES)

    class Meta:
        model = UserRights
        fields = ["user_id", "email", "is_active", "entity_id", "entity_name", "entity_type", "role"]
