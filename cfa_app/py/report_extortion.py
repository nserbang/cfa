from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition
from kivy.properties import ObjectProperty, StringProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelOneLine
from kivy.uix.modalview import ModalView
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineIconListItem

from kivy_garden.mapview import MapView, MapMarker

class Item(OneLineIconListItem):
    divider = None
    source = StringProperty()

class Video_Photo_Content(MDBoxLayout):

    camera_popup = None

    def capture_img(self, instance):
        self.camera_popup = Camera_Popup()
        self.camera_popup.parent_instance = self
        self.camera_popup.open()    


    def choose_option_photo(self):
        self.dialog = MDDialog(
            title="Select Option",
            type="simple",
            items=[
                Item(text="Gallery", source="folder-multiple-image", on_release=self.choose_img_gallery),
                Item(text="Camera", source="camera", on_release=self.capture_img),
            ],
        )
        self.dialog.open()


    def choose_img_gallery(self, instance):
        pass


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

        # Snack message 
        snack_bar = Snackbar(text="Location is added",
            snackbar_x="10dp",
            snackbar_y="10dp",
            size_hint_x=.8)
        snack_bar.open()
        

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
        self.parent_instance.ids.filename_box.text = filename

        #destroy instance
        self.__del__()



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
        
        

