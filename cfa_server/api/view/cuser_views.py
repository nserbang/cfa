from api.view_includes import *
from api.utl import local_update
import logging

logger = logging.getLogger(__name__)

class cUserViewSet(viewsets.ViewSet):
    def create(self, request):
        logger.info("Entering create")
        serializer = cUserSerializer(data=json.loads(request.data))
        
        if serializer.is_valid():
            logger.debug("Serializer validation successful")
            app_user = cUser(**serializer.validated_data)
            username = app_user.username
            flag = True
            token_flag = False
            token = None
            serialized = None
            
            try:
                app_user = cUser.objects.get(username=username)
                logger.warning(f"User already exists with username: {username}")
            except app_user.DoesNotExist:
                flag = False
                logger.info(f"Username {username} is available")
                
            if flag is True:
                logger.info("Exiting create - username already registered")
                return JsonResponse({"error": "username already registered"}, status=HTTPStatus.BAD_REQUEST)
            else:
                app_user = cUser(**serializer.validated_data)
                app_user.is_superuser = False
                app_user.is_staff = False
                app_user.is_active = False
                app_user.save()
                logger.info(f"Created new user: {username}")
                
            try:
                token = Token.objects.create(user=app_user)
                token_flag = True
                logger.info(f"Created token for user: {username}")
            except Exception as e:
                logger.error(f"Token creation error for user {username}: {str(e)}")

            if token_flag == True:
                serialized = cUserSerializer(app_user)
                logger.info(f"Serialized user data for: {username}")
                
            logger.info("Exiting create - successful creation")
            return JsonResponse({
                "token": token.key,
                "user": serialized.data
            }, status=HTTPStatus.CREATED)
            
        logger.warning(f"Serializer validation failed: {serializer.errors}")
        return JsonResponse(serializer.errors, status=HTTPStatus.BAD_REQUEST)
    
    def partial_update(self, request, pk = None):
        logger.info("Entering partial_update")
        username = pk
        logger.debug(f"Attempting to update user: {username}")
        
        try:
            user = cUser.objects.get(username=username)
            logger.info(f"Found user to update: {username}")
        except cUser.DoesNotExist:
            logger.warning(f"User not found: {username}")
            return JsonResponse({"message": "user not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError as e:
            logger.error(f"Validation error for username {username}: {str(e)}")
            return JsonResponse({"message": "invalid user name input"}, status=HTTPStatus.BAD_REQUEST)
                
        try:
            user = local_update(user, json.loads(request.data))
            user.save()
            logger.info(f"Successfully updated user: {username}")
        except Exception as e:
            logger.error(f"Error updating user {username}: {str(e)}")
            return JsonResponse({"message": "update failed"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        
        logger.info("Exiting partial_update - successful update")
        return JsonResponse({"message": "OK"}, status=HTTPStatus.ACCEPTED)

    def cuser_detail(self, request, usrname):
        logger.info("Entering cuser_detail")
        logger.info(f"Requested details for user: {usrname}")
        # ... implementation to be added ...
        logger.info("Exiting cuser_detail")
        pass
