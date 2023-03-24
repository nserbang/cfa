from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition
from kivy.properties import ObjectProperty
from kivymd.uix.scrollview import MDScrollView


class Edit_Profile_Screen(Screen):


    def choose_photo(self):
        print('Choose Photo Clicked')

    def save_clicked(self):
        phone = self.ids.phone_box.text
        name = self.ids.name_box.text
        address = self.ids.address_box.text
        
        print('Profile Saved')
        
      
    def back_clicked(self):
        self.manager.current = 'user_home_scr'
