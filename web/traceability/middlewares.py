from django.http import JsonResponse
from rest_framework import status

from traceability.handlers.registry import get_action_handler
from traceability.serializers.action import ActionQuerySerializer


class ActionHandlerMiddleware:
    """Resolve the industry handler and attach it on the Django request.

    Applied per-viewset (see ActionViewset), same pattern as EntityMiddleware:
    `request.handler` lives on the WSGI request so DRF wrappers and clones see it.
    """

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        response = self.process_request(request)
        if response is not None:
            return response
        return self.get_response(request)

    def process_request(self, request):
        serializer = ActionQuerySerializer(data=request.GET)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        request.handler = get_action_handler(serializer.validated_data["industry"])
        return None
