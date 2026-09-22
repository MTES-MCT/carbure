from collections import defaultdict

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


class UniqueInListSerializer(serializers.ListSerializer):
    unique_fields = []

    def to_internal_value(self, data):
        attrs = super().to_internal_value(data)
        errors = [{} for _ in attrs]
        message = _("Cette valeur est déjà utilisée ailleurs dans le fichier.")

        for name in self.unique_fields:
            seen = defaultdict(list)
            for i, row in enumerate(attrs):
                value = row.get(name)
                if value not in (None, ""):
                    seen[value].append(i)

            for indexes in seen.values():
                if len(indexes) > 1:
                    for i in indexes:
                        errors[i][name] = [message]

        if any(errors):
            raise serializers.ValidationError(errors)
        return attrs
