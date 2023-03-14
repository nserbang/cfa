
""" from django.shortcuts import render
from http import HTTPStatus
from datetime import datetime
from rest_framework import viewsets
from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from django.core.exceptions import ValidationError
from  api.serializers import *
import json 
from functools import partial  """

from api.view_includes import *
from rest_framework.decorators import api_view
class DistrictViewSet(viewsets.ViewSet):   
    def list(self,request):
        try:            
            queryset = District.objects.all()            
        except District.DoesNotExist:
            return JsonResponse({"message": "District not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST) 
        name = request.query_params.get('name')
        if name:           
            queryset = queryset.filter(Q(name__icontains=name))
        serialized = DistrictSerializer(queryset,many= True)
        return JsonResponse(serialized.data, safe=False, status =HTTPStatus.OK)

    def create(self, request):        
        serializer = DistrictSerializer(data=json.loads(request.data))
        if serializer.is_valid():
            district  = District(**serializer.validated_data)
            district.save()            
            serialized = DistrictSerializer(district)
            return JsonResponse(serialized.data, status = HTTPStatus.OK)
        return JsonResponse({"message": "District not saved"}, status=HTTPStatus.BAD_REQUEST)
    
    def update(self, request, pk = None):
        did = pk
        try:
            district = District.objects.get(pk = did)            
        except District.DoesNotExist:
            return JsonResponse({"message": "District not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)            
        serializer = DistrictSerializer(district, data= json.loads(request.data), partial = True)
        if serializer.is_valid():
            serializer.save()
            serialized = DistrictSerializer(district)
            return JsonResponse(serialized.data, status=HTTPStatus.ACCEPTED)
        return JsonResponse(serializer.errors, status=HTTPStatus.BAD_REQUEST)

    def partial_update(self, request, pk = None):
        did = pk     
        try:
            district = District.objects.get(pk = did)            
        except District.DoesNotExist:
            return JsonResponse({"message": "District not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)            
        serializer = DistrictSerializer(district, data= json.loads(request.data), partial = True)
        if serializer.is_valid():
            serializer.save()
            serialized = DistrictSerializer(district)
            return JsonResponse(serialized.data, status=HTTPStatus.ACCEPTED)
        return JsonResponse(serializer.errors, status=HTTPStatus.BAD_REQUEST)
    
    def destroy(self, request, pk = None):
        did = pk
        try:
            district = District.objects.get(pk=did)
            district.delete()
        except District.DoesNotExist:
            return JsonResponse({"message": "District not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        return JsonResponse({"message": "District deleted"}, status=HTTPStatus.OK)
    
    def retrieve(self, request, pk=None):
        try:
            district = District.objects.get(did=pk)
        except District.DoesNotExist:
            return JsonResponse({"message": "District not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        serialized = DistrictSerializer(district)
        return JsonResponse(serialized.data, status=200)