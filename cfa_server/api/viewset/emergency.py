from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from api.models import Emergency
from api.serializers import EmergencySerializer
from api.viewset.permission import IsReadOnly

class EmergencyViewSet(ModelViewSet):
    serializer_class = EmergencySerializer
    queryset = Emergency.objects.all()
    permission_classes = (IsReadOnly, )

    def get_queryset(self):
        district_id = self.kwargs['district_id']
        queryset = Emergency.objects.filter(did=district_id)
        return queryset


class EmergencyViewListSet(ModelViewSet):
    serializer_class = EmergencySerializer
    queryset = Emergency.objects.all()
    permission_classes = (IsReadOnly,)
