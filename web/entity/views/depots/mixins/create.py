from datetime import datetime

from django.conf import settings
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
)
from rest_framework.decorators import action
from rest_framework.response import Response

from carbure.tasks import background_bulk_sanity_checks, background_bulk_scoring
from core.carburetypes import CarbureSanityCheckErrors
from core.helpers import send_mail
from core.models import CarbureLot, Entity, GenericError
from core.utils import CarbureEnv
from entity.serializers.depot import CreateDepotSerializer
from entity.services.geolocation import get_coordinates


class CreateDepotActionMixin:
    @extend_schema(
        parameters=[
            OpenApiParameter(
                "entity_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Entity ID",
                required=True,
            ),
        ],
        request=CreateDepotSerializer,
        responses={
            200: OpenApiResponse(
                response={"status": "success"},
                description="Request successful.",
            ),
            400: OpenApiResponse(
                response={"message": ""},
                description="Bad request.",
            ),
        },
        examples=[
            OpenApiExample(
                "Success example",
                value={"status": "success"},
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "Bad request",
                value={"message": ""},
                response_only=True,
                status_codes=["400"],
            ),
        ],
    )
    @action(detail=False, methods=["post"], url_path="create-depot")
    def create_depot(self, request):
        entity_id = self.request.query_params.get("entity_id")
        entity = Entity.objects.get(id=entity_id)
        serializer = CreateDepotSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        depot = serializer.save()

        depot.gps_coordinates = get_gps_coordinates(depot)
        depot.save()

        send_email_to_user(entity, depot.name, request)
        send_email_to_dgec(entity, depot.name, request)

        lots = CarbureLot.objects.filter(carbure_client=entity, carbure_delivery_site=depot)
        background_bulk_scoring(lots)
        background_bulk_sanity_checks(lots)
        GenericError.objects.filter(lot__in=lots, error=CarbureSanityCheckErrors.DEPOT_NOT_CONFIGURED).delete()

        return Response({"status": "success"})


def get_gps_coordinates(depot):
    address = depot.address + " " + depot.postal_code + " " + depot.city + ", " + depot.country.name
    xy = get_coordinates(address)
    return f"{xy[0]},{xy[1]}" if xy else None


def send_email_to_user(entity, depot_name, request):
    today = datetime.now().strftime("%d/%m/%Y")
    recipient_list = [request.user.email]
    text_message = f"""
    Bonjour,

    Votre demande de création du dépôt {depot_name} pour la société {entity.name} a bien été enregistrée à la date du {today}.
    L'équipe de la DGEC va étudier votre demande et vous serez notifiés lorsque celle-ci aura été traitée.

    Bien cordialement,
    L'équipe CarbuRe
    """  # noqa: E501

    send_mail(
        request=request,
        subject="[CarbuRe][Demande d’ajout de dépôt enregistrée]",
        message=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
    )


def send_email_to_dgec(entity, depot_name, request):
    today = datetime.now().strftime("%d/%m/%Y")
    recipient_list = ["carbure@beta.gouv.fr"]
    admin_link = f"{CarbureEnv.get_base_url()}/admin/transactions/site/?is_enabled=False"
    text_message = f"""
    Bonjour,

    Une demande de création de dépôt {depot_name} pour la société {entity.name} a été déposé le {today} par l’utilisateur {request.user.email}.

    Veuillez traiter cette demande dans l'interface administrateur de CarbuRe :

    1 - Visualisez la liste des dépôts à valider sur ce lien : {admin_link}
    2 - Selectionnez le dépôt {depot_name}.
    3 - Selectionnez l'action "Valider les dépôts sélectionnés".
    4 - Cliquez sur "Envoyer".

    Bien à vous,
    CarbuRe
    """  # noqa: E501
    send_mail(
        request=request,
        subject="[CarbuRe][Nouvelle demande d’ajout de dépôt enregistrée]",
        message=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
    )
