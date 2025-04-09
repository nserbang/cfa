
from api.view_includes import *
from api.log import log
from api.utl import local_update
import logging
logger = logging.getLogger(__name__)

class CaseViewSet(viewsets.ViewSet):
    def list(self,request): 
        logger.info("Entering")
        try:
            user1 = request.query_params.get('user')            
            if user1:             
                cs = Case.objects.filter(Q(user = user1))
            else:
                cs = Case.objects.all()
        except Case.DoesNotExist:
            log.info("Exiting")
            return JsonResponse({"message": "Case not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            log.info("Exiting")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)       
        
        serialized = CaseSerializer(cs,many= True)
        log.info("Exiting")
        return JsonResponse(serialized.data, safe=False) 

    def create(self, request):
        logger.info(" Entering")
        #print(" Json : ",json.loads(request.data))             
        serializer = CaseSerializer(data=json.loads(request.data))
        #print(" Error :", serializer.error_messages)
        if serializer.is_valid():
            cs  = Case(**serializer.validated_data)
            cs.save()
            
            serialized = CaseSerializer(cs)
            log.info(" Exiting with success") 
            return JsonResponse(serialized.data, status = HTTPStatus.OK)
        logger.info(" Exiting ") 
        return JsonResponse({"message": "Case not saved"}, status=HTTPStatus.BAD_REQUEST)
    
    def lupdate(self, instance, data):
        logger.info("Entering")
        for field, value in data.items():           
            if field == 'oid':                
                oid = PoliceOfficer.objects.get(pk=value)
                if oid is not None:
                    setattr(instance,field,oid)               
            elif field =='user':                            
                log.error( "User not allowed to change in case")
                #print(" Not police officer")
            elif field =='pid':
                log.info(" Updating police station ")
                ps = PoliceStation.objects.get(pk = value)   
                if ps is not None:                    
                    setattr(instance,field,ps)                
            elif field == 'cstate' or \
            field=='description' or \
            field == 'follow' or \
            field =='type':   
                #pass
                ignore = ['pid','oid','user']
                #, lat, long, description, follow, title, type,':
                local_update(instance,data, ignore )   
        return instance
        #log.info("Exiting")

    def update(self, request, pk = None):       
        logger.info("Entering")  
        cid = pk
        try:
            cs = Case.objects.get(pk = cid)            
        except Case.DoesNotExist:
            log.info("Exiting") 
            return JsonResponse({"message": "Case not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            log.info("Exiting")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        #cs = local_update(cs, json.loads(request.data))            
        #serializer = CaseSerializer(cs, data= json.loads(request.data), partial = True)
        #if serializer.is_valid():         
        # serializer.save()
        # serialized = CaseSerializer(cs)
        # log.info("Exiting with Success")        
        cs = self.lupdate(cs,json.loads(request.data))
        cs.save()
        #serialized = CaseSerializer(cs)
        logger.info("Exiting with OK")
        return JsonResponse({" message:":"OK"}, status=HTTPStatus.ACCEPTED)
        #return JsonResponse(serialized, status=HTTPStatus.ACCEPTED, safe=True)
        #log.info("Exiting")
        #return JsonResponse(serializer.errors, status=HTTPStatus.BAD_REQUEST)
    
    def destroy(self, request, pk = None):
        logger.info("Entering")
        cid = pk
        try:
            cs = Case.objects.get(pk=cid)
            cs.delete()
        except Case.DoesNotExist:
            return JsonResponse({"message": "Case not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        return JsonResponse({"message": "Case deleted"}, status=HTTPStatus.OK)
    
    def retrieve(self, request, pk = None):
        logger.info("Entering") 
        cid = pk
        try:
            cs = Case.objects.get(pk=cid)
        except Case.DoesNotExist:
            logger.info("Exiting")
            return JsonResponse({"message": "Case not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            logger.info("Exiting") 
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        serialized = CaseSerializer(cs)
        logger.info("Exiting with success")
        return JsonResponse(serialized.data, status=200)
    
class CaseHistoryViewSet(viewsets.ViewSet):
    def list(self,request):
        logger.info("Entering")
        try:
            #uid = request
            ch = CaseHistory.objects.all()
        except CaseHistory.DoesNotExist:
            return JsonResponse({"message": "CaseHistory not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)        
        serialized = CaseHistorySerializer(ch,many= True)
        return JsonResponse(serialized.data, safe=False) 

    def create(self, request):   
        logger.info("Entering")         
        serializer = CaseHistorySerializer(data=json.loads(request.data))       
        if serializer.is_valid():           
            ch  = CaseHistory(**serializer.validated_data)
            ch.save()            
            serialized = CaseHistorySerializer(ch)
            log.info("Returning with Success") 
            return JsonResponse(serialized.data, status = HTTPStatus.OK)
        logger.info("Returning with error") 
        return JsonResponse({"message": "CaseHistory not saved"}, status=HTTPStatus.BAD_REQUEST)
    
    def update(self, request, pk = None): 
        logger.info("Entering")
        chid = pk    
        try:
            ch = CaseHistory.objects.get(pk = chid)            
        except CaseHistory.DoesNotExist:
            return JsonResponse({"message": "CaseHistory not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)            
        serializer = CaseHistorySerializer(ch, data= json.loads(request.data), partial = True)
        if serializer.is_valid():            
            serializer.save()
            serialized = CaseHistorySerializer(ch)
            return JsonResponse(serialized.data, status=HTTPStatus.ACCEPTED)
        return JsonResponse(serializer.errors, status=HTTPStatus.BAD_REQUEST)
    
    def partial_update(self, request, pk = None): 
        logger.info("Entering")
        chid = pk    
        try:
            ch = CaseHistory.objects.get(pk = chid)            
        except CaseHistory.DoesNotExist:
            return JsonResponse({"message": "CaseHistory not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)            
        serializer = CaseHistorySerializer(ch, data= json.loads(request.data), partial = True)
        if serializer.is_valid():            
            serializer.save()
            serialized = CaseHistorySerializer(ch)
            return JsonResponse(serialized.data, status=HTTPStatus.ACCEPTED)
        return JsonResponse(serializer.errors, status=HTTPStatus.BAD_REQUEST)
    
    def destroy(self, request, pk = None):
        logger.info("Entering")
        chid = pk
        try:
            ch = CaseHistory.objects.get(pk=chid)
            ch.delete()
        except CaseHistory.DoesNotExist:
            return JsonResponse({"message": "CaseHistory not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        return JsonResponse({"message": "CaseHistory deleted"}, status=HTTPStatus.OK)
    
    def retrieve(self, request, pk = None):
        logger.info("Entering")
        chid = pk
        try:
            ch = CaseHistory.objects.get(pk=chid)
        except CaseHistory.DoesNotExist:
            return JsonResponse({"message": "CaseHistory not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        serialized = CaseHistorySerializer(ch)
        return JsonResponse(serialized.data, status=200)
    
class MediaViewSet(viewsets.ViewSet):
    def list(self,request):
        logger.info("Entering")
        try:
            md = Media.objects.all()
        except Media.DoesNotExist:
            return JsonResponse({"message": "Media not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)        
        serialized = MediaSerializer(md,many= True)
        return JsonResponse(serialized.data, safe=False) 

    def create(self, request):     
        logger.info("Entering")
        log.info("Entering")
        serializer = MediaSerializer(data=json.loads(request.data))
        print(" Media : ",serializer.error_messages, " dd : ",serializer)
        if serializer.is_valid():
            md  = Media(**serializer.validated_data)
            md.save()            
            serialized = MediaSerializer(md)
            return JsonResponse(serialized.data, status = HTTPStatus.OK)
        return JsonResponse({"message": "Media not saved"}, status=HTTPStatus.BAD_REQUEST)
    
    def update(self, request, pk = None):
        logger.info("Entering")
        mid = pk     
        try:
            md = Media.objects.get(pk = mid)            
        except Media.DoesNotExist:
            return JsonResponse({"message": "Media not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)            
        serializer = MediaSerializer(md, data= json.loads(request.data), partial = True)
        if serializer.is_valid():         
            serializer.save()
            serialized = MediaSerializer(md)
            return JsonResponse(serialized.data, status=HTTPStatus.ACCEPTED)
        return JsonResponse(serializer.errors, status=HTTPStatus.BAD_REQUEST)
    
    def destroy(self, request, pk = None):
        logger.info("Entering")
        mid = pk
        try:
            md = Media.objects.get(pk=mid)
            md.delete()
        except Media.DoesNotExist:
            return JsonResponse({"message": "Media not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        return JsonResponse({"message": "Media deleted"}, status=HTTPStatus.OK)
    
    def partial_destroy(self, request, pk = None):
        logger.info("Entering")
        mid = pk
        try:
            md = Media.objects.get(pk=mid)
            md.delete()
        except Media.DoesNotExist:
            return JsonResponse({"message": "Media not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        return JsonResponse({"message": "Media deleted"}, status=HTTPStatus.OK)
    
    def retrieve(self, request, pk):
        mid = pk
        try:
            md = Media.objects.get(pk=mid)
        except Media.DoesNotExist:
            return JsonResponse({"message": "Media not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        serialized = MediaSerializer(md)
        return JsonResponse(serialized.data, status=200)
    
class LostVehicleViewSet(viewsets.ViewSet):
    def list(self,request):
        logger.info("Entering")
        try:
            lv = LostVehicle.objects.all()
        except LostVehicle.DoesNotExist:
            return JsonResponse({"message": "Lost Vehicle not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)        
        serialized = LostVehicleSerializer(lv,many= True)
        return JsonResponse(serialized.data, safe=False) 

    def create(self, request): 
        logger.info("Entering")
        log.info("Entering")       
        serializer = LostVehicleSerializer(data=json.loads(request.data))
        print(" Creating Vehicle :",serializer.error_messages, "\n Values ",serializer, "\n Received :",json.loads(request.data))
        if serializer.is_valid():
            lv  = LostVehicle(**serializer.validated_data)
            lv.save()            
            serialized = LostVehicleSerializer(lv)
            log.info("Exiting with success")   
            return JsonResponse(serialized.data, status = HTTPStatus.OK)
        log.info("Exiting with error")   
        return JsonResponse({"message": "Lost vehicle not saved"}, status=HTTPStatus.BAD_REQUEST)
    
    def update(self, request, pk = None):
        logger.info("Entering")
        log.info(" Entering")
        caseId  = pk             
        try:
            lv = LostVehicle.objects.get(pk = caseId) 
            print(" Vehicle :",lv, " case id ",caseId)           
        except LostVehicle.DoesNotExist:
            log.info(" Exiting with vehicle not found")
            return JsonResponse({"message": "LostVehicle not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            log.info(" Exiting with validation error")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)            
        serializer = LostVehicleSerializer(lv, data= json.loads(request.data), partial = True)
        if serializer.is_valid():           
            serializer.save()
            serialized = LostVehicleSerializer(lv)
            log.info(" Exiting with success")
            return JsonResponse(serialized.data, status=HTTPStatus.ACCEPTED)
        log.info(" Exiting with error")
        return JsonResponse(serializer.errors, status=HTTPStatus.BAD_REQUEST)
    
    def partial_update(self, request, pk = None):
        logger.info("Entering")
        caseId  = pk             
        try:
            lv = LostVehicle.objects.get(pk = caseId)            
        except LostVehicle.DoesNotExist:
            return JsonResponse({"message": "LostVehicle not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)            
        serializer = LostVehicleSerializer(lv, data= json.loads(request.data), partial = True)
        if serializer.is_valid():           
            serializer.save()
            serialized = LostVehicleSerializer(lv)
            return JsonResponse(serialized.data, status=HTTPStatus.ACCEPTED)
        return JsonResponse(serializer.errors, status=HTTPStatus.BAD_REQUEST)
    
    def destroy(self, request, pk = None):
        logger.info("Entering")
        caseId  = pk 
        try:
            lv = LostVehicle.objects.get(pk=caseId)
            lv.delete()
        except LostVehicle.DoesNotExist:
            return JsonResponse({"message": "LostVehicle not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        return JsonResponse({"message": "LostVehicle deleted"}, status=HTTPStatus.OK)
    
    def retrieve(self, request, pk):
        logger.info("Entering")
        #pk = caseId
        try:
            lv = LostVehicle.objects.get(caseId=pk)
        except LostVehicle.DoesNotExist:
            return JsonResponse({"message": "LostVehicle not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        serialized = LostVehicleSerializer(lv)
        return JsonResponse(serialized.data, status=200)

class CommentViewSet(viewsets.ViewSet):
    def list(self,request):
        logger.info("Entering")
        try:
            lv = Comment.objects.all()
        except Comment.DoesNotExist:
            return JsonResponse({"message": "Comments not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)        
        serialized = CommentSerializer(lv,many= True)
        return JsonResponse(serialized.data, safe=False) 

    def create(self, request): 
        logger.info("Entering")       
        serializer = CommentSerializer(data=json.loads(request.data))
        print(" Creating Comment :",serializer.error_messages, "\n Values ",serializer, "\n Received :",json.loads(request.data))
        if serializer.is_valid():
            lv  = Comment(**serializer.validated_data)
            lv.save()            
            serialized = CommentSerializer(lv)
            log.info("Exiting with success")   
            return JsonResponse(serialized.data, status = HTTPStatus.OK)
        log.info("Exiting with error")   
        return JsonResponse({"message": "Comment not saved"}, status=HTTPStatus.BAD_REQUEST)
    
    def update(self, request, pk = None):
        logger.info("Entering ")
        caseId  = pk             
        try:
            lv = Comment.objects.get(pk = caseId) 
            print(" Comment :",lv, " case id ",caseId)           
        except Comment.DoesNotExist:
            log.info(" Exiting with vehicle not found")
            return JsonResponse({"message": "Comment not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            log.info(" Exiting with validation error")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)            
        serializer = LostVehicleSerializer(lv, data= json.loads(request.data), partial = True)
        if serializer.is_valid():           
            serializer.save()
            serialized = CommentSerializer(lv)
            log.info(" Exiting with success")
            return JsonResponse(serialized.data, status=HTTPStatus.ACCEPTED)
        logger.info(" Exiting with error")
        return JsonResponse(serializer.errors, status=HTTPStatus.BAD_REQUEST)
        
    def destroy(self, request, pk = None):
        caseId  = pk 
        try:
            lv = Comment.objects.get(pk=caseId)
            lv.delete()
        except Comment.DoesNotExist:
            return JsonResponse({"message": "Comment not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        return JsonResponse({"message": "Comment deleted"}, status=HTTPStatus.OK)
    
    def retrieve(self, request, pk):
        logger.info("Entering")
        #pk = caseId
        try:
            lv = Comment.objects.get(cmtid=pk)
        except Comment.DoesNotExist:
            return JsonResponse({"message": "LostVehicle not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        serialized = CommentSerializer(lv)
        return JsonResponse(serialized.data, status=200)
