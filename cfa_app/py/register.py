from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition


class Register_Screen(Screen):
    def register_clicked(self):
        pass

    def back_clicked(self):
        self.manager.current = 'login_scr'

