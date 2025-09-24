from rest_framework.permissions import BasePermission
from datetime import timedelta, timezone, datetime

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, "role", None) == "admin"

class IsModerator(BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, "role", None) == "moderator"

class IsDoctor(BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, "role", None) == "doctor"

class IsNurse(BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, "role", None) == "nurse"


class IsVisitor(BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, "role", None) == "visitor"
    
class DoctorOnlyOwnPatientNote(BasePermission):
    """
    For object-level check: doctor can add note only for his patient and only at appointment time window
    """
    def has_permission(self, request, view):
        # top-level creation check handled in view
        return True

    def has_object_permission(self, request, view, obj):
        # obj is Patient instance for object-level check (not used here)
        return False
