from django import forms
from django.utils.html import format_html
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
import logging
logger = logging.getLogger(__name__)

from api.forms.banner import BannerForm
from api.forms.media import MediaForm
from .models import *
from api.forms.user import UserChangeForm, UserCreationForm

# from api.log import log
# Register your models here.


@admin.register(District)
class DistrictModel(admin.ModelAdmin):
    def __init__(self, *args, **kwargs):
        logger.info("Entering __init__")
        super().__init__(*args, **kwargs)
        logger.info("Exiting __init__")

    def get_queryset(self, request):
        logger.info("Entering get_queryset")
        qs = super().get_queryset(request)
        logger.info("Exiting get_queryset")
        return qs

    def get_ordering(self, request):
        logger.info("Entering get_ordering")
        ordering = super().get_ordering(request)
        logger.info("Exiting get_ordering")
        return ordering

    def get_search_results(self, request, queryset, search_term):
        logger.info("Entering get_search_results")
        results = super().get_search_results(request, queryset, search_term)
        logger.info("Exiting get_search_results")
        return results

    list_display = ["did", "name"]


@admin.register(cUser)
class cUserModel(auth_admin.UserAdmin):
    def __init__(self, *args, **kwargs):
        logger.info("Entering __init__")
        super().__init__(*args, **kwargs)
        logger.info("Exiting __init__")

    def get_queryset(self, request):
        logger.info("Entering get_queryset")
        qs = super().get_queryset(request)
        logger.info("Exiting get_queryset")
        return qs

    def get_ordering(self, request):
        logger.info("Entering get_ordering")
        ordering = super().get_ordering(request)
        logger.info("Exiting get_ordering")
        return ordering

    def get_search_results(self, request, queryset, search_term):
        logger.info("Entering get_search_results")
        results = super().get_search_results(request, queryset, search_term)
        logger.info("Exiting get_search_results")
        return results

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "password",
                )
            },
        ),
        (
            ("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "mobile",
                    "address",
                    "profile_picture",
                )
            },
        ),
        (
            ("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                    "role",
                ),
            },
        ),
        (("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "mobile",
                    "profile_picture",
                    "address",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                    "role",
                ),
            },
        ),
    )
    list_display = [
        "mobile",
        "email",
        "first_name",
        "last_name",
        "is_superuser",
        "role",
    ]
    search_fields = ["first_name", "email", "mobile", "role"]
    ordering = ["-date_joined", "mobile"]
    form = UserChangeForm
    add_form = UserCreationForm


class PoliceStationAdmin(admin.ModelAdmin):
    def __init__(self, *args, **kwargs):
        logger.info("Entering __init__")
        super().__init__(*args, **kwargs)
        logger.info("Exiting __init__")

    def get_queryset(self, request):
        logger.info("Entering get_queryset")
        qs = super().get_queryset(request)
        logger.info("Exiting get_queryset")
        return qs

    def get_ordering(self, request):
        logger.info("Entering get_ordering")
        ordering = super().get_ordering(request)
        logger.info("Exiting get_ordering")
        return ordering

    def get_search_results(self, request, queryset, search_term):
        logger.info("Entering get_search_results")
        results = super().get_search_results(request, queryset, search_term)
        logger.info("Exiting get_search_results")
        return results

    def contact(self, obj):
        logger.info("Entering contact")
        try:
            contact_html = format_html(
                '<span style="color: red"> <p> This is new para </p> <a hreff ="#">hello {} fff</a></span>',
                obj.name,
            )
            logger.info("Contact formatted successfully")
        except Exception as e:
            logger.exception(f"Error formatting contact: {e}")
            contact_html = "Error formatting contact"
        logger.info("Exiting contact")
        return contact_html

    contact.short_description = "Custom Field"

    def station(self, obj):
        logger.info("Entering station")
        try:
            station_html = format_html(
                "<span> {} \
                <p> {}, {}</p> </span>",
                obj.name,
                obj.address,
                obj.did.name,
            )
            logger.info("Station formatted successfully")
        except Exception as e:
            logger.exception(f"Error formatting station: {e}")
            station_html = "Error formatting station"
        logger.info("Exiting station")
        return station_html

    station.short_description = "Police Station"

    def district(self, obj):
        logger.info("Entering district")
        try:
            district_name = obj.did.name
            logger.info(f"District name: {district_name}")
        except Exception as e:
            logger.exception(f"Error getting district name: {e}")
            district_name = "Error getting district name"
        logger.info("Exiting district")
        return district_name

    district.short_description = "District"

    list_display = ["pid", district, "name", "address", "lat", "long", "station"]
    list_select_related = ("did",)
    district.admin_order_field = "did__did"
    search_fields = ["name"]


