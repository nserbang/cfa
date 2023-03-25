from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition
from kivy.properties import ObjectProperty
from kivymd.uix.scrollview import MDScrollView

from py.list_card import ListingCard
    

class User_Home_Screen(Screen):

    def on_enter(self):
        self.fill_case_list()

    # fill case list
    def fill_case_list(self):
        
        case_list_test = [ ['1','type 1','3/3/2023','Accepted','XYZ Police Station', 'Smith', 'lorem text lorem text lorem text lorem text lorem text lorem text lorem text lorem text lorem text lorem text lorem text lorem text lorem text lorem text lorem text lorem text lorem text lorem text lorem text lorem text lorem text lorem text lorem text lorem text lorem text lorem text lorem text lorem text lorem text lorem text lorem text lorem text lorem text lorem text ' ],
        ['2','type 2','4/3/2023','Accepted','XYZ Police Station', 'Smith', 'lorem text lorem text lorem text lorem text lorem text lorem text ' ],
        ['3','type 3','4/3/2023','Accepted','XYZ Police Station', 'Smith', 'lorem text lorem text lorem text lorem text lorem text lorem text ' ] ]


        for case in case_list_test:

            self.ids.case_list.add_widget(
                ListingCard(
                        case_no = 'Case No.: {}'.format(str(case[0])),
                        comp_type = 'Complaint Type: {}'.format(str(case[1])),
                        time = 'Reported On: {}'.format(str(case[2])),
                        status = 'Status: {}'.format(str(case[3])),
                        station = '{}'.format(str(case[4])),
                        officer = 'Officer: {}'.format(str(case[5])),
                        
                        para_case = str(case[6][:100]),
                        all_paragraph = str(case[6]),
                        
                        likes_no = str(10),
                        comments_no = str(15),
                )
            )





