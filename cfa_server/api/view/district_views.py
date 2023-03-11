
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
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name']    
    def list(self,request):
        print(" Entering list::: ")
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
    
    def update(self, request, did):     
        try:
            district = District.objects.get(pk = did)            
        except District.DoesNotExist:
            return JsonResponse({"message": "District not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)            
        serializer = DistrictSerializer(district, data= json.loads(request.data), partial = True)
        if serializer.is_valid():
            #district = serializer.data
            serializer.save()
            serialized = DistrictSerializer(district)
            return JsonResponse(serialized.data, status=HTTPStatus.ACCEPTED)
        return JsonResponse(serializer.errors, status=HTTPStatus.BAD_REQUEST)
    
    def delete(self, request, did):
        try:
            district = District.objects.get(pk=did)
            district.delete()
        except District.DoesNotExist:
            return JsonResponse({"message": "District not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        return JsonResponse({"message": "District deleted"}, status=HTTPStatus.OK)
    
    def retrieve(self, request, did):
        try:
            district = District.objects.get(pk=did)
        except District.DoesNotExist:
            return JsonResponse({"message": "District not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError:
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        serialized = DistrictSerializer(district)
        return JsonResponse(serialized.data, status=200)