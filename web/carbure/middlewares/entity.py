from core.entity_context import clear_current_entity, set_current_entity
from core.models import Entity


class EntityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        entity_id = request.POST.get("entity_id", request.GET.get("entity_id")) or None
        entity = None

        # Clear any previous entity context
        clear_current_entity()

        if entity_id and entity_id.isdigit():
            try:
                entity = Entity.all_objects.get(id=entity_id)
            except Entity.DoesNotExist:
                pass

        # Store entity in thread-local for automatic filtering
        set_current_entity(entity)
        request.entity = entity

        response = self.get_response(request)

        # Clean up thread-local after request
        clear_current_entity()

        return response