admin.site.register(PoliceStation, PoliceStationAdmin)


class PoliceStationContactAdmin(admin.ModelAdmin):
    def __init__(self, *args, **kwargs):
        logger.info("Entering __init__")
        super().__init__(*args, **kwargs)
        logger.info("Exiting __init__")

    def get_queryset(self, request):
        logger.info("Entering get_queryset")
        qs = super().get_queryset(request)
        logger.info("Exiting get_queryset")
        return qs

    def get_ordering(self, request):
        logger.info("Entering get_ordering")
        ordering = super().get_ordering(request)
        logger.info("Exiting get_ordering")
        return ordering

    def get_search_results(self, request, queryset, search_term):
        logger.info("Entering get_search_results")
        results = super().get_search_results(request, queryset, search_term)
        logger.info("Exiting get_search_results")
        return results

    def PoliceStation(self, obj):
        logger.info("Entering PoliceStation")
        try:
            police_station_name = obj.pid.name
            logger.info(f"Police station name: {police_station_name}")
        except Exception as e:
            logger.exception(f"Error getting police station name: {e}")
            police_station_name = "Error getting police station name"
        logger.info("Exiting PoliceStation")
        return police_station_name

    PoliceStation.short_description = "Police Station"

    def contact_id(self, obj):
        logger.info("Entering contact_id")
        try:
            contact_name = obj.contactName
            logger.info(f"Contact name: {contact_name}")
        except Exception as e:
            logger.exception(f"Error getting contact name: {e}")
            contact_name = "Error getting contact name"
        logger.info("Exiting contact_id")
        return contact_name

    contact_id.short_description = "Contact Id"

    # fields = [PoliceStation,'contactName','number']
    list_display = ["contactName", PoliceStation, "number"]
    # ps_cid.short_descrption = 'Contact Id'
    list_select_related = ("pid",)
    PoliceStation.admin_order_field = "pid__pid"
    search_fields = [
        "number__icontains",
        "contactName__icontains",
        "pid__pid__icontains",
    ]


admin.site.register(PoliceStationContact, PoliceStationContactAdmin)


class PoliceOfficerAdmin(admin.ModelAdmin):
    def __init__(self, *args, **kwargs):
        logger.info("Entering __init__")
        super().__init__(*args, **kwargs)
        logger.info("Exiting __init__")

    def get_queryset(self, request):
        logger.info("Entering get_queryset")
        qs = super().get_queryset(request)
        logger.info("Exiting get_queryset")
        return qs

    def get_ordering(self, request):
        logger.info("Entering get_ordering")
        ordering = super().get_ordering(request)
        logger.info("Exiting get_ordering")
        return ordering

    def get_search_results(self, request, queryset, search_term):
        logger.info("Entering get_search_results")
        results = super().get_search_results(request, queryset, search_term)
        logger.info("Exiting get_search_results")
        return results

    list_display = ["oid", "pid", "rank", "entryDate", "mobile", "status"]
    #autocomplete_fields =['mobile']
    search_fields = [
        "name__icontains",
        "pid__pid__icontains",
        "rank__icontains",
        "entryDate__icontains",
        "^mobile",
        "^status",
    ]


admin.site.register(PoliceOfficer, PoliceOfficerAdmin)


