from django import forms
from django.utils.html import format_html
from django.contrib import admin
from django.contrib.auth import admin as auth_admin

from api.forms.banner import BannerForm
from api.forms.media import MediaForm
from .models import *
from api.forms.user import UserChangeForm, UserCreationForm

# from api.log import log
# Register your models here.


@admin.register(District)
class DistrictModel(admin.ModelAdmin):
    list_display = ["did", "name"]


@admin.register(cUser)
class cUserModel(auth_admin.UserAdmin):
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
    def contact(self, obj):
        # psc = PoliceStationContact.objects.get(pid = obj)
        # obj.field3
        return format_html(
            '<span style="color: red"> <p> This is new para </p> <a hreff ="#">hello {} fff</a></span>',
            obj.name,
        )

    contact.short_description = "Custom Field"

    def station(self, obj):
        return format_html(
            "<span> {} \
            <p> {}, {}</p> </span>",
            obj.name,
            obj.address,
            obj.did.name,
        )
        # print(" MAGIC :",str)
        # return format_html(str,obj.name,obj.address, obj.did.name)

    station.short_description = "Police Station"

    def district(self):
        return self.did.name

    list_display = ["pid", district, "name", "address", "lat", "long", "station"]
    list_select_related = ("did",)
    district.admin_order_field = "did__did"
    search_fields = ["name"]


admin.site.register(PoliceStation, PoliceStationAdmin)


class PoliceStationContactAdmin(admin.ModelAdmin):
    def PoliceStation(self):
        return self.pid.name

    PoliceStation.short_description = "Police Station"

    def contact_id(self):
        return self.contactName

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
    def PoliceStation(self):
        return self.pid.name

    PoliceStation.short_description = "Police Station"

    def contact_id(self):
        return self.contactName

    contact_id.short_description = "Contact Id"

    # fields = [PoliceStation,'contactName','number']
    list_display = ["contactName", PoliceStation, "number"]
    # ps_cid.short_descrption = 'Contact Id'
    list_select_related = ("pid",)
    PoliceStation.admin_order_field = "pid__pid"

    def officer_name(self):
        # print(" Ranks: ",PoliceOfficer.RANKS)
        ranks = PoliceOfficer.RANKS
        # print("rank at 13 :",ranks[13])
        dic = {}
        for x in ranks:
            d1 = {k: v for k, v in zip(x[0:], x[1:])}
            dic = {**dic, **d1}
        return format_html(
            "<span> <b> {} </b> <p> {} </p> </span>",
            self.oid.user.first_name,
            dic[self.oid.rank],
        )

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
    list_display = ["id", "case", "user", "cstate", "created", "description"]
    list_editable = ["cstate"]
    search_fields = ["cid__icontains"]


admin.site.register(CaseHistory, CaseHistoryAdmin)


class MediaAdmin(admin.ModelAdmin):
    form = MediaForm

    list_display = ["mtype", "path", "description"]
    search_fields = ["mtype"]


class LostVehicleAdmin(admin.ModelAdmin):
    def Id(self):
        return self.caseId.cid

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
    def Id(self):
        return self.cid.cid

    Id.short_description = "Case ID"

    def commentid(self):
        return self.cmtid

    commentid.short_description = "Comment ID"
    list_display = [commentid, Id, "user", "content"]


admin.site.register(Comment, CommentAdmin)


@admin.register(Information)
class InformationAdmin(admin.ModelAdmin):
    def information_id(self):
        return self.inid

    def information_type(self):
        return self.get_information_type_display()

    def title(self):
        return self.heading

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
        super().__init__(*args, **kwargs)
        # Remove placeholder for the name field
        self.fields["name"].widget.attrs.pop("placeholder", None)


class EmergencyAdmin(admin.ModelAdmin):
    form = EmergencyAdminForm
    list_display = ("emid", "tid_display", "name", "number", "lat", "long")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "tid":
            kwargs["queryset"] = EmergencyType.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def tid_display(self, obj):
        return obj.tid.service_type


class EmergencyTypeAdmin(admin.ModelAdmin):
    list_display = ("emtid", "service_type")


@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
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
