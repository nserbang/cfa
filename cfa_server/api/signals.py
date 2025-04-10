from axes.signals import user_locked_out
from rest_framework.exceptions import PermissionDenied
from django.dispatch import receiver
from django.contrib.auth import user_logged_in, user_logged_out
from django.contrib.auth.models import User
from api.models import LoggedInUser
import logging

logger = logging.getLogger(__name__)

@receiver(user_logged_in)
def on_user_logged_in(sender, request, **kwargs):
    logger.info("Entering on_user_logged_in")
    user = kwargs.get("user")
    logger.info(f"User logging in: {user.username if user else 'Unknown'}")
    
    try:
        logged_in_user, created = LoggedInUser.objects.get_or_create(user=user)
        if created:
            logger.info(f"Created new LoggedInUser record for {user.username}")
        else:
            logger.info(f"Found existing LoggedInUser record for {user.username}")
    except Exception as e:
        logger.error(f"Error creating LoggedInUser record: {str(e)}")
        raise
    
    logger.info("Exiting on_user_logged_in")


@receiver(user_logged_out)
def on_user_logged_out(sender, **kwargs):
    logger.info("Entering on_user_logged_out")
    user = kwargs.get("user")
    logger.info(f"User logging out: {user.username if user else 'Unknown'}")
    
    try:
        deleted_count = LoggedInUser.objects.filter(user=user).delete()[0]
        logger.info(f"Deleted {deleted_count} LoggedInUser records for {user.username}")
    except Exception as e:
        logger.error(f"Error deleting LoggedInUser records: {str(e)}")
        raise
    
    logger.info("Exiting on_user_logged_out")


@receiver(user_locked_out)
def raise_permission_denied(*args, **kwargs):
    logger.info("Entering raise_permission_denied")
    logger.warning("User locked out due to too many failed login attempts")
    
    if 'request' in kwargs:
        request = kwargs['request']
        logger.warning(f"Locked out IP: {request.META.get('REMOTE_ADDR')}")
        if request.POST.get('username'):
            logger.warning(f"Attempted username: {request.POST.get('username')}")
    
    logger.info("Exiting raise_permission_denied")
    raise PermissionDenied("Too many failed login attempts")
