from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition


class Register_Screen(Screen):

    def register_clicked(self):
        name = self.ids.name_box.text
        phone = self.ids.phone_box.text
        password = self.ids.pass_box.text

        self.manager.current = 'otp_scr'

    def back_clicked(self):
        self.manager.current = 'login_scr'

