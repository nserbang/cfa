from rest_framework.viewsets import ModelViewSet
from api.models import AboutPage
from api.serializers import AboutSerializer
from api.viewset.permission import IsReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class AboutViewSet(ModelViewSet):
    serializer_class = AboutSerializer
    queryset = AboutPage.objects.all()
    permission_classes = (IsReadOnly,)
    

class AboutAPIView(APIView):
    """
    API endpoint to get the latest About content.
    """
    def get(self, request):
        about = AboutPage.objects.order_by('-id').first()
        if about:
            serializer = AboutSerializer(about)
            return Response(serializer.data)
        return Response({"detail": "No about content found."}, status=status.HTTP_404_NOT_FOUND)