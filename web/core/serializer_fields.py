from rest_framework import serializers


class CachedPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    """PrimaryKeyRelatedField resolving instances from a pre-fetched cache instead of one query per value.

    The cache must be a `{pk: instance}` dict provided via the serializer context under `cache_key`.
    This avoids N+1 queries when validating many rows at once (e.g. `many=True` on a large dataset).
    Falls back to the regular per-value queryset lookup if no cache is found in the context, so the
    field remains usable stand-alone (e.g. in isolated tests).
    """

    def __init__(self, *args, cache_key, **kwargs):
        self.cache_key = cache_key
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data):
        cache = self.context.get(self.cache_key)
        if cache is None:
            return super().to_internal_value(data)

        if isinstance(data, bool):
            self.fail("incorrect_type", data_type=type(data).__name__)

        try:
            pk = int(data)
        except (TypeError, ValueError):
            self.fail("incorrect_type", data_type=type(data).__name__)

        try:
            return cache[pk]
        except KeyError:
            self.fail("does_not_exist", pk_value=data)