class CaseAdmin(admin.ModelAdmin):
    def __init__(self, *args, **kwargs):
        logger.info("Entering __init__")
        super().__init__(*args, **kwargs)
        logger.info("Exiting __init__")

    def get_queryset(self, request):
        logger.info("Entering get_queryset")
        qs = super().get_queryset(request)
        logger.info("Exiting get_queryset")
        return qs

    def get_ordering(self, request):
        logger.info("Entering get_ordering")
        ordering = super().get_ordering(request)
        logger.info("Exiting get_ordering")
        return ordering

    def get_search_results(self, request, queryset, search_term):
        logger.info("Entering get_search_results")
        results = super().get_search_results(request, queryset, search_term)
        logger.info("Exiting get_search_results")
        return results

    def PoliceStation(self, obj):
        logger.info("Entering PoliceStation")
        try:
            police_station_name = obj.pid.name
            logger.info(f"Police station name: {police_station_name}")
        except Exception as e:
            logger.exception(f"Error getting police station name: {e}")
            police_station_name = "Error getting police station name"
        logger.info("Exiting PoliceStation")
        return police_station_name

    PoliceStation.short_description = "Police Station"

    def contact_id(self, obj):
        logger.info("Entering contact_id")
        try:
            contact_name = obj.contactName
            logger.info(f"Contact name: {contact_name}")
        except Exception as e:
            logger.exception(f"Error getting contact name: {e}")
            contact_name = "Error getting contact name"
        logger.info("Exiting contact_id")
        return contact_name

    contact_id.short_description = "Contact Id"

    # fields = [PoliceStation,'contactName','number']
    list_display = ["contactName", PoliceStation, "number"]
    # ps_cid.short_descrption = 'Contact Id'
    list_select_related = ("pid",)
    PoliceStation.admin_order_field = "pid__pid"

    def officer_name(self, obj):
        logger.info("Entering officer_name")
        try:
            ranks = PoliceOfficer.RANKS
            dic = {}
            for x in ranks:
                d1 = {k: v for k, v in zip(x[0:], x[1:])}
                dic = {**dic, **d1}
            officer_name_html = format_html(
                "<span> <b> {} </b> <p> {} </p> </span>",
                obj.oid.user.first_name,
                dic[obj.oid.rank],
            )
            logger.info("Officer name formatted successfully")
        except Exception as e:
            logger.exception(f"Error formatting officer name: {e}")
            officer_name_html = "Error formatting officer name"
        logger.info("Exiting officer_name")
        return officer_name_html

    officer_name.short_description = "Officer Name"
    officer_name.admin_order_field = "oid__oid"
    list_select_related = ("pid", "oid")
    # search_fields = ['number__icontains','contactName__icontains','pid__pid__icontains']
    list_display = [
        "cid",
        PoliceStation,
        "user",
        # officer_name,
        "type",
        "title",
        "cstate",
        "created",
        "lat",
        "long",
        "description",
        "follow",
    ]
    search_fields = ["type__icontains", "^cstate", "created__icontains"]


admin.site.register(Case, CaseAdmin)


class CaseHistoryAdmin(admin.ModelAdmin):
    def __init__(self, *args, **kwargs):
        logger.info("Entering __init__")
        super().__init__(*args, **kwargs)
        logger.info("Exiting __init__")

    def get_queryset(self, request):
        logger.info("Entering get_queryset")
        qs = super().get_queryset(request)
        logger.info("Exiting get_queryset")
        return qs

    def get_ordering(self, request):
        logger.info("Entering get_ordering")
        ordering = super().get_ordering(request)
        logger.info("Exiting get_ordering")
        return ordering

    def get_search_results(self, request, queryset, search_term):
        logger.info("Entering get_search_results")
        results = super().get_search_results(request, queryset, search_term)
        logger.info("Exiting get_search_results")
        return results

    list_display = ["id", "case", "user", "cstate", "created", "description"]
    list_editable = ["cstate"]
    search_fields = ["cid__icontains"]


admin.site.register(CaseHistory, CaseHistoryAdmin)


