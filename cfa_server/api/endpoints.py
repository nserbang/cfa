from api.views import *

user_create = cUserViewSet.as_view({"post":"create"})
user_update = cUserViewSet.as_view({"patch":"partial_update"})

########################## district url begins####################
district_list = DistrictViewSet.as_view({"get":"list"})
district_create = DistrictViewSet.as_view({"post":"create"})
district_get = DistrictViewSet.as_view({"get":"retrieve"})
district_delete = DistrictViewSet.as_view({"delete":"destroy"})
district_update = DistrictViewSet.as_view({"patch":"update"})
######################### district url name ends##################

########################## PoliceStationContact url begins####################
policeStationContact_list = PoliceStationContactViewSet.as_view({"get":"list"})
policeStationContact_create = PoliceStationContactViewSet.as_view({"post":"create"})
policeStationContact_get = PoliceStationContactViewSet.as_view({"get":"retrieve"})
policeStationContact_delete = PoliceStationContactViewSet.as_view({"delete":"destroy"})
policeStationContact_update = PoliceStationContactViewSet.as_view({"patch":"update"})
######################### PoliceStationContact url name ends##################

########################## PoliceStation url begins####################
policeStation_list = PoliceStationViewSet.as_view({"get":"list"})
policeStation_create = PoliceStationViewSet.as_view({"post":"create"})
policeStation_get = PoliceStationViewSet.as_view({"get":"retrieve"})
policeStation_delete = PoliceStationViewSet.as_view({"delete":"destroy"})
policeStation_update = PoliceStationViewSet.as_view({"patch":"update"})
######################### PoliceStation url name ends##################


########################## PoliceOfficer url begins####################
policeOfficer_list = PoliceOfficerViewSet.as_view({"get":"list"})
policeOfficer_create = PoliceOfficerViewSet.as_view({"post":"create"})
policeOfficer_get = PoliceOfficerViewSet.as_view({"get":"retrieve"})
policeOfficer_delete = PoliceOfficerViewSet.as_view({"delete":"destroy"})
policeOfficer_update = PoliceOfficerViewSet.as_view({"patch":"patch"})
######################### PoliceOfficer url name ends##################

########################## Case url begins####################
case_list = CaseViewSet.as_view({"get":"list"})
case_create = CaseViewSet.as_view({"post":"create"})
case_get = CaseViewSet.as_view({"get":"retrieve"})
case_delete = CaseViewSet.as_view({"delete":"destroy"})
case_update = CaseViewSet.as_view({"patch":"update"})
######################### Case url name ends##################


########################## CaseHistory url begins####################
caseHistory_list = CaseHistoryViewSet.as_view({"get":"list"})
caseHistory_create = CaseHistoryViewSet.as_view({"post":"create"})
caseHistory_get = CaseHistoryViewSet.as_view({"get":"retrieve"})
caseHistory_delete = CaseHistoryViewSet.as_view({"delete":"destroy"})
caseHistory_update = CaseHistoryViewSet.as_view({"patch":"update"})
######################### CaseHistory url name ends##################


########################## Media url begins####################
media_list = MediaViewSet.as_view({"get":"list"})
media_create = MediaViewSet.as_view({"post":"create"})
media_get = MediaViewSet.as_view({"get":"retrieve"})
media_delete = MediaViewSet.as_view({"delete":"destroy"})
media_update = MediaViewSet.as_view({"patch":"update"})
######################### Media url name ends##################


########################## LostVehicle url begins####################
lostVehicle_list = LostVehicleViewSet.as_view({"get":"list"})
lostVehicle_create = LostVehicleViewSet.as_view({"post":"create"})
lostVehicle_get = LostVehicleViewSet.as_view({"get":"retrieve"})
lostVehicle_delete = LostVehicleViewSet.as_view({"delete":"destroy"})
lostVehicle_update = LostVehicleViewSet.as_view({"patch":"update"})
######################### LostVehicle url name ends##################






