from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition
from kivy.properties import ObjectProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelOneLine

from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.tab import MDTabsBase


class Tab(MDFloatLayout, MDTabsBase):
    '''Class implementing content for a tab.'''




class Title_Content_1(MDBoxLayout):
    '''Custom content.'''

class Title_Content_2(MDBoxLayout):
    '''Custom content.'''
    
    
class Drugs_Screen(Screen):
    def __init__(self, **kwargs):
        super(Drugs_Screen, self).__init__(**kwargs)
        
        # Add Title 1 ExpansionPanel
        self.ids.box.add_widget(
            MDExpansionPanel(
                icon="format-title",
                content=Title_Content_1(),
                panel_cls=MDExpansionPanelOneLine(
                text="Title 1",
                )
            )    
        )

        # Add Location ExpansionPanel
        self.ids.box.add_widget(
            MDExpansionPanel(
                icon="format-title",
                content=Title_Content_2(),
                panel_cls=MDExpansionPanelOneLine(
                text="Title 2",
                )
            )    
        )


class Extortion_Screen(Screen):
    pass

class Theft_Screen(Screen):
    pass


class Information_Screen(Screen):


    def __init__(self, **kwargs):
        super(Information_Screen, self).__init__(**kwargs)


        self.drugs_screen = Drugs_Screen()
        self.extortion_screen = Extortion_Screen()
        self.theft_screen = Theft_Screen()


        self.ids.info_sm.add_widget(self.drugs_screen)
        self.ids.info_sm.add_widget(self.extortion_screen)
        self.ids.info_sm.add_widget(self.theft_screen)


    def on_tab_switch(self, instance_tabs, instance_tab, instance_tab_label, tab_name):

        if tab_name == 'Drugs':
            self.ids.info_sm.current = 'drugs_scr'
        elif tab_name == 'Extortion':
            self.ids.info_sm.current = 'extortion_scr'
        else:
            self.ids.info_sm.current = 'theft_scr'


        
