from rest_framework import serializers


class LookupSlugRelatedField(serializers.SlugRelatedField):
    """Resolve related objects from handler lookups, cached on the serializer context.

    The first access for a `lookup` runs `handler.lookups.<lookup>(entity)` once and stores
    `{slug: instance}` on `context["serializer_cache"][lookup]`. Later rows hit that dict.
    """

    def __init__(self, *args, lookup, **kwargs):
        self.lookup = lookup
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        return getattr(self.context["handler"].lookups, self.lookup)(self.context.get("entity"))

    def to_internal_value(self, data):
        try:
            serializer_cache = self.context.setdefault("serializer_cache", {})
            if self.lookup not in serializer_cache:
                serializer_cache[self.lookup] = {
                    getattr(instance, self.slug_field): instance for instance in self.get_queryset()
                }
            return serializer_cache[self.lookup][data]
        except KeyError:
            self.fail("does_not_exist", slug_name=self.slug_field, value=data)
