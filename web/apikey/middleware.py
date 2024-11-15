from django.utils.deprecation import MiddlewareMixin
from rest_framework.authentication import get_authorization_header


class RemoveSessionIfAPIKeyAuthMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        auth_header = get_authorization_header(request).decode("utf-8")
        if auth_header and auth_header.startswith("Api-Key"):
            response.delete_cookie("sessionid")
        return response
