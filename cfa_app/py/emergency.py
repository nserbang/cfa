from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition
from kivy.properties import ObjectProperty
from kivymd.uix.menu import MDDropdownMenu


from py.call_card import CallCard


class Emergency_Screen(Screen):


    def __init__(self, **kwargs):
        super(Emergency_Screen, self).__init__(**kwargs)


        # dropdown of District        

        district_items = [
            {
                "text": f"Item {i}",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"Item {i}": self.district_callback(x),
            } for i in range(5)
        ]
        self.district_menu = MDDropdownMenu(
            caller=self.ids.district_drop_item,
            items=district_items,
            elevation=4,
            radius=[12, 0, 12, 0],
            width_mult=3,
        )


        # dropdown of Type

        type_items = [
            {
                "text": f"Item {i}",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"Item {i}": self.type_callback(x),
            } for i in range(3)
        ]
        self.type_menu = MDDropdownMenu(
            caller=self.ids.type_drop_item,
            items=type_items,
            elevation=4,
            radius=[12, 0, 12, 0],
            width_mult=3,
        )



    def district_callback(self, text_item):
        self.ids.district_drop_item.text = text_item
        self.district_menu.dismiss()


    def type_callback(self, text_item):
        self.ids.type_drop_item.text = text_item
        self.type_menu.dismiss()


        self.fill_calls_list()





    def fill_calls_list(self):
    
    
    
        calls_list_test = [ ['place 1', 'type 1', 'phone 1', 'km no.'],
                            ['place 2', 'type 2', 'phone 2', 'km no.'],
                            ['place 3', 'type 3', 'phone 3', 'km no.'],
                            ['place 4', 'type 4', 'phone 4', 'km no.']
                          ]
                          

        self.ids.calls_list.clear_widgets()
                          
        for call in calls_list_test:
              self.ids.calls_list.add_widget(
                CallCard(
                    place_type_lbl = '{} - {}'.format(call[0], call[1]),
                    phone_lbl = str(call[2]),
                    km_lbl = '{} Km Away'.format(str(call[3]))
                )
              
              )
