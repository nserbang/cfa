from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition


class Change_Password_Screen(Screen):

    def change_pass_clicked(self):
        old_pass = self.ids.old_pass_box.text
        new_pass = self.ids.new_pass_box.text
        confirm_new_pass = self.ids.confirm_pass_box.text


        print('Confirm New Pass')


    def back_clicked(self):
        self.manager.current = 'user_home_scr'

