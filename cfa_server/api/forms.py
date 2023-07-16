from django import forms
from .models import cUser


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        max_length=128,
        widget=forms.TextInput(attrs={"type": "password"}),
    )

    class Meta:
        model = cUser
        fields = [
            'username',
            'password',
            'mobile',
            'first_name',
            'last_name',
            'email',
            'role',
            'address',
            'pincode',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].choices = (('user', "User"), ('police', 'Police'))
        self.fields['username'].required = True
        self.fields['last_name'].required = True
        self.fields['last_name'].required = True
