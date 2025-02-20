from api.view_includes import *
from api.utl import local_update
#from geopy import distance
from api.log import log
import decimal
from django.db.models.functions import Cast
""" from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point """
from django.db.models import F, FloatField
from geopy.distance import distance
#from geopy.distance import geodesic
# Views for Police Stations
class PoliceStationViewSet(viewsets.ViewSet):
    
    """ def calculate_distance(self, lat1, lon1, lat2, lon2):
        # convert coordinates to geopy format
        point1 = (lat1, lon1)
        point2 = (lat2, lon2)
        print(" P1 ",point1, " P2 ",point2)
        
        # calculate distance using Haversine formula
        try:
            return distance.distance(point1, point2).km
        except Exception as e:
            print(" ERROR ",e.args) """
    
    def list(self,request):
        log.info("ENTERED")      
        try:
            ps = PoliceStation.objects.all()            
        except PoliceStation.DoesNotExist:
            return JsonResponse({"message": "PoliceStation not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)  
        name = request.query_params.get('name')
        if name:           
            ps = ps.filter(Q(name__icontains=name))
        serialized = PoliceStationSerializer(ps,many= True)

        data = serialized.data
        lat = long = None
        lat_str = request.query_params.get('lat')
        if lat_str is not None:
            lat = decimal.Decimal(lat_str)
        long_str = request.query_params.get('long')
        if long_str is not None:
            long = decimal.Decimal(long_str)
           
        if lat is not None and long is not None:
            for x in data:
                x1 = x['lat']
                x2 = x['long']
                p1 = (x1,x2)
                p2 = (lat,long)
                x['distance'] =  distance(p1,p2).km
        return JsonResponse(serialized.data, safe=False) 

    def create(self, request):
        serializer = PoliceStationSerializer(data=json.loads(request.data))
        if serializer.is_valid():
            ps  = PoliceStation(**serializer.validated_data)
            ps.save()
            serialized = PoliceStationSerializer(ps)
            return JsonResponse(serialized.data, status = HTTPStatus.OK)
        return JsonResponse({"message": "Police Station not saved"}, status=HTTPStatus.BAD_REQUEST)
    
    def update(self, request, pk= None ):     
        pid = pk
        try:
            ps = PoliceStation.objects.get(pk = pid)
        except PoliceStation.DoesNotExist:
            return JsonResponse({"message": "Police Station not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)            
        serializer = PoliceStationSerializer(ps, data= json.loads(request.data), partial = True)
        if serializer.is_valid():
            serializer.save()
            serialized = PoliceStationSerializer(ps)
            return JsonResponse(serialized.data, status=HTTPStatus.ACCEPTED)
        return JsonResponse(serializer.errors, status=HTTPStatus.BAD_REQUEST)
    
    def partial_update(self, request, pk= None ):     
        pid = pk
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
    
    def destroy(self, request, pk = None):
        pid = pk
        try:
            ps = PoliceStation.objects.get(pk=pid)
            ps.delete()
        except PoliceStation.DoesNotExist:
            return JsonResponse({"message": "PoliceStation not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        return JsonResponse({"message": "PoliceStation deleted"}, status=HTTPStatus.OK)
    
    def retrieve(self, request, pk = None):
        pid = pk
        try:
            ps = PoliceStation.objects.get(pk=pid)
        except PoliceStation.DoesNotExist:
            return JsonResponse({"message": "PoliceStation not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        serialized = PoliceStationSerializer(ps)
        """ 
        lat = long = None
        lat_str = request.query_params.get('lat')
        if lat_str is not None:
            lat = decimal.Decimal(lat_str)
        long_str = request.query_params.get('long')
        if long_str is not None:
            long = decimal.Decimal(long_str)
        data = serialized.data   
        if lat is not None and long is not None:
            print(" Raw Data :::: ",serialized.data['distance'])
             #data['lat']                              
            x1 = data['lat']
            x2 = data['long']
            p1 = (x1,x2)
            p2 = (lat,long)
            print(" P1 : ",p1, " P2 :",p2)
            serialized.data['distance'] =  distance(p1,p2).km
            print(" dist : ",distance(p1,p2).km)
            print(" Calculated Data :::: ",serialized.data['distance']) """
        return JsonResponse(serialized.data, status=200)

# View cor Police Station Contact
class PoliceStationContactViewSet(viewsets.ViewSet):
    def list(self,request):
        try:
            pid = request.query_params.get('station_id')
            if pid is not None:
                psc = PoliceStationContact.objects.filter(pid = pid)
            else:
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
    
    def update(self, request, pk = None):
        cid =pk
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
    
    def partial_update(self, request, pk = None):
        cid =pk     
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
    def destroy(self, request, cid):
        try:
            psc = PoliceStationContact.objects.get(pk=cid)
            psc.delete()
        except PoliceStationContact.DoesNotExist:
            return JsonResponse({"message": "PoliceStationContact not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        return JsonResponse({"message": "PoliceStationContact deleted"}, status=HTTPStatus.OK)
    
    def retrieve(self, request, pk = None):
        try:
            psc = PoliceStationContact.objects.get(pk=pk)
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
            pid = request.query_params.get('station_id')
            if pid is not None:
                pos = PoliceOfficer.objects.filter(pid = pid)
            else:
                pos = PoliceOfficer.objects.all()
            #pos = PoliceOfficer.objects.all()
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
    
    def update(self, request, pk = None):
        oid = pk     
        try:
            po = PoliceOfficer.objects.get(pk = oid)            
        except PoliceOfficer.DoesNotExist:
            return JsonResponse({"message": "Police Officer not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)            
        serializer = PoliceOfficerSerializer(po, data= json.loads(request.data), partial = True)
        #serializers = 
        if serializer.is_valid():
            #district = serializer.data
            serializer.save()
            serialized = PoliceOfficerSerializer(po)
            return JsonResponse(serialized.data, status=HTTPStatus.ACCEPTED)
        return JsonResponse(serializer.errors, status=HTTPStatus.BAD_REQUEST)
    
    def partial_update(self, request, pk = None):
        oid = pk     
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
    
    def destroy(self, request, pk = None):
        oid = pk        
        try:
            po = PoliceOfficer.objects.get(pk=oid)
            po.delete()
        except PoliceOfficer.DoesNotExist:
            return JsonResponse({"message": "Police Officer not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        return JsonResponse({"message": "Police Officer deleted"}, status=HTTPStatus.OK)
    
    def retrieve(self, request, pk = None):
        #oid = pk
        try:
            po = PoliceOfficer.objects.get(pk=pk)
        except PoliceOfficer.DoesNotExist:
            return JsonResponse({"message": "Police Officer not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        serialized = PoliceOfficerSerializer(po)
        return JsonResponse(serialized.data, status=200)