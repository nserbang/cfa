from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition


class Login_Screen(Screen):
    def login_clicked(self):
        self.manager.current = 'home_scr'
        
    def go_to_register_scr(self):
        self.manager.current = 'register_scr'

