import os
import hashlib
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition

class Register_Screen(Screen):

    def register_clicked(self):
        name = self.ids.name_box.text
        phone = self.ids.phone_box.text
        password = self.ids.pass_box.text
        if self.register_user(name, phone,password):
            self.manager.current = "otp_scr"
        else:
            # Handle error
            print(" Error messages")

    def back_clicked(self):
        self.manager.current = 'login_scr' 
    
    def register_user(self, name, phone, password):
        result = True
        #TO DO user = get_user(phone) # See if user existed
        # if user is not None:
        salt = os.urandom(16).hex()
        hashed_password = self.hash_password(password,salt)

        # TO DO : send name, phone, hashed_password, salt to server for store.
        # Check status and status and store in result
        return result


    def hash_password(self, password, salt):
        # Combine the password and salt
        password_salt = f"{password}{salt}".encode("utf-8")

        # Hash the combined password and salt using SHA-256
        hashed_password = hashlib.sha256(password_salt).hexdigest()

        return hashed_password


