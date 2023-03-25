from kivy.properties import StringProperty, ListProperty
from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel


class Case_Details_Screen(Screen):

    case_list_field = ListProperty()

    case_no_field = StringProperty()
    comp_type_field = StringProperty()
    time_field = StringProperty()
    status_field = StringProperty()
    station_field = StringProperty()
    officer_field = StringProperty()
    
    all_paragraph_field = StringProperty()

