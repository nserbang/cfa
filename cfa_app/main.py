from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.card import MDCard
from kivymd.uix.tab import MDTabsBase
from kivy.properties import StringProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.theming import ThemableBehavior
from kivymd.uix.list import OneLineListItem
from kivymd.uix.list import MDList
from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition
from kivy.metrics import dp
from kivymd.uix.menu import MDDropdownMenu
from functools import partial

from py.login import Login_Screen
from py.register import Register_Screen
from py.otp import Otp_Screen
from py.home import Home_Screen


    
class MainApp(MDApp):

    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        
        self.sm = ScreenManager()
        self.sm.transition = WipeTransition()

        self.login_screen = Login_Screen()
        self.register_screen = Register_Screen()
        self.otp_screen = Otp_Screen()
        self.home_screen = Home_Screen()

        self.sm.add_widget(self.login_screen)
        self.sm.add_widget(self.register_screen)
        self.sm.add_widget(self.otp_screen)
        self.sm.add_widget(self.home_screen)
        
        return self.sm




if __name__ == '__main__':
    app = MainApp()
    app.run()
