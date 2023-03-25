from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition
from kivy.properties import ObjectProperty



class Report_Stolen_Screen(Screen):

    def submit_clicked(self):
        print('Submit Clicked')
