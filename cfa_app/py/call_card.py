from kivymd.app import MDApp
from kivy.properties import StringProperty, ListProperty
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.animation import Animation

class CallCard(MDCard):

    place_type_lbl = StringProperty()
    phone_lbl = StringProperty()
    km_lbl = StringProperty()

