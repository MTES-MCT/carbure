class UnitMixin:
    """
    Mixin to manage the unit of measurement (L, MJ, KG) in views.

    This mixin automatically adds the unit to the request via `initialize_request()`
    and to the serializer context via `get_serializer_context()`.

    The unit is determined in the following order:
    1. 'unit' parameter from the request (POST or GET)
    2. Entity's preferred unit (entity.preferred_unit)
    3. Default value: 'l' (liters)
    """

    def initialize_request(self, request, *args, **kwargs):
        """
        Initializes the request by adding the 'unit' attribute.

        The unit is retrieved from request parameters,
        the entity, or defaults to 'l'.
        """
        request = super().initialize_request(request, *args, **kwargs)
        # Get unit from request params or entity preference or default to liters
        entity = getattr(request, "entity", None)
        unit = (
            request.POST.get("unit", request.GET.get("unit")) or (entity.preferred_unit.lower() if entity else None) or "l"
        )
        setattr(request, "unit", unit.lower())
        return request

    def get_serializer_context(self):
        """
        Adds entity_id and unit to the serializer context.
        """
        context = super().get_serializer_context()
        entity = self.request.entity
        context["entity_id"] = entity.id
        if getattr(self.request, "unit", None):
            context["unit"] = self.request.unit
        return context
