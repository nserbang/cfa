from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from api.models import cUser


class cUserCreationForm(UserCreationForm):
    class Meta:
        model = cUser
        fields = ("mobile",)


class cUserChangeForm(UserChangeForm):
    class Meta:
        model = cUser
        fields = ("mobile", "email")
        error_messages = {"mobile": {"unique": ("This mobile is already registered.")}}
