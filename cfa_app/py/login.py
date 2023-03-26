from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition
import hashlib
import os

class Login_Screen(Screen):
    def login_clicked(self):
        phone = self.ids.phone_box.text
        password = self.ids.pass_box.text
        if (self.verify_user(phone,password)):
            self.manager.current = 'home_scr'
        else:
            print(" User not found ")
        
    def go_to_register_scr(self):
        self.manager.current = 'register_scr'
    
    def verify_user(self, phone, password):
        result = True
        flag, salt = self.get_salt(phone)
        if flag == True:
            password = self.hash_password(password,salt)
        # TO DO : Send query of phone and password to server 
        return result

    def hash_password(self, password, salt):
        # Combine the password and salt
        password_salt = f"{password}{salt}".encode("utf-8")

        # Hash the combined password and salt using SHA-256
        hashed_password = hashlib.sha256(password_salt).hexdigest()

        return hashed_password

    def get_salt(self, phone):
        flag = True
        salt = None
        # TO DO : Send retrieve user/phone and salt from server
        # flag, salt = get_salt_from_server(phone)

        return flag, salt
    
    # TO DO: In order to bypass login screen during development,
    # we are directly loading the home screen. Remove this from production
    #def on_enter(self, *args):
       # self.manager.current = 'user_home_scr'





