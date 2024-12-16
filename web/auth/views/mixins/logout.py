from django.contrib.auth import logout as django_logout
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response


class UserLogoutAction:
    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(
                response={"status": "success"},
                description="Request successful.",
            ),
        },
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
        django_logout(request)
        return Response({"status": "success"})
