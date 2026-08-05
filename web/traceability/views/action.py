from django.db.models import Q
from rest_framework import viewsets

from core.permissions import HasEntityReadRights, HasEntityWriteRights
from traceability.models import Action
from traceability.serializers import ActionSerializer
from traceability.serializers.action import ActionInputSerializer


class ActionViewset(viewsets.ModelViewSet):
    queryset = Action.objects.all()
    serializer_class = ActionSerializer
    permission_classes = [HasEntityReadRights]
    search_fields = ["pos_id"]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [HasEntityWriteRights()]
        return super().get_permissions()

    def get_queryset(self):
        return self.queryset.filter(Q(holder=self.request.entity) | Q(parent__holder=self.request.entity))

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["entity"] = getattr(self.request, "entity", None)
        return context

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ActionInputSerializer
        return ActionSerializer
