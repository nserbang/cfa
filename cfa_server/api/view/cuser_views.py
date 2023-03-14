from api.view_includes import *
from api.utl import local_update
from api.log import *
#import logging

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
    

    
    def partial_update(self, request, pk = None):
        log.info("ENTERED")    
        username = pk
        try:
            user = cUser.objects.get(username = username)            
            for k, v in vars(user).items():
                print(k," : ", v)
            print("\n\n Retrieved user : ",user)  
        except cUser.DoesNotExist:
            log.info("Exiting. User is not found")
            return JsonResponse({"message": "user not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            log.info("Exiting. Validation error")
            return JsonResponse({"message": "invalid user name input"}, status=HTTPStatus.BAD_REQUEST)          
                
        user = local_update(user, json.loads(request.data))       
        user.save()
        log.info("Returning with success")  
        return JsonResponse({"message": "OK"}, status=HTTPStatus.ACCEPTED)

    def cuser_detail(self, request, usrname):
        pass        
