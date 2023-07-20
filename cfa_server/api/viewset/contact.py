from rest_framework.viewsets import ModelViewSet
from api.models import Contact
from api.serializers import ContactSerializer
from api.viewset.permission import IsReadOnly

class ContactViewSet(ModelViewSet):
    serializer_class = ContactSerializer
    queryset = Contact.objects.all()
    permission_classes = (IsReadOnly,)