from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition


class Otp_Screen(Screen):

    def verify_otp_clicked(self):
        otp_no = self.ids.otp_box.text
       
        self.show_message_box(otp_no)

        #self.manager.current = 'login_scr'

    def on_enter(self, *args):
        self.ids.otp_box.text = ""
    
    def back_clicked(self):
        self.manager.current = 'register_scr'

    def show_message_box(self, *args):
        otp_no = str(args)
        print(" OTP Entered : ",otp_no)
        
        self.result = False
        self.message = "OTP verification failed. Try again"
        self.result  = self.otp_verification(otp_no)  
        if self.result == True:
            self.message = "OTP verification successful"

        self.dialog = MDDialog(
            title="[u]OTP Verification[/u]",
            text= str(self.message),
            size_hint=(0.8, 1),
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=self.close_message_box
                )
            ]
        )
        self.dialog.open()
    
    def close_message_box(self, *args):        
        self.dialog.dismiss(force=True)
        if self.result == True:
            self.manager.current = 'login_scr'
        else:
            self.ids.otp_box.text = ""

    def otp_verification(self, otp):
        # implement rest api call logic to verify otp
        restul = True # TO DO. Replace this line with actual api call code
        return restul