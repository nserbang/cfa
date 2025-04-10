from rest_framework.permissions import BasePermission
import logging

logger = logging.getLogger(__name__)

class IsAuthenticatedOrWriteOnly(BasePermission):
    def has_permission(self, request, view):
        logger.info("Entering IsAuthenticatedOrWriteOnly.has_permission")
        logger.debug(f"Checking permission for method: {request.method}")
        
        if request.method in ["POST", "PUT", "DELETE"]:
            is_authenticated = request.user.is_authenticated
            logger.info(f"Write operation requested, user authenticated: {is_authenticated}")
            return is_authenticated
            
        logger.info("Read operation requested, permission granted")
        logger.info("Exiting IsAuthenticatedOrWriteOnly.has_permission")
        return True


class IsReadOnly(BasePermission):
    def has_permission(self, request, view):
        logger.info("Entering IsReadOnly.has_permission")
        logger.debug(f"Checking permission for method: {request.method}")
        
        is_read_method = request.method in ["GET", "HEAD", "OPTIONS"]
        logger.info(f"Is read method: {is_read_method}")
        
        logger.info("Exiting IsReadOnly.has_permission")
        return is_read_method


class IsPoliceOfficer(BasePermission):
    def has_permission(self, request, view):
        logger.info("Entering IsPoliceOfficer.has_permission")
        logger.debug(f"Checking permission for user: {request.user}")
        
        is_authenticated = request.user.is_authenticated
        is_police = getattr(request.user, 'is_police', False)
        
        logger.info(f"User authenticated: {is_authenticated}, is police: {is_police}")
        logger.info("Exiting IsPoliceOfficer.has_permission")
        
        return is_authenticated and is_police
