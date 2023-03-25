from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition


class Otp_Screen(Screen):

    def verify_otp_clicked(self):
        otp_no = self.ids.otp_box.text

        self.manager.current = 'login_scr'


    def back_clicked(self):
        self.manager.current = 'register_scr'

