from rest_framework.permissions import BasePermission


class IsAuthenticatedOrWriteOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in ["POST", "PUT", "DELETE"]:
            return request.user.is_authenticated
        return True


class IsReadOnly(BasePermission):
    def has_permission(self, request, view):
        # Allow read access for any user
        return request.method in ["GET", "HEAD", "OPTIONS"]


class IsPoliceOfficer(BasePermission):
    def has_permission(self, request, view):
        # Allow read access for any user
        return request.user.is_authenticated and request.user.is_police
