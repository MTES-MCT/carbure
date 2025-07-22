from django.contrib.auth import update_session_auth_hash
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema, inline_serializer
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import CharField

from auth.serializers import ChangePasswordErrors, ChangePasswordSerializer


class ChangePasswordActionMixin:
    @extend_schema(
        request=ChangePasswordSerializer,
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=inline_serializer(
                    name="ChangePasswordSuccess",
                    fields={"status": CharField(default="success")},
                ),
                description="Mot de passe modifié avec succès",
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=inline_serializer(
                    name="ChangePasswordError",
                    fields={
                        "message": CharField(help_text="Message d'erreur général", required=False),
                        "errors": CharField(help_text="Détails des erreurs de validation", required=False),
                    },
                ),
                description="Erreurs possibles: données invalides, mot de passe actuel incorrect, "
                "nouveau mot de passe invalide",
            ),
        },
        examples=[
            OpenApiExample(
                "Succès",
                value={"status": "success"},
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "Mot de passe actuel incorrect",
                value={
                    "message": ChangePasswordErrors.INVALID_DATA,
                    "errors": {
                        "current_password": [ChangePasswordErrors.WRONG_CURRENT_PASSWORD],
                    },
                },
                response_only=True,
                status_codes=["400"],
            ),
            OpenApiExample(
                "Nouveau mot de passe invalide",
                value={
                    "message": ChangePasswordErrors.INVALID_DATA,
                    "errors": {
                        "new_password": ["Ce mot de passe est trop court. Il doit contenir au minimum 8 caractères."],
                    },
                },
                response_only=True,
                status_codes=["400"],
            ),
            OpenApiExample(
                "Mots de passe identiques",
                value={
                    "message": ChangePasswordErrors.INVALID_DATA,
                    "errors": {
                        "current_password": [ChangePasswordErrors.PASSWORDS_MATCH],
                    },
                },
                response_only=True,
                status_codes=["400"],
            ),
        ],
    )
    @action(detail=False, methods=["post"], url_path="request-password-change")
    def change_password(self, request):
        # Vérification explicite que l'utilisateur est authentifié
        if not request.user.is_authenticated:
            return Response({"detail": "Authentification requise."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            serializer = ChangePasswordSerializer(data=request.data, context={"request": request})

            if not serializer.is_valid():
                return Response(
                    {"message": ChangePasswordErrors.INVALID_DATA, "errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            new_password = serializer.validated_data["new_password"]

            request.user.set_password(new_password)
            request.user.save()

            update_session_auth_hash(request, request.user)

            return Response({"status": "success"}, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback

            traceback.print_exc()
            return Response({"error": f"Erreur interne: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
