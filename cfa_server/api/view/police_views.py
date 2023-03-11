from api.view_includes import *

# Views for Police Stations
class PoliceStationViewSet(viewsets.ViewSet):
    def list(self,request):      
        try:
            ps = PoliceStation.objects.all()
        except PoliceStation.DoesNotExist:
            return JsonResponse({"message": "PoliceStation not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)        
        serialized = PoliceStationSerializer(ps,many= True)
        return JsonResponse(serialized.data, safe=False) 

    def create(self, request):     
        serializer = PoliceStationSerializer(data=json.loads(request.data))
        if serializer.is_valid():
            ps  = PoliceStation(**serializer.validated_data)
            ps.save()            
            serialized = PoliceStationSerializer(ps)
            return JsonResponse(serialized.data, status = HTTPStatus.OK)
        return JsonResponse({"message": "PoliceStation not saved"}, status=HTTPStatus.BAD_REQUEST)
    
    def update(self, request, pid):     
        try:
            ps = PoliceStation.objects.get(pk = pid)            
        except PoliceStation.DoesNotExist:
            return JsonResponse({"message": "PoliceStation not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)            
        serializer = PoliceStationSerializer(ps, data= json.loads(request.data), partial = True)
        if serializer.is_valid():          
            serializer.save()
            serialized = PoliceStationSerializer(ps)
            return JsonResponse(serialized.data, status=HTTPStatus.ACCEPTED)
        return JsonResponse(serializer.errors, status=HTTPStatus.BAD_REQUEST)
    
    def delete(self, request, pid):
        try:
            ps = PoliceStation.objects.get(pk=pid)
            ps.delete()
        except PoliceStation.DoesNotExist:
            return JsonResponse({"message": "PoliceStation not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        return JsonResponse({"message": "PoliceStation deleted"}, status=HTTPStatus.OK)
    
    def retrieve(self, request, pid):
        try:
            ps = District.objects.get(pk=pid)
        except PoliceStation.DoesNotExist:
            return JsonResponse({"message": "PoliceStation not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        serialized = PoliceStationSerializer(ps)
        return JsonResponse(serialized.data, status=200)

# View cor Police Station Contact
class PoliceStationContactViewSet(viewsets.ViewSet):
    def list(self,request):      
        try:
            psc = PoliceStationContact.objects.all()
        except PoliceStationContact.DoesNotExist:
            return JsonResponse({"message": "PoliceStationContact not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)        
        serialized = PoliceStationContactSerializer(psc,many= True)
        return JsonResponse(serialized.data, safe=False) 

    def create(self, request):
        print("\n Entered District Create Method. Data : ",request)        
        serializer = PoliceStationContact(data=json.loads(request.data))
        if serializer.is_valid():
            psc  = PoliceStationContact(**serializer.validated_data)
            psc.save()            
            serialized = PoliceStationContactSerializer(psc)
            return JsonResponse(serialized.data, status = HTTPStatus.OK)
        return JsonResponse({"message": "PoliceStationContact not saved"}, status=HTTPStatus.BAD_REQUEST)
    
    def update(self, request, cid):     
        try:
            psc = PoliceStationContact.objects.get(pk = cid)            
        except PoliceStationContact.DoesNotExist:
            return JsonResponse({"message": "PoliceStationContact not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)            
        serializer = PoliceStationContactSerializer(psc, data= json.loads(request.data), partial = True)
        if serializer.is_valid():
            #district = serializer.data
            serializer.save()
            serialized = PoliceStationContactSerializer(psc)
            return JsonResponse(serialized.data, status=HTTPStatus.ACCEPTED)
        return JsonResponse(serializer.errors, status=HTTPStatus.BAD_REQUEST)
    
    def delete(self, request, cid):
        try:
            psc = PoliceStationContact.objects.get(pk=cid)
            psc.delete()
        except PoliceStationContact.DoesNotExist:
            return JsonResponse({"message": "PoliceStationContact not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        return JsonResponse({"message": "PoliceStationContact deleted"}, status=HTTPStatus.OK)
    
    def retrieve(self, request, cid):
        try:
            psc = PoliceStationContact.objects.get(pk=cid)
        except District.DoesNotExist:
            return JsonResponse({"message": "PoliceStationContact not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        serialized = PoliceStationContactSerializer(psc)
        return JsonResponse(serialized.data, status=200)


# Views for Police Officers 
class PoliceOfficerViewSet(viewsets.ViewSet):
    def list(self,request): 
        try:
            pos = PoliceOfficer.objects.all()
        except PoliceOfficer.DoesNotExist:
            return JsonResponse({"message": "PoliceOfficer not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)        
        serialized = PoliceOfficerSerializer(pos,many= True)
        return JsonResponse(serialized.data, safe=False) 

    def create(self, request):         
        serializer = PoliceOfficerSerializer(data=json.loads(request.data))
        if serializer.is_valid():
            po  = PoliceOfficer(**serializer.validated_data)
            po.save()            
            serialized = PoliceOfficerSerializer(po)
            return JsonResponse(serialized.data, status = HTTPStatus.OK)
        return JsonResponse({"message": "PoliceOfficer not saved"}, status=HTTPStatus.BAD_REQUEST)
    
    def update(self, request, oid):     
        try:
            po = PoliceOfficer.objects.get(pk = oid)            
        except PoliceOfficer.DoesNotExist:
            return JsonResponse({"message": "Police Officer not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)            
        serializer = PoliceOfficerSerializer(po, data= json.loads(request.data), partial = True)
        if serializer.is_valid():
            #district = serializer.data
            serializer.save()
            serialized = PoliceOfficerSerializer(po)
            return JsonResponse(serialized.data, status=HTTPStatus.ACCEPTED)
        return JsonResponse(serializer.errors, status=HTTPStatus.BAD_REQUEST)
    
    def delete(self, request, oid):
        try:
            po = PoliceOfficer.objects.get(pk=oid)
            po.delete()
        except PoliceOfficer.DoesNotExist:
            return JsonResponse({"message": "Police Officer not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        return JsonResponse({"message": "Police Officer deleted"}, status=HTTPStatus.OK)
    
    def retrieve(self, request, oid):
        try:
            po = PoliceOfficer.objects.get(pk=oid)
        except PoliceOfficer.DoesNotExist:
            return JsonResponse({"message": "Police Officer not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        serialized = PoliceOfficerSerializer(po)
        return JsonResponse(serialized.data, status=200)