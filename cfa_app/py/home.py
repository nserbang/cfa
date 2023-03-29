from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition
from kivy.properties import ObjectProperty
from kivymd.uix.scrollview import MDScrollView

from py.user_home import User_Home_Screen
from py.edit_profile import Edit_Profile_Screen
from py.change_password import Change_Password_Screen
from py.case_details import Case_Details_Screen
from py.emergency import Emergency_Screen
from py.information import Information_Screen
from py.report_stolen import Report_Stolen_Screen
from py.report_extortion import Report_Extortion_Screen

from kivymd.uix.button import MDFloatingActionButtonSpeedDial

class ContentNavigationDrawer(MDScrollView):
    screen_manager = ObjectProperty()
    nav_drawer = ObjectProperty()


class Home_Screen(Screen):

#    data = {
#        'Report Stolen Vehicle': ['plus', "on_release", lambda x: self.switch_screen("stolen_vehicle_scr")],
#        'Report Extortion': ['plus', "on_release", lambda x: self.switch_screen("stolen_vehicle_scr")],
#        'Report Drug Issue': ['plus', "on_release", lambda x: self.switch_screen("stolen_vehicle_scr")]
#    }



    def __init__(self, **kwargs):
        super(Home_Screen, self).__init__(**kwargs)

        self.user_home_screen = User_Home_Screen()
        self.edit_profile_screen = Edit_Profile_Screen()
        self.change_password_screen = Change_Password_Screen()
        
        self.case_details_screen = Case_Details_Screen()
        self.emergency_screen = Emergency_Screen()
        self.information_screen = Information_Screen()

        self.report_stolen_screen = Report_Stolen_Screen()
        self.report_extortion_screen = Report_Extortion_Screen()

        
        self.ids.screen_manager.add_widget(self.user_home_screen)
        self.ids.screen_manager.add_widget(self.edit_profile_screen)
        self.ids.screen_manager.add_widget(self.change_password_screen)

        self.ids.screen_manager.add_widget(self.case_details_screen)
        self.ids.screen_manager.add_widget(self.emergency_screen)
        self.ids.screen_manager.add_widget(self.information_screen)

        self.ids.screen_manager.add_widget(self.report_stolen_screen)
        self.ids.screen_manager.add_widget(self.report_extortion_screen)

    def on_pre_enter(self):
        self.speeddial_btn = MDFloatingActionButtonSpeedDial(
                    id="speed_dial",
                    #hint_animation= True,
                    root_button_anim =True,
                    label_text_color = "black",
                    label_bg_color = "orange"
                )
        self.add_widget(self.speeddial_btn)


        data = {
            'Report Stolen Vehicle': ['plus', "on_release", lambda x: self.switch_screen("report_stolen_scr")],
            'Report Extortion': ['plus', "on_release", lambda x: self.switch_screen("report_extortion_scr")],
            'Report Drug Issue': ['plus', "on_release", lambda x: self.switch_screen("report_drug_scr")]
        }

        self.speeddial_btn.data = data


    def switch_screen(self, screen_name):
        self.speeddial_btn.close_stack()
        self.ids.screen_manager.current = screen_name


