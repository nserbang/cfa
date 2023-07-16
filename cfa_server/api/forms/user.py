from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from api.models import cUser


class cUserCreationForm(UserCreationForm):

    class Meta:
        model = cUser
        fields = ('username',)

class cUserChangeForm(UserChangeForm):

    class Meta:
        model = cUser
        fields = ('username',)