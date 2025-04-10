from api.view_includes import *
from api.utl import local_update
import decimal
import logging
logger = logging.getLogger(__name__)
from django.db.models.functions import Cast
from django.db.models import F, FloatField
from geopy.distance import distance

# Views for Police Stations
class PoliceStationViewSet(viewsets.ViewSet):
    def list(self,request):
        logger.info("Entering list")
        try:
            ps = PoliceStation.objects.all()
            logger.info("All police stations retrieved")
        except PoliceStation.DoesNotExist:
            logger.warning("PoliceStation not found")
            return JsonResponse({"message": "PoliceStation not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)

        name = request.query_params.get('name')
        if name:
            logger.info(f"Filtering police stations by name: {name}")
            ps = ps.filter(Q(name__icontains=name))
        serialized = PoliceStationSerializer(ps,many= True)

        data = serialized.data
        lat = long = None
        lat_str = request.query_params.get('lat')
        if lat_str is not None:
            try:
                lat = decimal.Decimal(lat_str)
                logger.info(f"Latitude from query params: {lat}")
            except decimal.InvalidOperation:
                logger.warning(f"Invalid latitude value: {lat_str}")
                lat = None
        long_str = request.query_params.get('long')
        if long_str is not None:
            try:
                long = decimal.Decimal(long_str)
                logger.info(f"Longitude from query params: {long}")
            except decimal.InvalidOperation:
                logger.warning(f"Invalid longitude value: {long_str}")
                long = None

        if lat is not None and long is not None:
            for x in data:
                x1 = x['lat']
                x2 = x['long']
                p1 = (x1,x2)
                p2 = (lat,long)
                x['distance'] =  distance(p1,p2).km
                logger.info(f"Distance calculated between {p1} and {p2}: {x['distance']} km")
        logger.info("Exiting list")
        return JsonResponse(serialized.data, safe=False, status=HTTPStatus.OK)

    def create(self, request):
        logger.info("Entering create")
        try:
            serializer = PoliceStationSerializer(data=json.loads(request.data))
            if serializer.is_valid():
                ps  = PoliceStation(**serializer.validated_data)
                ps.save()
                serialized = PoliceStationSerializer(ps)
                logger.info("Police station created successfully")
                return JsonResponse(serialized.data, status = HTTPStatus.OK)
            else:
                logger.warning(f"Serializer is not valid: {serializer.errors}")
                return JsonResponse({"message": "Police Station not saved"}, status=HTTPStatus.BAD_REQUEST)
        except json.JSONDecodeError as e:
            logger.error(f"JSONDecodeError: {e}")
            return JsonResponse({"message": "Invalid JSON"}, status=HTTPStatus.BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Unexpected error during police station creation: {e}")
            return JsonResponse({"message": "Police Station not saved due to an error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        finally:
            logger.info("Exiting create")

    def update(self, request, pk= None ):
        logger.info("Entering update")
        pid = pk
        logger.info(f"Police station ID to update: {pid}")
        try:
            ps = PoliceStation.objects.get(pk = pid)
            logger.info(f"Police station with ID {pid} retrieved")
        except PoliceStation.DoesNotExist:
            logger.warning(f"Police Station with pk={pid} not found")
            return JsonResponse({"message": "Police Station not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)

        try:
            serializer = PoliceStationSerializer(ps, data= json.loads(request.data), partial = True)
            if serializer.is_valid():
                serializer.save()
                serialized = PoliceStationSerializer(ps)
                logger.info("Police station updated successfully")
                return JsonResponse(serialized.data, status=HTTPStatus.ACCEPTED)
            else:
                logger.warning(f"Serializer is not valid: {serializer.errors}")
                return JsonResponse(serializer.errors, status=HTTPStatus.BAD_REQUEST)
        except json.JSONDecodeError as e:
            logger.error(f"JSONDecodeError: {e}")
            return JsonResponse({"message": "Invalid JSON"}, status=HTTPStatus.BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Unexpected error during police station update: {e}")
            return JsonResponse({"message": "Police Station not updated due to an error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        finally:
            logger.info("Exiting update")

    def partial_update(self, request, pk= None ):
        logger.info("Entering partial_update")
        pid = pk
        logger.info(f"Police station ID to partially update: {pid}")
        try:
            ps = PoliceStation.objects.get(pk = pid)
            logger.info(f"Police station with ID {pid} retrieved")
        except PoliceStation.DoesNotExist:
            logger.warning(f"PoliceStation with pk={pid} not found")
            return JsonResponse({"message": "PoliceStation not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)

        try:
            serializer = PoliceStationSerializer(ps, data= json.loads(request.data), partial = True)
            if serializer.is_valid():
                serializer.save()
                serialized = PoliceStationSerializer(ps)
                logger.info("Police station partially updated successfully")
                return JsonResponse(serialized.data, status=HTTPStatus.ACCEPTED)
            else:
                logger.warning(f"Serializer is not valid: {serializer.errors}")
                return JsonResponse(serializer.errors, status=HTTPStatus.BAD_REQUEST)
        except json.JSONDecodeError as e:
            logger.error(f"JSONDecodeError: {e}")
            return JsonResponse({"message": "Invalid JSON"}, status=HTTPStatus.BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Unexpected error during police station partial update: {e}")
            return JsonResponse({"message": "PoliceStation not updated due to an error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        finally:
            logger.info("Exiting partial_update")

    def destroy(self, request, pk = None):
        logger.info("Entering destroy")
        pid = pk
        logger.info(f"Police station ID to delete: {pid}")
        try:
            ps = PoliceStation.objects.get(pk=pid)
            logger.info(f"Police station with ID {pid} retrieved")
            ps.delete()
            logger.info("Police station deleted successfully")
        except PoliceStation.DoesNotExist:
            logger.warning(f"PoliceStation with pk={pid} not found")
            return JsonResponse({"message": "PoliceStation not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Unexpected error during police station deletion: {e}")
            return JsonResponse({"message": "PoliceStation not deleted due to an error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        finally:
            logger.info("Exiting destroy")

    def retrieve(self, request, pk = None):
        logger.info("Entering retrieve")
        pid = pk
        logger.info(f"Police station ID to retrieve: {pid}")
        try:
            ps = PoliceStation.objects.get(pk=pid)
            logger.info(f"Police station with ID {pid} retrieved")
        except PoliceStation.DoesNotExist:
            logger.warning(f"PoliceStation with pk={pid} not found")
            return JsonResponse({"message": "PoliceStation not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        serialized = PoliceStationSerializer(ps)
        logger.info("Exiting retrieve")
        return JsonResponse(serialized.data, status=200)

# View cor Police Station Contact
class PoliceStationContactViewSet(viewsets.ViewSet):
    def list(self,request):
        logger.info("Entering list")
        try:
            pid = request.query_params.get('station_id')
            if pid is not None:
                logger.info(f"Filtering contacts by station_id: {pid}")
                psc = PoliceStationContact.objects.filter(pid = pid)
            else:
                psc = PoliceStationContact.objects.all()
                logger.info("All police station contacts retrieved")
        except PoliceStationContact.DoesNotExist:
            logger.warning("PoliceStationContact not found")
            return JsonResponse({"message": "PoliceStationContact not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        serialized = PoliceStationContactSerializer(psc,many= True)
        logger.info("Exiting list")
        return JsonResponse(serialized.data, safe=False, status=HTTPStatus.OK)

    def create(self, request):
        logger.info("Entering create")
        try:
            serializer = PoliceStationContactSerializer(data=json.loads(request.data))
            if serializer.is_valid():
                psc  = PoliceStationContact(**serializer.validated_data)
                psc.save()
                serialized = PoliceStationContactSerializer(psc)
                logger.info("Police station contact created successfully")
                return JsonResponse(serialized.data, status = HTTPStatus.OK)
            else:
                logger.warning(f"Serializer is not valid: {serializer.errors}")
                return JsonResponse({"message": "PoliceStationContact not saved"}, status=HTTPStatus.BAD_REQUEST)
        except json.JSONDecodeError as e:
            logger.error(f"JSONDecodeError: {e}")
            return JsonResponse({"message": "Invalid JSON"}, status=HTTPStatus.BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Unexpected error during police station contact creation: {e}")
            return JsonResponse({"message": "PoliceStationContact not saved due to an error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        finally:
            logger.info("Exiting create")

    def update(self, request, pk = None):
        logger.info("Entering update")
        cid =pk
        logger.info(f"Police station contact ID to update: {cid}")
        try:
            psc = PoliceStationContact.objects.get(pk = cid)
            logger.info(f"Police station contact with ID {cid} retrieved")
        except PoliceStationContact.DoesNotExist:
            logger.warning(f"PoliceStationContact with pk={cid} not found")
            return JsonResponse({"message": "PoliceStationContact not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)

        try:
            serializer = PoliceStationContactSerializer(psc, data= json.loads(request.data), partial = True)
            if serializer.is_valid():
                serializer.save()
                serialized = PoliceStationContactSerializer(psc)
                logger.info("Police station contact updated successfully")
                return JsonResponse(serialized.data, status=HTTPStatus.ACCEPTED)
            else:
                logger.warning(f"Serializer is not valid: {serializer.errors}")
                return JsonResponse(serializer.errors, status=HTTPStatus.BAD_REQUEST)
        except json.JSONDecodeError as e:
            logger.error(f"JSONDecodeError: {e}")
            return JsonResponse({"message": "Invalid JSON"}, status=HTTPStatus.BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Unexpected error during police station contact update: {e}")
            return JsonResponse({"message": "PoliceStationContact not updated due to an error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        finally:
            logger.info("Exiting update")

    def partial_update(self, request, pk = None):
        logger.info("Entering partial_update")
        cid =pk
        logger.info(f"Police station contact ID to partially update: {cid}")
        try:
            psc = PoliceStationContact.objects.get(pk = cid)
            logger.info(f"Police station contact with ID {cid} retrieved")
        except PoliceStationContact.DoesNotExist:
            logger.warning(f"PoliceStationContact with pk={cid} not found")
            return JsonResponse({"message": "PoliceStationContact not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)

        try:
            serializer = PoliceStationContactSerializer(psc, data= json.loads(request.data), partial = True)
            if serializer.is_valid():
                serializer.save()
                serialized = PoliceStationContactSerializer(psc)
                logger.info("Police station contact partially updated successfully")
                return JsonResponse(serialized.data, status=HTTPStatus.ACCEPTED)
            else:
                logger.warning(f"Serializer is not valid: {serializer.errors}")
                return JsonResponse(serializer.errors, status=HTTPStatus.BAD_REQUEST)
        except json.JSONDecodeError as e:
            logger.error(f"JSONDecodeError: {e}")
            return JsonResponse({"message": "Invalid JSON"}, status=HTTPStatus.BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Unexpected error during police station contact partial update: {e}")
            return JsonResponse({"message": "PoliceStationContact not updated due to an error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        finally:
            logger.info("Exiting partial_update")

    def destroy(self, request, cid):
        logger.info("Entering destroy")
        logger.info(f"Police station contact ID to delete: {cid}")
        try:
            psc = PoliceStationContact.objects.get(pk=cid)
            logger.info(f"Police station contact with ID {cid} retrieved")
            psc.delete()
            logger.info("Police station contact deleted successfully")
        except PoliceStationContact.DoesNotExist:
            logger.warning(f"PoliceStationContact with pk={cid} not found")
            return JsonResponse({"message": "PoliceStationContact not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Unexpected error during police station contact deletion: {e}")
            return JsonResponse({"message": "PoliceStationContact not deleted due to an error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        finally:
            logger.info("Exiting destroy")
        return JsonResponse({"message": "PoliceStationContact deleted"}, status=HTTPStatus.OK)

    def retrieve(self, request, pk = None):
        logger.info("Entering retrieve")
        logger.info(f"Police station contact ID to retrieve: {pk}")
        try:
            psc = PoliceStationContact.objects.get(pk=pk)
            logger.info(f"Police station contact with ID {pk} retrieved")
        except PoliceStationContact.DoesNotExist:
            logger.warning(f"PoliceStationContact with pk={pk} not found")
            return JsonResponse({"message": "PoliceStationContact not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        serialized = PoliceStationContactSerializer(psc)
        logger.info("Exiting retrieve")
        return JsonResponse(serialized.data, status=200)


# Views for Police Officers
class PoliceOfficerViewSet(viewsets.ViewSet):
    def list(self,request):
        logger.info("Entering list")
        try:
            pid = request.query_params.get('station_id')
            if pid is not None:
                logger.info(f"Filtering police officers by station_id: {pid}")
                pos = PoliceOfficer.objects.filter(pid = pid)
            else:
                pos = PoliceOfficer.objects.all()
                logger.info("All police officers retrieved")
        except PoliceOfficer.DoesNotExist:
            logger.warning("PoliceOfficer not found")
            return JsonResponse({"message": "PoliceOfficer not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        serialized = PoliceOfficerSerializer(pos,many= True)
        logger.info("Exiting list")
        return JsonResponse(serialized.data, safe=False, status=HTTPStatus.OK)

    def create(self, request):
        logger.info("Entering create")
        try:
            serializer = PoliceOfficerSerializer(data=json.loads(request.data))
            if serializer.is_valid():
                po  = PoliceOfficer(**serializer.validated_data)
                po.save()
                serialized = PoliceOfficerSerializer(po)
                logger.info("Police officer created successfully")
                return JsonResponse(serialized.data, status = HTTPStatus.OK)
            else:
                logger.warning(f"Serializer is not valid: {serializer.errors}")
                return JsonResponse({"message": "PoliceOfficer not saved"}, status=HTTPStatus.BAD_REQUEST)
        except json.JSONDecodeError as e:
            logger.error(f"JSONDecodeError: {e}")
            return JsonResponse({"message": "Invalid JSON"}, status=HTTPStatus.BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Unexpected error during police officer creation: {e}")
            return JsonResponse({"message": "PoliceOfficer not saved due to an error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        finally:
            logger.info("Exiting create")

    def update(self, request, pk = None):
        logger.info("Entering update")
        oid = pk
        logger.info(f"Police officer ID to update: {oid}")
        try:
            po = PoliceOfficer.objects.get(pk = oid)
            logger.info(f"Police officer with ID {oid} retrieved")
        except PoliceOfficer.DoesNotExist:
            logger.warning(f"Police Officer with pk={oid} not found")
            return JsonResponse({"message": "Police Officer not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)

        try:
            serializer = PoliceOfficerSerializer(po, data= json.loads(request.data), partial = True)
            if serializer.is_valid():
                serializer.save()
                serialized = PoliceOfficerSerializer(po)
                logger.info("Police officer updated successfully")
                return JsonResponse(serialized.data, status=HTTPStatus.ACCEPTED)
            else:
                logger.warning(f"Serializer is not valid: {serializer.errors}")
                return JsonResponse(serializer.errors, status=HTTPStatus.BAD_REQUEST)
        except json.JSONDecodeError as e:
            logger.error(f"JSONDecodeError: {e}")
            return JsonResponse({"message": "Invalid JSON"}, status=HTTPStatus.BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Unexpected error during police officer update: {e}")
            return JsonResponse({"message": "PoliceOfficer not updated due to an error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        finally:
            logger.info("Exiting update")

    def partial_update(self, request, pk = None):
        logger.info("Entering partial_update")
        oid = pk
        logger.info(f"Police officer ID to partially update: {oid}")
        try:
            po = PoliceOfficer.objects.get(pk = oid)
            logger.info(f"Police officer with ID {oid} retrieved")
        except PoliceOfficer.DoesNotExist:
            logger.warning(f"Police Officer with pk={oid} not found")
            return JsonResponse({"message": "Police Officer not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)

        try:
            serializer = PoliceOfficerSerializer(po, data= json.loads(request.data), partial = True)
            if serializer.is_valid():
                serializer.save()
                serialized = PoliceOfficerSerializer(po)
                logger.info("Police officer partially updated successfully")
                return JsonResponse(serialized.data, status=HTTPStatus.ACCEPTED)
            else:
                logger.warning(f"Serializer is not valid: {serializer.errors}")
                return JsonResponse(serializer.errors, status=HTTPStatus.BAD_REQUEST)
        except json.JSONDecodeError as e:
            logger.error(f"JSONDecodeError: {e}")
            return JsonResponse({"message": "Invalid JSON"}, status=HTTPStatus.BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Unexpected error during police officer partial update: {e}")
            return JsonResponse({"message": "PoliceOfficer not updated due to an error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        finally:
            logger.info("Exiting partial_update")

    def destroy(self, request, pk = None):
        logger.info("Entering destroy")
        oid = pk
        logger.info(f"Police officer ID to delete: {oid}")
        try:
            po = PoliceOfficer.objects.get(pk=oid)
            logger.info(f"Police officer with ID {oid} retrieved")
            po.delete()
            logger.info("Police officer deleted successfully")
        except PoliceOfficer.DoesNotExist:
            logger.warning(f"Police Officer with pk={oid} not found")
            return JsonResponse({"message": "Police Officer not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Unexpected error during police officer deletion: {e}")
            return JsonResponse({"message": "PoliceOfficer not deleted due to an error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        finally:
            logger.info("Exiting destroy")

    def retrieve(self, request, pk = None):
        logger.info("Entering retrieve")
        logger.info(f"Police officer ID to retrieve: {pk}")
        try:
            po = PoliceOfficer.objects.get(pk=pk)
            logger.info(f"Police officer with ID {pk} retrieved")
        except PoliceOfficer.DoesNotExist:
            logger.warning(f"Police Officer with pk={pk} not found")
            return JsonResponse({"message": "Police Officer not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        serialized = PoliceOfficerSerializer(po)
        logger.info("Exiting retrieve")
        return JsonResponse(serialized.data, status=200)