class MediaAdmin(admin.ModelAdmin):
    def __init__(self, *args, **kwargs):
        logger.info("Entering __init__")
        super().__init__(*args, **kwargs)
        logger.info("Exiting __init__")

    def get_queryset(self, request):
        logger.info("Entering get_queryset")
        qs = super().get_queryset(request)
        logger.info("Exiting get_queryset")
        return qs

    def get_ordering(self, request):
        logger.info("Entering get_ordering")
        ordering = super().get_ordering(request)
        logger.info("Exiting get_ordering")
        return ordering

    def get_search_results(self, request, queryset, search_term):
        logger.info("Entering get_search_results")
        results = super().get_search_results(request, queryset, search_term)
        logger.info("Exiting get_search_results")
        return results

    form = MediaForm

    list_display = ["mtype", "path", "description"]
    search_fields = ["mtype"]


class LostVehicleAdmin(admin.ModelAdmin):
    def __init__(self, *args, **kwargs):
        logger.info("Entering __init__")
        super().__init__(*args, **kwargs)
        logger.info("Exiting __init__")

    def get_queryset(self, request):
        logger.info("Entering get_queryset")
        qs = super().get_queryset(request)
        logger.info("Exiting get_queryset")
        return qs

    def get_ordering(self, request):
        logger.info("Entering get_ordering")
        ordering = super().get_ordering(request)
        logger.info("Exiting get_ordering")
        return ordering

    def get_search_results(self, request, queryset, search_term):
        logger.info("Entering get_search_results")
        results = super().get_search_results(request, queryset, search_term)
        logger.info("Exiting get_search_results")
        return results

    def Id(self, obj):
        logger.info("Entering Id")
        try:
            case_id = obj.caseId.cid
            logger.info(f"Case ID: {case_id}")
        except Exception as e:
            logger.exception(f"Error getting case ID: {e}")
            case_id = "Error getting case ID"
        logger.info("Exiting Id")
        return case_id

    Id.short_description = "Case ID"
    # PoliceStation.short_description ="Police Station"
    list_display = [
        Id,
        "regNumber",
        "chasisNumber",
        "engineNumber",
        "make",
        "model",
        "type",
    ]


admin.site.register(LostVehicle, LostVehicleAdmin)

"""caseId = models.OneToOneField(Case,to_field="cid",db_column="Case_cid",on_delete=models.DO_NOTHING)
    regNumber = models.CharField(max_length=30)
    chasisNumber = models.CharField(max_length=50, null=True)
    engineNumber = models.CharField(max_length=50, null=True)
    make = models.CharField(max_length=50, null=True)
    model = models.CharField(max_length=50, null=True) """


class CommentAdmin(admin.ModelAdmin):
    def __init__(self, *args, **kwargs):
        logger.info("Entering __init__")
        super().__init__(*args, **kwargs)
        logger.info("Exiting __init__")

    def get_queryset(self, request):
        logger.info("Entering get_queryset")
        qs = super().get_queryset(request)
        logger.info("Exiting get_queryset")
        return qs

    def get_ordering(self, request):
        logger.info("Entering get_ordering")
        ordering = super().get_ordering(request)
        logger.info("Exiting get_ordering")
        return ordering

    def get_search_results(self, request, queryset, search_term):
        logger.info("Entering get_search_results")
        results = super().get_search_results(request, queryset, search_term)
        logger.info("Exiting get_search_results")
        return results

    def Id(self, obj):
        logger.info("Entering Id")
        try:
            case_id = obj.cid.cid
            logger.info(f"Case ID: {case_id}")
        except Exception as e:
            logger.exception(f"Error getting case ID: {e}")
            case_id = "Error getting case ID"
        logger.info("Exiting Id")
        return case_id

    Id.short_description = "Case ID"

    def commentid(self, obj):
        logger.info("Entering commentid")
        try:
            comment_id = obj.cmtid
            logger.info(f"Comment ID: {comment_id}")
        except Exception as e:
            logger.exception(f"Error getting comment ID: {e}")
            comment_id = "Error getting comment ID"
        logger.info("Exiting commentid")
        return comment_id

    commentid.short_description = "Comment ID"
    list_display = [commentid, Id, "user", "content"]


admin.site.register(Comment, CommentAdmin)


