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
        print(" \n\nEntered user creation:  \n\n")
        serializer = None
        try:
            serializer = cUserSerializer(data= json.loads(request.data))
        except Exception as e:
            print(" Serialization error : ",e.args)

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
            except AssertionError as e:
                print(" User registration assertion error :",e.args)
            except NoReverseMatch as e:
                print ("No Reverse match exception ",e.args)
            except Exception as e:
                print(" \n\n Exception :",e.args)

            if flag is True:
                return JsonResponse({"error": "username already registered"}, status=HTTPStatus.BAD_REQUEST)
            else:
                #app_user = cUser(**serializer.validated_data)
                app_user.is_superuser = False
                app_user.is_staff = False
                app_user.is_active = False
                #app_user.date_joined = datetime.now()
                app_user.save()
                print("\n\n New User added \n\n")
            try:
                print (" 1111111111111111 error : ")
                token = Token.objects.create(user=app_user)
                token_flag = True
            except AssertionError as e:
                token_flag = True
                print (" Assertion error in token: ",e.args)

            except NoReverseMatch as e:
                print ("No Reverse match exception ",e.args)

            except Exception as e:
                print(" Token Error ",e.args)
 

            if token_flag == True:
                serializer_context = {'request':None}
                try:
                    print (" 222222222222 error : ")
                    serialized = cUserSerializer(app_user,context={'request': None})
                    print (" 3333333333333333333 error : ")
                except NoReverseMatch as e:
                    print (" Reverse error : ",e.args)
                except Exception as e:
                    print (" Serilizing error : ",e.args)

                print (" 44444444444444 error : ")
                return JsonResponse(
                    {
                        "token": token.key,
                        "user": serialized.data
                    }, status=HTTPStatus.CREATED
                )
                print (" 5555555555555 error : ")

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

