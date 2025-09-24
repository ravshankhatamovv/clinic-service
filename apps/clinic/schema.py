# apps/clinic/schema.py
from drf_spectacular.extensions import OpenApiAuthenticationExtension

class CustomJWTAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = 'apps.clinic.authentication.CustomJWTAuthentication'
    name = 'CustomJWTAuthentication'  

    def get_security_definition(self, auto_schema):
        return {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
        }
