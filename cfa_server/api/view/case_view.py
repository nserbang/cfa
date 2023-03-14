
from api.view_includes import *

class CaseViewSet(viewsets.ViewSet):
    def list(self,request):        
        try:
            cs = Case.objects.all()
        except Case.DoesNotExist:
            return JsonResponse({"message": "Case not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)        
        
        name = request.query_params.get('search')
        if name:
            print(" Got value :",name)
            cs = cs.filter(Q(name__icontains=name))
        serialized = CaseSerializer(cs,many= True)
        return JsonResponse(serialized.data, safe=False) 

    def create(self, request):             
        serializer = CaseSerializer(data=json.loads(request.data))
        if serializer.is_valid():
            cs  = Case(**serializer.validated_data)
            cs.save()            
            serialized = CaseSerializer(cs)
            return JsonResponse(serialized.data, status = HTTPStatus.OK)
        return JsonResponse({"message": "Case not saved"}, status=HTTPStatus.BAD_REQUEST)
    
    def update(self, request, pk = None):     
        cid = pk
        try:
            cs = Case.objects.get(pk = cid)            
        except Case.DoesNotExist:
            return JsonResponse({"message": "Case not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)            
        serializer = CaseSerializer(cs, data= json.loads(request.data), partial = True)
        if serializer.is_valid():         
            serializer.save()
            serialized = CaseSerializer(cs)
            return JsonResponse(serialized.data, status=HTTPStatus.ACCEPTED)
        return JsonResponse(serializer.errors, status=HTTPStatus.BAD_REQUEST)
    
    def destroy(self, request, pk = None):
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
        cid = pk
        try:
            cs = Case.objects.get(pk=did)
        except Case.DoesNotExist:
            return JsonResponse({"message": "Case not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        serialized = CaseSerializer(cs)
        return JsonResponse(serialized.data, status=200)
    
class CaseHistoryViewSet(viewsets.ViewSet):
    def list(self,request):
        try:
            ch = CaseHistory.objects.all()
        except CaseHistory.DoesNotExist:
            return JsonResponse({"message": "CaseHistory not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)        
        serialized = CaseHistorySerializer(ch,many= True)
        return JsonResponse(serialized.data, safe=False) 

    def create(self, request):            
        serializer = CaseHistorySerializer(data=json.loads(request.data))
        if serializer.is_valid():
            ch  = CaseHistory(**serializer.validated_data)
            ch.save()            
            serialized = CaseHistorySerializer(ch)
            return JsonResponse(serialized.data, status = HTTPStatus.OK)
        return JsonResponse({"message": "CaseHistory not saved"}, status=HTTPStatus.BAD_REQUEST)
    
    def update(self, request, pk = None): 
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
        try:
            md = Media.objects.all()
        except Media.DoesNotExist:
            return JsonResponse({"message": "Media not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)        
        serialized = MediaSerializer(md,many= True)
        return JsonResponse(serialized.data, safe=False) 

    def create(self, request):     
        serializer = MediaSerializer(data=json.loads(request.data))
        if serializer.is_valid():
            md  = Media(**serializer.validated_data)
            md.save()            
            serialized = MediaSerializer(md)
            return JsonResponse(serialized.data, status = HTTPStatus.OK)
        return JsonResponse({"message": "Media not saved"}, status=HTTPStatus.BAD_REQUEST)
    
    def update(self, request, pk = None):
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
        try:
            lv = LostVehicle.objects.all()
        except LostVehicle.DoesNotExist:
            return JsonResponse({"message": "Lost Vehicle not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)        
        serialized = LostVehicleSerializer(lv,many= True)
        return JsonResponse(serialized.data, safe=False) 

    def create(self, request):        
        serializer = LostVehicleSerializer(data=json.loads(request.data))
        if serializer.is_valid():
            lv  = LostVehicle(**serializer.validated_data)
            lv.save()            
            serialized = LostVehicleSerializer(lv)
            return JsonResponse(serialized.data, status = HTTPStatus.OK)
        return JsonResponse({"message": "LostVehicle not saved"}, status=HTTPStatus.BAD_REQUEST)
    
    def update(self, request, pk = None):
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
    
    def partial_update(self, request, pk = None):
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
        caseId  = pk 
        try:
            lv = LostVehicle.objects.get(pk=caseId)
            lv.delete()
        except LostVehicle.DoesNotExist:
            return JsonResponse({"message": "LostVehicle not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        return JsonResponse({"message": "LostVehicle deleted"}, status=HTTPStatus.OK)
    
    def retrieve(self, request, caseId):
        try:
            lv = LostVehicle.objects.get(pk=caseId)
        except LostVehicle.DoesNotExist:
            return JsonResponse({"message": "LostVehicle not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        serialized = LostVehicleSerializer(lv)
        return JsonResponse(serialized.data, status=200)
