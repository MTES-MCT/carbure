from django.contrib.auth import logout
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response


class UserLogoutAction:
    @extend_schema(
        examples=[
            OpenApiExample(
                "Example response.",
                value={"status": "success"},
                request_only=False,
                response_only=True,
            ),
        ],
    )
    @action(detail=False, methods=["get"], url_path="logout")
    def logout(self, request):
        logout(request)
        return Response({"status": "success"})
