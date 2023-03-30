from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition
from kivy.properties import ObjectProperty, StringProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelOneLine
from kivy.uix.modalview import ModalView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineIconListItem

from kivymd.uix.filemanager import MDFileManager
from kivymd.toast import toast

import os
from os.path import exists
from datetime import datetime

from plyer import camera
from kivy_garden.mapview import MapView, MapMarker
#from kivy_garden.xcamera import XCamera

class Item(OneLineIconListItem):
    divider = None
    source = StringProperty()

class Video_Photo_Content(MDBoxLayout):

    camera_popup = None

    video_manager_open = False
    photo_manager_open = False


    """
        Functions of Choose Video Options  (Gallery / Camera)
    """


    def choose_option_video(self):
        self.video_dialog = MDDialog(
            title="Select Video Option",
            type="simple",
            items=[
                Item(text="Gallery", source="folder-multiple-image", on_release=self.show_video_gallery),
                Item(text="Camera", source="camera", on_release=self.capture_video),
            ],
        )
        self.video_dialog.open()


    def show_video_gallery(self, instance):
        # Video File Manager
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            ext=['.mp4']
        )

        path = os.path.expanduser("~")  # path of directory opened file manager
        self.file_manager.show(path)

        self.video_manager_open = True


    def capture_video(self, instance):
        print("Capturing Video has not yet been implemented.")

        # toast message 
        toast("Capturing Video has not yet been implemented.")


    """
        Functions of Choose Photo Options (Gallery / Camera)
    """

    def choose_option_photo(self):
        self.photo_dialog = MDDialog(
            title="Select Image Option",
            type="simple",
            items=[
                Item(text="Gallery", source="folder-multiple-image", on_release=self.show_photo_gallery),
                Item(text="Camera", source="camera", on_release=self.capture_image),
            ],
        )
        self.photo_dialog.open()



    def show_photo_gallery(self, instance):
        # Photo File Manager
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            ext=['.png', '.jpg', '.jpeg'],
            preview=True
        )

        path = os.path.expanduser("~")  # path of directory opened file manager
        self.file_manager.show(path)

        self.photo_manager_open = True


    def capture_image(self, instance):
#        self.camera_popup = Camera_Popup()
#        self.camera_popup.parent_instance = self
#        self.camera_popup.open()    


        ti = datetime.now()
        timestr = ti.strftime("%Y%m%d_%H%M%S")

        filepath = 'IMG_{}.png'.format(timestr)

        if exists(filepath):
            print("Picture with this name already exists!")
            return False
        try:
            camera.take_picture(filename=filepath,
                                on_complete=self.camera_callback)
        except NotImplementedError:
            print("This feature hasn't yet been implemented for this platform.")

            # toast message 
            toast("This feature hasn't yet been implemented for this platform.")


    def camera_callback(self, filepath):
        if exists(filepath):
            print("Picture saved!")
        else:
            print("Could not save your picture!")



    """
        Functions of File Manager (Video / Photo)
    """

    def select_path(self, path: str):

        self.exit_manager()
        toast(path)

        # Path of video choosen from Gallery
        if self.video_manager_open == True:
            self.video_manager_open = False
            
            # video path
            self.gallery_video_path = path
            print('Video Path')
            
        # Path of  choosen from Gallery
        elif self.photo_manager_open == True:
            self.photo_manager_open = False

            # photo path 
            self.gallery_photo_path = path
            print('Photo Path')


    def exit_manager(self, *args):
        '''Called when the user reaches the root of the directory tree.'''

        self.file_manager.close()




class Location_Content(MDBoxLayout):

    marker_inst = None    

    def __init__(self, **kwargs):
        super(Location_Content, self).__init__(**kwargs)

        self.mapview = MapView(zoom=11, lat=31, lon=30.57)
        self.ids.mapview_box.add_widget(self.mapview)


    def add_marker(self):
        lat =  self.mapview.lat
        lon =  self.mapview.lon
        print('add marker')

        # Toast message 
        toast("Location is added")
        

    def remove_marker(self):
        pass

class Details_Content(MDBoxLayout):
    '''Custom content.'''


class Camera_Popup(ModalView):
    parent_instance = None
    
    def capture_clicked(self):
    
        filename ='captured_image.png'
        camera = self.ids.camera
        camera.export_to_png(filename)

        # dismiss popup
        self.dismiss()
        #self.parent_instance.ids.filename_box.text = filename

        #play is False
        camera.play = False



class Report_Extortion_Screen(Screen):

    def __init__(self, **kwargs):
        super(Report_Extortion_Screen, self).__init__(**kwargs)
        
        # Add Video/Photo ExpansionPanel
        self.ids.box.add_widget(
            MDExpansionPanel(
                icon="camera",
                content=Video_Photo_Content(),
                panel_cls=MDExpansionPanelOneLine(
                text="Add Video/Photo",
                )
            )    
        )

        # Add Location ExpansionPanel
        self.ids.box.add_widget(
            MDExpansionPanel(
                icon="map-marker",
                content=Location_Content(),
                panel_cls=MDExpansionPanelOneLine(
                text="Add Location",
                )
            )    
        )



    def submit_clicked(self):
        print('Submit Clicked')
        
    def back_clicked(self):
        self.manager.current = 'user_home_scr'
        
        

