from api.view_includes import *
import logging
logger = logging.getLogger(__name__)

class DistrictViewSet(viewsets.ViewSet):
    def list(self,request):
        logger.info("Entering list")
        try:
            queryset = District.objects.all()
            logger.info("All districts retrieved")
        except District.DoesNotExist:
            logger.warning("District not found")
            return JsonResponse({"message": "District not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)

        name = request.query_params.get('name')
        if name:
            logger.info(f"Filtering districts by name: {name}")
            queryset = queryset.filter(Q(name__icontains=name))
        serialized = DistrictSerializer(queryset,many= True)
        logger.info("Exiting list")
        return JsonResponse(serialized.data, safe=False, status =HTTPStatus.OK)

    def create(self, request):
        logger.info("Entering create")
        try:
            serializer = DistrictSerializer(data=json.loads(request.data))
            if serializer.is_valid():
                district  = District(**serializer.validated_data)
                district.save()
                serialized = DistrictSerializer(district)
                logger.info("District created successfully")
                return JsonResponse(serialized.data, status = HTTPStatus.OK)
            else:
                logger.warning(f"Serializer is not valid: {serializer.errors}")
                return JsonResponse({"message": "District not saved"}, status=HTTPStatus.BAD_REQUEST)
        except json.JSONDecodeError as e:
            logger.error(f"JSONDecodeError: {e}")
            return JsonResponse({"message": "Invalid JSON"}, status=HTTPStatus.BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Unexpected error during district creation: {e}")
            return JsonResponse({"message": "District not saved due to an error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        finally:
            logger.info("Exiting create")

    def update(self, request, pk = None):
        logger.info("Entering update")
        did = pk
        logger.info(f"District ID to update: {did}")
        try:
            district = District.objects.get(pk = did)
            logger.info(f"District with ID {did} retrieved")
        except District.DoesNotExist:
            logger.warning(f"District with pk={did} not found")
            return JsonResponse({"message": "District not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)

        try:
            serializer = DistrictSerializer(district, data= json.loads(request.data), partial = True)
            if serializer.is_valid():
                serializer.save()
                serialized = DistrictSerializer(district)
                logger.info("District updated successfully")
                return JsonResponse(serialized.data, status=HTTPStatus.ACCEPTED)
            else:
                logger.warning(f"Serializer is not valid: {serializer.errors}")
                return JsonResponse(serializer.errors, status=HTTPStatus.BAD_REQUEST)
        except json.JSONDecodeError as e:
            logger.error(f"JSONDecodeError: {e}")
            return JsonResponse({"message": "Invalid JSON"}, status=HTTPStatus.BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Unexpected error during district update: {e}")
            return JsonResponse({"message": "District not updated due to an error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        finally:
            logger.info("Exiting update")

    def partial_update(self, request, pk = None):
        logger.info("Entering partial_update")
        did = pk
        logger.info(f"District ID to partially update: {did}")
        try:
            district = District.objects.get(pk = did)
            logger.info(f"District with ID {did} retrieved")
        except District.DoesNotExist:
            logger.warning(f"District with pk={did} not found")
            return JsonResponse({"message": "District not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)

        try:
            serializer = DistrictSerializer(district, data= json.loads(request.data), partial = True)
            if serializer.is_valid():
                serializer.save()
                serialized = DistrictSerializer(district)
                logger.info("District partially updated successfully")
                return JsonResponse(serialized.data, status=HTTPStatus.ACCEPTED)
            else:
                logger.warning(f"Serializer is not valid: {serializer.errors}")
                return JsonResponse(serializer.errors, status=HTTPStatus.BAD_REQUEST)
        except json.JSONDecodeError as e:
            logger.error(f"JSONDecodeError: {e}")
            return JsonResponse({"message": "Invalid JSON"}, status=HTTPStatus.BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Unexpected error during district partial update: {e}")
            return JsonResponse({"message": "District not updated due to an error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        finally:
            logger.info("Exiting partial_update")

    def destroy(self, request, pk = None):
        logger.info("Entering destroy")
        did = pk
        logger.info(f"District ID to delete: {did}")
        try:
            district = District.objects.get(pk=did)
            logger.info(f"District with ID {did} retrieved")
            district.delete()
            logger.info("District deleted successfully")
        except District.DoesNotExist:
            logger.warning(f"District with pk={did} not found")
            return JsonResponse({"message": "District not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Unexpected error during district deletion: {e}")
            return JsonResponse({"message": "District not deleted due to an error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        finally:
            logger.info("Exiting destroy")

    def retrieve(self, request, pk=None):
        logger.info("Entering retrieve")
        did = pk
        logger.info(f"District ID to retrieve: {did}")
        try:
            district = District.objects.get(did=pk)
            logger.info(f"District with ID {did} retrieved")
        except District.DoesNotExist:
            logger.warning(f"District with did={pk} not found")
            return JsonResponse({"message": "District not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)

        serialized = DistrictSerializer(district)
        logger.info("Exiting retrieve")
        return JsonResponse(serialized.data, status=200)