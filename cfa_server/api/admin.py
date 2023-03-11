from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(District)
class DistrictModel(admin.ModelAdmin):
    list_display = ["did","name"]

@admin.register(cUser)
class cUserModel(admin.ModelAdmin):
    list_display = ['username','first_name','last_name','email','password','is_active', \
                    'is_staff','is_superuser','role','address','pincode','otp_code']