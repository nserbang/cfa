from rest_framework.viewsets import ModelViewSet
from api.models import TermsCondition
from api.serializers import TermsConditionSerializer
from api.viewset.permission import IsReadOnly

class TermsConditionViewSet(ModelViewSet):
    serializer_class = TermsConditionSerializer
    queryset = TermsCondition.objects.all()
    permission_classes = (IsReadOnly,)