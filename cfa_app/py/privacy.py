from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition
from kivy.properties import ObjectProperty
from kivymd.uix.boxlayout import MDBoxLayout


class Privacy_Screen(Screen):

    def __init__(self, **kwargs):
        super(Privacy_Screen, self).__init__(**kwargs)


        self.ids.privacy_box.text = 'Privacy Content'
