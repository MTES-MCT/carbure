# myapp/spectacular_extensions.py

from drf_spectacular.extensions import OpenApiAuthenticationExtension


class APIKeyAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = "apikey.authentication.APIKeyAuthentication"  # Le chemin complet vers ton authentification
    name = "APIKeyAuth"

    def get_security_definition(self, auto_schema):
        return {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": 'Include your API key in the Authorization header as "Authorization: Api-Key {your_api_key}"',
            "example": "Authorization: Api-Key abc123xyz",
        }
