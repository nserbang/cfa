from django.utils.html import format_html
from django.contrib import admin
from .models import *
from django.urls import reverse
#from api.log import log
# Register your models here.

@admin.register(District)
class DistrictModel(admin.ModelAdmin):
    list_display = ["did","name"]

@admin.register(cUser)
class cUserModel(admin.ModelAdmin):
    list_display = ['username','first_name','last_name','email','password','is_active', \
                    'is_staff','is_superuser','role','address','pincode','otp_code']

""" @admin.register(PoliceStation)
class PoliceStationModel(admin.ModelAdmin):
    def did_name(self, obj):
        return obj.district.name
       
    list_display = ['pid',did_name,'name','address','lat','long'] """



class PoliceStationAdmin(admin.ModelAdmin):
    def contact(self,obj):
        #psc = PoliceStationContact.objects.get(pid = obj)
        #obj.field3
        return format_html('<span style="color: red"> <p> This is new para </p> <a hreff ="#">hello {} fff</a></span>',obj.name)    
    contact.short_description = 'Custom Field'

    def station(self, obj):
        return format_html('<span> {} \
            <p> {}, {}</p> </span>', obj.name,obj.address, obj.did.name)
        #print(" MAGIC :",str)
        #return format_html(str,obj.name,obj.address, obj.did.name)
    station.short_description = 'Police Station'                 
        
        
    def district(self):             
        return self.did.name
    
    list_display = ['pid',district,'name', 'address','lat','long','station']
    list_select_related = ('did',)
    district.admin_order_field = 'did__did'
    search_fields =['name']



admin.site.register(PoliceStation,PoliceStationAdmin)

class PoliceStationContactAdmin(admin.ModelAdmin):
    def PoliceStation(self):
        return self.pid.name
    PoliceStation.short_description ="Police Station"

    def contact_id(self):
        return self.contactName    
    contact_id.short_description = "Contact Id"

    #fields = [PoliceStation,'contactName','number']
    list_display = ['contactName',PoliceStation,'number']
    #ps_cid.short_descrption = 'Contact Id'
    list_select_related = ('pid',)
    PoliceStation.admin_order_field = "pid__pid"
    search_fields = ['number__icontains','contactName__icontains','pid__pid__icontains']

admin.site.register(PoliceStationContact, PoliceStationContactAdmin)
 

