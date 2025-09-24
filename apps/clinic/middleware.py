# app/clinic/middleware.py
import jwt
from django.conf import settings
from types import SimpleNamespace
SECRET_KEY = "npnm9VN8koi4qLdLJi3hMMmfGPDKVHsaK0UPFevkAFejMsP6UJIWdCpQzhUI7GB4"
ALGORITHM = "HS256"

from django.http import JsonResponse

import jwt
from django.http import JsonResponse

SECRET_KEY = "npnm9VN8koi4qLdLJi3hMMmfGPDKVHsaK0UPFevkAFejMsP6UJIWdCpQzhUI7GB4"
ALGORITHM = "HS256"

EXEMPT_PATHS = [
    "/admin",       # Django admin
    "/api/docs",     # drf-yasg swagger UI
    "/redoc",       # drf-yasg redoc UI
    "/api/schema",  # drf-spectacular schema
    "/auth/login",  # login endpoint
]

class JWTMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        if any(path.startswith(exempt) for exempt in EXEMPT_PATHS):
            return self.get_response(request)

        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header.startswith("Bearer "):
            return JsonResponse({"detail": "No credentials"}, status=401)

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            request.user_id = payload["user_id"]
            request.role = payload["role"]
        except jwt.ExpiredSignatureError:
            return JsonResponse({"detail": "Token expired"}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({"detail": "Invalid token"}, status=401)

        return self.get_response(request)


# class JWTUserMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response
#         self.secret =  settings.SECRET_KEY

#     def __call__(self, request):
#         auth = request.META.get("HTTP_AUTHORIZATION", "")
#         if auth.startswith("Bearer "):
#             token = auth.split(" ", 1)[1]
#             try:
#                 payload = jwt.decode(token, self.secret, algorithms=["HS256"])
#                 # create simple user-like object with id and role
#                 request.user = SimpleNamespace(id=payload.get("id") or payload.get("user_id"), role=payload.get("role"), is_authenticated=True)
#             except Exception:
#                 request.user = SimpleNamespace(id=None, role=None, is_authenticated=False)
#         else:
#             request.user = SimpleNamespace(id=None, role=None, is_authenticated=False)
#         return self.get_response(request)


# clinic_service/middleware.py
# import jwt
# from django.conf import settings
# from django.http import JsonResponse

# SECRET_KEY = "npnm9VN8koi4qLdLJi3hMMmfGPDKVHsaK0UPFevkAFejMsP6UJIWdCpQzhUI7GB4"
# ALGORITHM = "HS256"

# class JWTMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         auth_header = request.META.get("HTTP_AUTHORIZATION")
#         if auth_header is None or not auth_header.startswith("Bearer "):
#             return JsonResponse({"detail": "Authentication credentials were not provided."}, status=401)

#         token = auth_header.split(" ")[1]

#         try:
#             payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#             request.user_id = payload["user_id"]
#             request.role = payload["role"]
#         except jwt.ExpiredSignatureError:
#             return JsonResponse({"detail": "Token has expired."}, status=401)
#         except jwt.InvalidTokenError:
#             return JsonResponse({"detail": "Invalid token."}, status=401)

#         return self.get_response(request)
