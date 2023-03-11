#from view_includes import *

from django.urls import NoReverseMatch
from api.view.district_views import *
from api.view.police_views import *
from api.view.case_view import *
from django.utils import timezone
from datetime import datetime
from rest_framework.request import Request
class cUserViewSet(viewsets.ViewSet):
    def create(self, request):                   
        serializer = cUserSerializer(data= json.loads(request.data))            
        if serializer.is_valid():           
            app_user = cUser(**serializer.validated_data)
            username = app_user.username
            flag = True
            token_flag = False
            token = None
            serialized = None
            try:
                app_user = cUser.objects.get(username=username)
            except app_user.DoesNotExist:
              flag = False
            if flag is True:
                return JsonResponse({"error": "username already registered"}, status=HTTPStatus.BAD_REQUEST)
            else:
                app_user = cUser(**serializer.validated_data)
                app_user.is_superuser = False
                app_user.is_staff = False
                app_user.is_active = False
                #app_user.date_joined = datetime.now()
                app_user.save()          
            try:
                token = Token.objects.create(user=app_user)
                token_flag = True
            except Exception as e:
                print(" Token Error ",e.args)

            if token_flag == True: 
                    serialized = cUserSerializer(app_user)
            return JsonResponse(
                {
                    "token": token.key,
                        "user": serialized.data
                }, status=HTTPStatus.CREATED
            )
        return JsonResponse(serializer.errors, status=HTTPStatus.BAD_REQUEST)
    
    def update(self, request, username):
        try:
            user = cUser.objects.get(pk = username)
        except cUser.DoesNotExist:
            return JsonResponse({"message": "user not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid user name input"}, status=HTTPStatus.BAD_REQUEST)            
        serializer = cUserSerializer(user, data= json.loads(request.data))
        if serializer.is_valid():
            user.save()            
            serialized = DistrictSerializer(user)
            return JsonResponse(serialized.data, status=HTTPStatus.ACCEPTED)
        return JsonResponse(serializer.errors, status=HTTPStatus.BAD_REQUEST)

    def cuser_detail(self, request, usrname):
        pass        

