from rest_framework.viewsets import ModelViewSet
from api.models import TermsCondition
from api.serializers import TermsConditionSerializer
from api.viewset.permission import IsReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class TermsConditionViewSet(ModelViewSet):
    serializer_class = TermsConditionSerializer
    queryset = TermsCondition.objects.all()
    permission_classes = (IsReadOnly,)
    
from api.serializers import TermsConditionSerializer

class TermsConditionAPIView(APIView):
    """
    API endpoint to get the latest Terms and Conditions content.
    """
    def get(self, request):
        terms = TermsCondition.objects.order_by('-id').first()
        if terms:
            serializer = TermsConditionSerializer(terms)
            return Response(serializer.data)
        return Response({"detail": "No terms content found."}, status=status.HTTP_404_NOT_FOUND)