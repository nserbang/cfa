from rest_framework.viewsets import ModelViewSet
from api.models import Privacy
from api.serializers import PrivacySerializer
from api.viewset.permission import IsReadOnly

class PrivacyViewSet(ModelViewSet):
    serializer_class = PrivacySerializer
    queryset = Privacy.objects.all()
    permission_classes = (IsReadOnly,)