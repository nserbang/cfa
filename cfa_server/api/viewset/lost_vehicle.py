from rest_framework.views import APIView
from rest_framework.response import Response
from api.serializers import CheckLostVehicleSerializer


class CheckLostVehicle(APIView):
    serializer_class = CheckLostVehicleSerializer

    def post(self, request, *args, **kwargs):
        serializer = CheckLostVehicleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.check_vehicle()
        return Response(data)
