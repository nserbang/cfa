from axes.signals import user_locked_out
from rest_framework.exceptions import PermissionDenied
from django.dispatch import receiver
from django.contrib.auth import user_logged_in, user_logged_out
from django.contrib.auth.models import User
from api.models import LoggedInUser


@receiver(user_logged_in)
def on_user_logged_in(sender, request, **kwargs):
    LoggedInUser.objects.get_or_create(user=kwargs.get("user"))


@receiver(user_logged_out)
def on_user_logged_out(sender, **kwargs):
    LoggedInUser.objects.filter(user=kwargs.get("user")).delete()


@receiver(user_locked_out)
def raise_permission_denied(*args, **kwargs):
    raise PermissionDenied("Too many failed login attempts")
