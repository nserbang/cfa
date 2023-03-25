from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition
from kivy.properties import ObjectProperty
from kivymd.uix.scrollview import MDScrollView

from py.user_home import User_Home_Screen
from py.edit_profile import Edit_Profile_Screen
from py.change_password import Change_Password_Screen

class ContentNavigationDrawer(MDScrollView):
    screen_manager = ObjectProperty()
    nav_drawer = ObjectProperty()


class Home_Screen(Screen):

    def on_enter(self):

        self.user_home_screen = User_Home_Screen()
        self.edit_profile_screen = Edit_Profile_Screen()
        self.change_password_screen = Change_Password_Screen()
        
        self.ids.screen_manager.add_widget(self.user_home_screen)
        self.ids.screen_manager.add_widget(self.edit_profile_screen)
        self.ids.screen_manager.add_widget(self.change_password_screen)




