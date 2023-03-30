from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition
from kivy.properties import ObjectProperty
from kivymd.uix.boxlayout import MDBoxLayout


class Terms_Screen(Screen):

    def __init__(self, **kwargs):
        super(Terms_Screen, self).__init__(**kwargs)


        self.ids.terms_box.text = 'Terms and Conditions Content'
