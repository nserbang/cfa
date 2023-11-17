from django import forms

from api.models import Banner
from api.forms import detect_malicious_patterns

class BannerForm(forms.ModelForm):

    class Meta:
        model = Banner
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        file_path = cleaned_data.get('path')

        if file_path:
            malicious_file = detect_malicious_patterns(file_path)
            if malicious_file:
                self.add_error('path', forms.ValidationError("Malicious file type."))



        