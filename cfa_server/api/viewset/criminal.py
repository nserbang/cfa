from rest_framework.viewsets import ModelViewSet
from api.models import Criminal
from api.serializers import CriminalSerializer
from api.viewset.permission import IsReadOnly

class CriminalViewSet(ModelViewSet):
    serializer_class = CriminalSerializer
    queryset = Criminal.objects.all()
    permission_classes = (IsReadOnly,)