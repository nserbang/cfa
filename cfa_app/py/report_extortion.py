from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition
from kivy.properties import ObjectProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelOneLine


class Video_Photo_Content(MDBoxLayout):
    '''Custom content.'''


class Location_Content(MDBoxLayout):
    '''Custom content.'''


class Details_Content(MDBoxLayout):
    '''Custom content.'''



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