@admin.register(Information)
class InformationAdmin(admin.ModelAdmin):
    def __init__(self, *args, **kwargs):
        logger.info("Entering __init__")
        super().__init__(*args, **kwargs)
        logger.info("Exiting __init__")

    def get_queryset(self, request):
        logger.info("Entering get_queryset")
        qs = super().get_queryset(request)
        logger.info("Exiting get_queryset")
        return qs

    def get_ordering(self, request):
        logger.info("Entering get_ordering")
        ordering = super().get_ordering(request)
        logger.info("Exiting get_ordering")
        return ordering

    def get_search_results(self, request, queryset, search_term):
        logger.info("Entering get_search_results")
        results = super().get_search_results(request, queryset, search_term)
        logger.info("Exiting get_search_results")
        return results

    def information_id(self, obj):
        logger.info("Entering information_id")
        try:
            information_id_value = obj.inid
            logger.info(f"Information ID: {information_id_value}")
        except Exception as e:
            logger.exception(f"Error getting information ID: {e}")
            information_id_value = "Error getting information ID"
        logger.info("Exiting information_id")
        return information_id_value

    def information_type(self, obj):
        logger.info("Entering information_type")
        try:
            information_type_value = obj.get_information_type_display()
            logger.info(f"Information type: {information_type_value}")
        except Exception as e:
            logger.exception(f"Error getting information type: {e}")
            information_type_value = "Error getting information type"
        logger.info("Exiting information_type")
        return information_type_value

    def title(self, obj):
        logger.info("Entering title")
        try:
            title_value = obj.heading
            logger.info(f"Title: {title_value}")
        except Exception as e:
            logger.exception(f"Error getting title: {e}")
            title_value = "Error getting title"
        logger.info("Exiting title")
        return title_value

    information_id.short_description = "Information ID"
    information_type.short_description = "Type"
    title.short_description = "Title"
    list_display = [information_id, information_type, title]


# @admin.register(Victim)
# class Victim(admin.ModelAdmin):
#     pass

# @admin.register(Criminal)
# class Criminal(admin.ModelAdmin):
#     pass


class BannerAdmin(admin.ModelAdmin):
    def __init__(self, *args, **kwargs):
        logger.info("Entering __init__")
        super().__init__(*args, **kwargs)
        logger.info("Exiting __init__")

    def get_queryset(self, request):
        logger.info("Entering get_queryset")
        qs = super().get_queryset(request)
        logger.info("Exiting get_queryset")
        return qs

    def get_ordering(self, request):
        logger.info("Entering get_ordering")
        ordering = super().get_ordering(request)
        logger.info("Exiting get_ordering")
        return ordering

    def get_search_results(self, request, queryset, search_term):
        logger.info("Entering get_search_results")
        results = super().get_search_results(request, queryset, search_term)
        logger.info("Exiting get_search_results")
        return results

    form = BannerForm

    list_display = (
        "bid",
        "mtype",
        "description",
    )
    search_fields = [
        "bid",
        "mtype",
        "description",
    ]


class EmergencyAdminForm(forms.ModelForm):
    class Meta:
        model = Emergency
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        logger.info("Entering EmergencyAdminForm __init__")
        super().__init__(*args, **kwargs)
        # Remove placeholder for the name field
        self.fields["name"].widget.attrs.pop("placeholder", None)
        # Make Name field mandatory
        self.fields["name"].required = True
        # Change label of tid to Type
        self.fields["tid"].label = "Type"
        logger.info("Exiting EmergencyAdminForm __init__")

    def clean(self):
        logger.info("Entering EmergencyAdminForm clean")
        cleaned_data = super().clean()
        lat = cleaned_data.get("lat")
        long = cleaned_data.get("long")

        # Ensure lat and long are no more than 9 digits
        if lat is not None:
            lat_str = str(lat).replace('.', '').replace('-', '')
            if len(lat_str) > 8:
                lat = float(str(lat)[:9])
                logger.warning(f"Latitude truncated to 9 digits: {lat}")
        if long is not None:
            long_str = str(long).replace('.', '').replace('-', '')
            if len(long_str) > 8:
                long = float(str(long)[:9])
                logger.warning(f"Longitude truncated to 9 digits: {long}")

        # Ensure lat and long are mandatory
        if lat is None or long is None:
            logger.warning("Latitude and Longitude are required.")
            raise forms.ValidationError("Latitude and Longitude are required.")

        # Truncate lat and long to 6 decimal places
        if lat is not None:
            cleaned_data["lat"] = round(lat, 6)
        if long is not None:
            cleaned_data["long"] = round(long, 6)

        logger.info("Exiting EmergencyAdminForm clean")
        return cleaned_data


