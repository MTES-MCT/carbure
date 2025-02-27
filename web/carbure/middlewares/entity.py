from core.models import Entity


class EntityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        entity_id = request.POST.get("entity_id", request.GET.get("entity_id"))
        request.entity = None

        if entity_id:
            try:
                request.entity = Entity.objects.get(id=entity_id)
            except Entity.DoesNotExist:
                pass

        return self.get_response(request)
