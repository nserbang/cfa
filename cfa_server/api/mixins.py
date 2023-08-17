from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied


class AdminRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_admin:
            raise PermissionDenied("Permission Denied")
        return super().dispatch(request, *args, **kwargs)


class UserMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_authenticated:
            qs = qs.filter(user=self.request.user)
        return qs
