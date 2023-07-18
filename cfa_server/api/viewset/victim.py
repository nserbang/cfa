from rest_framework.viewsets import ModelViewSet
from api.models import Victim
from api.serializers import VictimSerializer
from api.viewset.permission import IsReadOnly

class VictimViewSet(ModelViewSet):
    serializer_class = VictimSerializer
    queryset = Victim.objects.all()
    permission_classes = (IsReadOnly,)