class EmergencyAdmin(admin.ModelAdmin):
    def __init__(self, *args, **kwargs):
        logger.info("Entering __init__")
        super().__init__(*args, **kwargs)
        logger.info("Exiting __init__")

    def get_queryset(self, request):
        logger.info("Entering get_queryset")
        qs = super().get_queryset(request)
        logger.info("Exiting get_queryset")
        return qs

    def get_ordering(self, request):
        logger.info("Entering get_ordering")
        ordering = super().get_ordering(request)
        logger.info("Exiting get_ordering")
        return ordering

    def get_search_results(self, request, queryset, search_term):
        logger.info("Entering get_search_results")
        results = super().get_search_results(request, queryset, search_term)
        logger.info("Exiting get_search_results")
        return results

    form = EmergencyAdminForm
    list_display = ("emid", "tid_display", "name", "number", "address", "lat", "long")  # Added address

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        logger.info("Entering formfield_for_foreignkey")
        if db_field.name == "tid":
            kwargs["queryset"] = EmergencyType.objects.all()
            logger.info("EmergencyType queryset set for tid field")
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        logger.info("Exiting formfield_for_foreignkey")
        return formfield

    def tid_display(self, obj):
        logger.info("Entering tid_display")
        try:
            service_type = obj.tid.service_type
            logger.info(f"Service type: {service_type}")
        except Exception as e:
            logger.exception(f"Error getting service type: {e}")
            service_type = "Error getting service type"
        logger.info("Exiting tid_display")
        return service_type

    tid_display.short_description = "Service Type"


class EmergencyTypeAdmin(admin.ModelAdmin):
    def __init__(self, *args, **kwargs):
        logger.info("Entering __init__")
        super().__init__(*args, **kwargs)
        logger.info("Exiting __init__")

    def get_queryset(self, request):
        logger.info("Entering get_queryset")
        qs = super().get_queryset(request)
        logger.info("Exiting get_queryset")
        return qs

    def get_ordering(self, request):
        logger.info("Entering get_ordering")
        ordering = super().get_ordering(request)
        logger.info("Exiting get_ordering")
        return ordering

    def get_search_results(self, request, queryset, search_term):
        logger.info("Entering get_search_results")
        results = super().get_search_results(request, queryset, search_term)
        logger.info("Exiting get_search_results")
        return results

    list_display = ("emtid", "service_type")


@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    def __init__(self, *args, **kwargs):
        logger.info("Entering __init__")
        super().__init__(*args, **kwargs)
        logger.info("Exiting __init__")

    def get_queryset(self, request):
        logger.info("Entering get_queryset")
        qs = super().get_queryset(request)
        logger.info("Exiting get_queryset")
        return qs

    def get_ordering(self, request):
        logger.info("Entering get_ordering")
        ordering = super().get_ordering(request)
        logger.info("Exiting get_ordering")
        return ordering

    def get_search_results(self, request, queryset, search_term):
        logger.info("Entering get_search_results")
        results = super().get_search_results(request, queryset, search_term)
        logger.info("Exiting get_search_results")
        return results

    pass # Use default admin interface


""" admin.site.register(Victim)
admin.site.register(Criminal) """
admin.site.register(Privacy)
admin.site.register(PoliceStationSupervisor)
admin.site.register(TermsCondition)
admin.site.register(Contact)
admin.site.register(Like)
admin.site.register(Banner, BannerAdmin)
admin.site.register(Media, MediaAdmin)
admin.site.register(Emergency, EmergencyAdmin)
admin.site.register(EmergencyType, EmergencyTypeAdmin)
