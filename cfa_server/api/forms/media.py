from django import forms
from api.models import Media
from api.forms import detect_malicious_patterns, detect_malicious_patterns_in_media
import logging

logger = logging.getLogger(__name__)

class MediaForm(forms.ModelForm):
    class Meta:
        model = Media
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        logger.info("Entering MediaForm.__init__")
        super().__init__(*args, **kwargs)
        logger.info("Exiting MediaForm.__init__")

    def clean(self):
        logger.info("Entering MediaForm.clean")
        cleaned_data = super().clean()
        file_path = cleaned_data.get('path')
        
        if file_path:
            logger.debug(f"Validating file: {file_path}")
            malicious_file = detect_malicious_patterns(file_path)
            
            if malicious_file:
                logger.warning(f"Malicious file detected: {file_path}")
                self.add_error('path', forms.ValidationError("Malicious file type."))
            else:
                logger.info(f"File validation passed: {file_path}")
        else:
            logger.warning("No file path provided")
            
        logger.info("Exiting MediaForm.clean")
        return cleaned_data

    def save(self, commit=True):
        logger.info("Entering MediaForm.save")
        instance = super().save(commit=False)
        
        if commit:
            instance.save()
            logger.info(f"Saved media instance: {instance.id}")
        else:
            logger.debug("Skipping save (commit=False)")
            
        logger.info("Exiting MediaForm.save")
        return instance



