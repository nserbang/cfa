from kivy.properties import StringProperty
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.animation import Animation

class ListingCard(MDCard):

    is_expanded = False

    case_no = StringProperty()
    comp_type = StringProperty()
    time = StringProperty()
    status = StringProperty()
    station = StringProperty()
    officer = StringProperty()
    
    para_case = StringProperty()


    all_paragraph = StringProperty()

    case_img = StringProperty()
    
    adaptive_height= True
    

    def expand_paragraph(self):
        self.is_expanded = not self.is_expanded
        card_layout = self.ids.paragraph_lbl

        if self.is_expanded:

            self.ids.paragraph_lbl.text = self.all_paragraph
            #lbl = MDLabel(text=f"{self.all_paragraph}", color=(0,0,0,1), font_size=0, size_hint=(1, None), height=0)
            #card_layout.add_widget(lbl)


            self.animate_label(self.ids.paragraph_lbl)

        else:
            self.ids.paragraph_lbl.text = self.all_paragraph[:90]
            self.height = 380
            self.ids.paragraph_lbl.height = '20sp'


    def animate_label(self, lbl):
        Animation(size=lbl.size, height = 150, font_size=15, duration=0.3).start(lbl) 
        #self.size_hint_y=None
        Animation(height=380+ 150,  duration=0.3).start(self)


