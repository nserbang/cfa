from api.view_includes import *
from api.utl import local_update
import logging
logger = logging.getLogger(__name__)

class CaseViewSet(viewsets.ViewSet):
    def list(self,request):
        logger.info("Entering list")
        try:
            user1 = request.query_params.get('user')
            logger.info(f"User ID from query parameters: {user1}")
            if user1:
                cs = Case.objects.filter(Q(user = user1))
                logger.info(f"Cases filtered by user: {user1}")
            else:
                cs = Case.objects.all()
                logger.info("All cases retrieved")
        except Case.DoesNotExist:
            logger.warning("Case not found")
            return JsonResponse({"message": "Case not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)

        serialized = CaseSerializer(cs,many= True)
        logger.info("Exiting list")
        return JsonResponse(serialized.data, safe=False)

    def create(self, request):
        logger.info("Entering create")
        try:
            serializer = CaseSerializer(data=json.loads(request.data))
            if serializer.is_valid():
                cs  = Case(**serializer.validated_data)
                cs.save()

                serialized = CaseSerializer(cs)
                logger.info("Exiting create with success")
                return JsonResponse(serialized.data, status = HTTPStatus.OK)
            else:
                logger.warning(f"Serializer is not valid: {serializer.errors}")
                return JsonResponse({"message": "Case not saved"}, status=HTTPStatus.BAD_REQUEST)
        except json.JSONDecodeError as e:
            logger.error(f"JSONDecodeError: {e}")
            return JsonResponse({"message": "Invalid JSON"}, status=HTTPStatus.BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Unexpected error during case creation: {e}")
            return JsonResponse({"message": "Case not saved due to an error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        finally:
            logger.info("Exiting create")

    def lupdate(self, instance, data):
        logger.info("Entering lupdate")
        for field, value in data.items():
            logger.info(f"Processing field: {field} with value: {value}")
            if field == 'oid':
                try:
                    oid = PoliceOfficer.objects.get(pk=value)
                    if oid is not None:
                        setattr(instance,field,oid)
                        logger.info(f"Updated oid to {value}")
                except PoliceOfficer.DoesNotExist:
                    logger.error(f"PoliceOfficer with pk={value} not found")
            elif field =='user':
                logger.error( "User not allowed to change in case")
            elif field =='pid':
                logger.info("Updating police station")
                try:
                    ps = PoliceStation.objects.get(pk = value)
                    if ps is not None:
                        setattr(instance,field,ps)
                        logger.info(f"Updated pid to {value}")
                    else:
                        logger.warning(f"PoliceStation with pk={value} is None")
                except PoliceStation.DoesNotExist:
                    logger.error(f"PoliceStation with pk={value} not found")
            elif field == 'cstate' or \
            field=='description' or \
            field == 'follow' or \
            field =='type':
                ignore = ['pid','oid','user']
                local_update(instance,data, ignore )
                logger.info(f"Updated field {field} using local_update")
        logger.info("Exiting lupdate")
        return instance

    def update(self, request, pk = None):
        logger.info("Entering update")
        cid = pk
        logger.info(f"Case ID to update: {cid}")
        try:
            cs = Case.objects.get(pk = cid)
        except Case.DoesNotExist:
            logger.warning(f"Case with pk={cid} not found")
            return JsonResponse({"message": "Case not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)

        try:
            cs = self.lupdate(cs,json.loads(request.data))
            cs.save()
            logger.info("Case updated successfully")
            return JsonResponse({" message:":"OK"}, status=HTTPStatus.ACCEPTED)
        except json.JSONDecodeError as e:
            logger.error(f"JSONDecodeError: {e}")
            return JsonResponse({"message": "Invalid JSON"}, status=HTTPStatus.BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Unexpected error during case update: {e}")
            return JsonResponse({"message": "Case not updated due to an error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        finally:
            logger.info("Exiting update")

    def destroy(self, request, pk = None):
        logger.info("Entering destroy")
        cid = pk
        logger.info(f"Case ID to delete: {cid}")
        try:
            cs = Case.objects.get(pk=cid)
            cs.delete()
            logger.info("Case deleted successfully")
        except Case.DoesNotExist:
            logger.warning(f"Case with pk={cid} not found")
            return JsonResponse({"message": "Case not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Unexpected error during case deletion: {e}")
            return JsonResponse({"message": "Case not deleted due to an error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        finally:
            logger.info("Exiting destroy")
        return JsonResponse({"message": "Case deleted"}, status=HTTPStatus.OK)

    def retrieve(self, request, pk = None):
        logger.info("Entering retrieve")
        cid = pk
        logger.info(f"Case ID to retrieve: {cid}")
        try:
            cs = Case.objects.get(pk=cid)
        except Case.DoesNotExist:
            logger.warning(f"Case with pk={cid} not found")
            return JsonResponse({"message": "Case not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)

        serialized = CaseSerializer(cs)
        logger.info("Exiting retrieve with success")
        return JsonResponse(serialized.data, status=200)

class CaseHistoryViewSet(viewsets.ViewSet):
    def list(self,request):
        logger.info("Entering list")
        try:
            ch = CaseHistory.objects.all()
        except CaseHistory.DoesNotExist:
            logger.warning("CaseHistory not found")
            return JsonResponse({"message": "CaseHistory not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)

        serialized = CaseHistorySerializer(ch,many= True)
        logger.info("Exiting list")
        return JsonResponse(serialized.data, safe=False)

    def create(self, request):
        logger.info("Entering create")
        try:
            serializer = CaseHistorySerializer(data=json.loads(request.data))
            if serializer.is_valid():
                ch  = CaseHistory(**serializer.validated_data)
                ch.save()

                serialized = CaseHistorySerializer(ch)
                logger.info("Exiting create with Success")
                return JsonResponse(serialized.data, status = HTTPStatus.OK)
            else:
                logger.warning(f"Serializer is not valid: {serializer.errors}")
                return JsonResponse({"message": "CaseHistory not saved"}, status=HTTPStatus.BAD_REQUEST)
        except json.JSONDecodeError as e:
            logger.error(f"JSONDecodeError: {e}")
            return JsonResponse({"message": "Invalid JSON"}, status=HTTPStatus.BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Unexpected error during CaseHistory creation: {e}")
            return JsonResponse({"message": "CaseHistory not saved due to an error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        finally:
            logger.info("Exiting create")

    def update(self, request, pk = None):
        logger.info("Entering update")
        chid = pk
        logger.info(f"CaseHistory ID to update: {chid}")
        try:
            ch = CaseHistory.objects.get(pk = chid)
            serializer = CaseHistorySerializer(ch, data= json.loads(request.data), partial = True)
            if serializer.is_valid():
                serializer.save()
                serialized = CaseHistorySerializer(ch)
                logger.info("CaseHistory updated successfully")
                return JsonResponse(serialized.data, status=HTTPStatus.ACCEPTED)
            else:
                logger.warning(f"Serializer is not valid: {serializer.errors}")
                return JsonResponse(serializer.errors, status=HTTPStatus.BAD_REQUEST)
        except CaseHistory.DoesNotExist:
            logger.warning(f"CaseHistory with pk={chid} not found")
            return JsonResponse({"message": "CaseHistory not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        except json.JSONDecodeError as e:
            logger.error(f"JSONDecodeError: {e}")
            return JsonResponse({"message": "Invalid JSON"}, status=HTTPStatus.BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Unexpected error during CaseHistory update: {e}")
            return JsonResponse({"message": "CaseHistory not updated due to an error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        finally:
            logger.info("Exiting update")

    def partial_update(self, request, pk = None):
        logger.info("Entering partial_update")
        chid = pk
        logger.info(f"CaseHistory ID to partially update: {chid}")
        try:
            ch = CaseHistory.objects.get(pk = chid)
        except CaseHistory.DoesNotExist:
            logger.warning(f"CaseHistory with pk={chid} not found")
            return JsonResponse({"message": "CaseHistory not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)

        try:
            serializer = CaseHistorySerializer(ch, data= json.loads(request.data), partial = True)
            if serializer.is_valid():
                serializer.save()
                serialized = CaseHistorySerializer(ch)
                logger.info("CaseHistory partially updated successfully")
                return JsonResponse(serialized.data, status=HTTPStatus.ACCEPTED)
            else:
                logger.warning(f"Serializer is not valid: {serializer.errors}")
                return JsonResponse(serializer.errors, status=HTTPStatus.BAD_REQUEST)
        except json.JSONDecodeError as e:
            logger.error(f"JSONDecodeError: {e}")
            return JsonResponse({"message": "Invalid JSON"}, status=HTTPStatus.BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Unexpected error during CaseHistory partial update: {e}")
            return JsonResponse({"message": "CaseHistory not updated due to an error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        finally:
            logger.info("Exiting partial_update")

    def destroy(self, request, pk = None):
        logger.info("Entering destroy")
        chid = pk
        logger.info(f"CaseHistory ID to delete: {chid}")
        try:
            ch = CaseHistory.objects.get(pk=chid)
            ch.delete()
            logger.info("CaseHistory deleted successfully")
        except CaseHistory.DoesNotExist:
            logger.warning(f"CaseHistory with pk={chid} not found")
            return JsonResponse({"message": "CaseHistory not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Unexpected error during CaseHistory deletion: {e}")
            return JsonResponse({"message": "CaseHistory not deleted due to an error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        finally:
            logger.info("Exiting destroy")

    def retrieve(self, request, pk = None):
        logger.info("Entering retrieve")
        chid = pk
        logger.info(f"CaseHistory ID to retrieve: {chid}")
        try:
            ch = CaseHistory.objects.get(pk=chid)
        except CaseHistory.DoesNotExist:
            logger.warning(f"CaseHistory with pk={chid} not found")
            return JsonResponse({"message": "CaseHistory not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)

        serialized = CaseHistorySerializer(ch)
        logger.info("Exiting retrieve")
        return JsonResponse(serialized.data, status=200)

class MediaViewSet(viewsets.ViewSet):
    def list(self,request):
        logger.info("Entering list")
        try:
            md = Media.objects.all()
        except Media.DoesNotExist:
            logger.warning("Media not found")
            return JsonResponse({"message": "Media not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)

        serialized = MediaSerializer(md,many= True)
        logger.info("Exiting list")
        return JsonResponse(serialized.data, safe=False)

    def create(self, request):
        logger.info("Entering create")
        try:
            serializer = MediaSerializer(data=json.loads(request.data))
            if serializer.is_valid():
                md  = Media(**serializer.validated_data)
                md.save()

                serialized = MediaSerializer(md)
                logger.info("Exiting create")
                return JsonResponse(serialized.data, status = HTTPStatus.OK)
            else:
                logger.warning(f"Serializer is not valid: {serializer.errors}")
                return JsonResponse({"message": "Media not saved"}, status=HTTPStatus.BAD_REQUEST)
        except json.JSONDecodeError as e:
            logger.error(f"JSONDecodeError: {e}")
            return JsonResponse({"message": "Invalid JSON"}, status=HTTPStatus.BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Unexpected error during Media creation: {e}")
            return JsonResponse({"message": "Media not saved due to an error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        finally:
            logger.info("Exiting create")

    def update(self, request, pk = None):
        logger.info("Entering update")
        mid = pk
        logger.info(f"Media ID to update: {mid}")
        try:
            md = Media.objects.get(pk = mid)
        except Media.DoesNotExist:
            logger.warning(f"Media with pk={mid} not found")
            return JsonResponse({"message": "Media not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)

        try:
            serializer = MediaSerializer(md, data= json.loads(request.data), partial = True)
            if serializer.is_valid():
                serializer.save()
                serialized = MediaSerializer(md)
                logger.info("Media updated successfully")
                return JsonResponse(serialized.data, status=HTTPStatus.ACCEPTED)
            else:
                logger.warning(f"Serializer is not valid: {serializer.errors}")
                return JsonResponse(serializer.errors, status=HTTPStatus.BAD_REQUEST)
        except json.JSONDecodeError as e:
            logger.error(f"JSONDecodeError: {e}")
            return JsonResponse({"message": "Invalid JSON"}, status=HTTPStatus.BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Unexpected error during Media update: {e}")
            return JsonResponse({"message": "Media not updated due to an error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        finally:
            logger.info("Exiting update")

    def destroy(self, request, pk = None):
        logger.info("Entering destroy")
        mid = pk
        logger.info(f"Media ID to delete: {mid}")
        try:
            md = Media.objects.get(pk=mid)
            md.delete()
            logger.info("Media deleted successfully")
        except Media.DoesNotExist:
            logger.warning(f"Media with pk={mid} not found")
            return JsonResponse({"message": "Media not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Unexpected error during Media deletion: {e}")
            return JsonResponse({"message": "Media not deleted due to an error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        finally:
            logger.info("Exiting destroy")

    def partial_destroy(self, request, pk = None):
        logger.info("Entering partial_destroy")
        mid = pk
        logger.info(f"Media ID to partially destroy: {mid}")
        try:
            md = Media.objects.get(pk=mid)
            md.delete()
            logger.info("Media partially destroyed successfully")
        except Media.DoesNotExist:
            logger.warning(f"Media with pk={mid} not found")
            return JsonResponse({"message": "Media not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Unexpected error during Media partial destruction: {e}")
            return JsonResponse({"message": "Media not deleted due to an error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        finally:
            logger.info("Exiting partial_destroy")

    def retrieve(self, request, pk):
        logger.info("Entering retrieve")
        mid = pk
        logger.info(f"Media ID to retrieve: {mid}")
        try:
            md = Media.objects.get(pk=mid)
        except Media.DoesNotExist:
            logger.warning(f"Media with pk={mid} not found")
            return JsonResponse({"message": "Media not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)

        serialized = MediaSerializer(md)
        logger.info("Exiting retrieve")
        return JsonResponse(serialized.data, status=200)

class LostVehicleViewSet(viewsets.ViewSet):
    def list(self,request):
        logger.info("Entering list")
        try:
            lv = LostVehicle.objects.all()
        except LostVehicle.DoesNotExist:
            logger.warning("Lost Vehicle not found")
            return JsonResponse({"message": "Lost Vehicle not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)

        serialized = LostVehicleSerializer(lv,many= True)
        logger.info("Exiting list")
        return JsonResponse(serialized.data, safe=False)

    def create(self, request):
        logger.info("Entering create")
        try:
            serializer = LostVehicleSerializer(data=json.loads(request.data))
            if serializer.is_valid():
                lv  = LostVehicle(**serializer.validated_data)
                lv.save()

                serialized = LostVehicleSerializer(lv)
                logger.info("Exiting create with success")
                return JsonResponse(serialized.data, status = HTTPStatus.OK)
            else:
                logger.warning(f"Serializer is not valid: {serializer.errors}")
                return JsonResponse({"message": "Lost vehicle not saved"}, status=HTTPStatus.BAD_REQUEST)
        except json.JSONDecodeError as e:
            logger.error(f"JSONDecodeError: {e}")
            return JsonResponse({"message": "Invalid JSON"}, status=HTTPStatus.BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Unexpected error during LostVehicle creation: {e}")
            return JsonResponse({"message": "Lost vehicle not saved due to an error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        finally:
            logger.info("Exiting create")

    def update(self, request, pk = None):
        logger.info("Entering update")
        caseId  = pk
        logger.info(f"LostVehicle ID to update: {caseId}")
        try:
            lv = LostVehicle.objects.get(pk = caseId)
        except LostVehicle.DoesNotExist:
            logger.warning(f"LostVehicle with pk={caseId} not found")
            return JsonResponse({"message": "LostVehicle not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)

        try:
            serializer = LostVehicleSerializer(lv, data= json.loads(request.data), partial = True)
            if serializer.is_valid():
                serializer.save()
                serialized = LostVehicleSerializer(lv)
                logger.info("LostVehicle updated successfully")
                return JsonResponse(serialized.data, status=HTTPStatus.ACCEPTED)
            else:
                logger.warning(f"Serializer is not valid: {serializer.errors}")
                return JsonResponse(serializer.errors, status=HTTPStatus.BAD_REQUEST)
        except json.JSONDecodeError as e:
            logger.error(f"JSONDecodeError: {e}")
            return JsonResponse({"message": "Invalid JSON"}, status=HTTPStatus.BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Unexpected error during LostVehicle update: {e}")
            return JsonResponse({"message": "LostVehicle not updated due to an error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        finally:
            logger.info("Exiting update")

    def partial_update(self, request, pk = None):
        logger.info("Entering partial_update")
        caseId  = pk
        logger.info(f"LostVehicle ID to partially update: {caseId}")
        try:
            lv = LostVehicle.objects.get(pk = caseId)
        except LostVehicle.DoesNotExist:
            logger.warning(f"LostVehicle with pk={caseId} not found")
            return JsonResponse({"message": "LostVehicle not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)

        try:
            serializer = LostVehicleSerializer(lv, data= json.loads(request.data), partial = True)
            if serializer.is_valid():
                serializer.save()
                serialized = LostVehicleSerializer(lv)
                logger.info("LostVehicle partially updated successfully")
                return JsonResponse(serialized.data, status=HTTPStatus.ACCEPTED)
            else:
                logger.warning(f"Serializer is not valid: {serializer.errors}")
                return JsonResponse(serializer.errors, status=HTTPStatus.BAD_REQUEST)
        except json.JSONDecodeError as e:
            logger.error(f"JSONDecodeError: {e}")
            return JsonResponse({"message": "Invalid JSON"}, status=HTTPStatus.BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Unexpected error during LostVehicle partial update: {e}")
            return JsonResponse({"message": "LostVehicle not updated due to an error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        finally:
            logger.info("Exiting partial_update")

    def destroy(self, request, pk = None):
        logger.info("Entering destroy")
        caseId  = pk
        logger.info(f"LostVehicle ID to delete: {caseId}")
        try:
            lv = LostVehicle.objects.get(pk=caseId)
            lv.delete()
            logger.info("LostVehicle deleted successfully")
        except LostVehicle.DoesNotExist:
            logger.warning(f"LostVehicle with pk={caseId} not found")
            return JsonResponse({"message": "LostVehicle not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Unexpected error during LostVehicle deletion: {e}")
            return JsonResponse({"message": "LostVehicle not deleted due to an error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        finally:
            logger.info("Exiting destroy")

    def retrieve(self, request, pk):
        logger.info("Entering retrieve")
        logger.info(f"LostVehicle ID to retrieve: {pk}")
        try:
            lv = LostVehicle.objects.get(caseId=pk)
        except LostVehicle.DoesNotExist:
            logger.warning(f"LostVehicle with caseId={pk} not found")
            return JsonResponse({"message": "LostVehicle not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)

        serialized = LostVehicleSerializer(lv)
        logger.info("Exiting retrieve")
        return JsonResponse(serialized.data, status=200)

class CommentViewSet(viewsets.ViewSet):
    def list(self,request):
        logger.info("Entering list")
        try:
            lv = Comment.objects.all()
        except Comment.DoesNotExist:
            logger.warning("Comments not found")
            return JsonResponse({"message": "Comments not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)

        serialized = CommentSerializer(lv,many= True)
        logger.info("Exiting list")
        return JsonResponse(serialized.data, safe=False)

    def create(self, request):
        logger.info("Entering create")
        try:
            serializer = CommentSerializer(data=json.loads(request.data))
            if serializer.is_valid():
                lv  = Comment(**serializer.validated_data)
                lv.save()

                serialized = CommentSerializer(lv)
                logger.info("Exiting create with success")
                return JsonResponse(serialized.data, status = HTTPStatus.OK)
            else:
                logger.warning(f"Serializer is not valid: {serializer.errors}")
                return JsonResponse({"message": "Comment not saved"}, status=HTTPStatus.BAD_REQUEST)
        except json.JSONDecodeError as e:
            logger.error(f"JSONDecodeError: {e}")
            return JsonResponse({"message": "Invalid JSON"}, status=HTTPStatus.BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Unexpected error during Comment creation: {e}")
            return JsonResponse({"message": "Comment not saved due to an error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        finally:
            logger.info("Exiting create")

    def update(self, request, pk = None):
        logger.info("Entering update")
        caseId  = pk
        logger.info(f"Comment ID to update: {caseId}")
        try:
            lv = Comment.objects.get(pk = caseId)
        except Comment.DoesNotExist:
            logger.warning(f"Comment with pk={caseId} not found")
            return JsonResponse({"message": "Comment not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)

        try:
            serializer = CommentSerializer(lv, data= json.loads(request.data), partial = True)
            if serializer.is_valid():
                serializer.save()
                serialized = CommentSerializer(lv)
                logger.info("Comment updated successfully")
                return JsonResponse(serialized.data, status=HTTPStatus.ACCEPTED)
            else:
                logger.warning(f"Serializer is not valid: {serializer.errors}")
                return JsonResponse(serializer.errors, status=HTTPStatus.BAD_REQUEST)
        except json.JSONDecodeError as e:
            logger.error(f"JSONDecodeError: {e}")
            return JsonResponse({"message": "Invalid JSON"}, status=HTTPStatus.BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Unexpected error during Comment update: {e}")
            return JsonResponse({"message": "Comment not updated due to an error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        finally:
            logger.info("Exiting update")

    def destroy(self, request, pk = None):
        logger.info("Entering destroy")
        caseId  = pk
        logger.info(f"Comment ID to delete: {caseId}")
        try:
            lv = Comment.objects.get(pk=caseId)
            lv.delete()
            logger.info("Comment deleted successfully")
        except Comment.DoesNotExist:
            logger.warning(f"Comment with pk={caseId} not found")
            return JsonResponse({"message": "Comment not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Unexpected error during Comment deletion: {e}")
            return JsonResponse({"message": "Comment not deleted due to an error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        finally:
            logger.info("Exiting destroy")

    def retrieve(self, request, pk):
        logger.info("Entering retrieve")
        logger.info(f"Comment ID to retrieve: {pk}")
        try:
            lv = Comment.objects.get(cmtid=pk)
        except Comment.DoesNotExist:
            logger.warning(f"Comment with cmtid={pk} not found")
            return JsonResponse({"message": "LostVehicle not found"}, status=HTTPStatus.NOT_FOUND)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JsonResponse({"message": "invalid input"}, status=HTTPStatus.BAD_REQUEST)

        serialized = CommentSerializer(lv)
        logger.info("Exiting retrieve")
        return JsonResponse(serialized.data, status=200)
