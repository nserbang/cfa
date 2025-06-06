from rest_framework.viewsets import ModelViewSet
from api.models import Privacy
from api.serializers import PrivacySerializer
from api.viewset.permission import IsReadOnly

class PrivacyViewSet(ModelViewSet):
    serializer_class = PrivacySerializer
    queryset = Privacy.objects.all()
    permission_classes = (IsReadOnly,)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.models import Privacy
from api.serializers import PrivacySerializer

class PrivacyAPIView(APIView):
    """
    API endpoint to get the latest Privacy content.
    """
    def get(self, request):
        privacy = Privacy.objects.order_by('-id').first()
        if privacy:
            serializer = PrivacySerializer(privacy)
            return Response(serializer.data)
        return Response({"detail": "No privacy content found."}, status=status.HTTP_404_NOT_FOUND)