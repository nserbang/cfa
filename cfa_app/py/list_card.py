from kivymd.app import MDApp
from kivy.properties import StringProperty, ListProperty
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.animation import Animation

from kivymd.uix.fitimage import FitImage
from kivymd.uix.swiper import MDSwiperItem
from kivy.uix.videoplayer import VideoPlayer


class Video_Player(VideoPlayer):
    #state='play'
    #options = {'eos': 'loop'}
    allow_stretch=True



class ListingCard(MDCard):

    is_expanded = False

    case_list = ListProperty()

    case_no = StringProperty()
    comp_type = StringProperty()
    time = StringProperty()
    status = StringProperty()
    station = StringProperty()
    officer = StringProperty()
    
    para_case = StringProperty()

    all_paragraph = StringProperty()

    case_img = StringProperty()

    likes_no = StringProperty()

    comments_no = StringProperty()
    
    adaptive_height= True

    media_list = ListProperty()

    def expand_paragraph(self):
        self.is_expanded = not self.is_expanded
        card_layout = self.ids.paragraph_lbl

        if self.is_expanded:

            self.ids.paragraph_lbl.text = self.all_paragraph
            #lbl = MDLabel(text=f"{self.all_paragraph}", color=(0,0,0,1), font_size=0, size_hint=(1, None), height=0)
            #card_layout.add_widget(lbl)


            self.animate_label(self.ids.paragraph_lbl)

        else:
            self.ids.paragraph_lbl.text = self.all_paragraph[:100]
            #self.height = 420
            #self.ids.paragraph_lbl.height = '20sp'

            Animation(height = 20, font_size=15, duration=0.3).start(self.ids.paragraph_lbl) 
            Animation(height=420,  duration=0.3).start(self)



    def animate_label(self, lbl):
        Animation(size=lbl.size, height = 150, font_size=15, duration=0.3).start(lbl) 
        #self.size_hint_y=None
        Animation(height=420+ 150,  duration=0.3).start(self)


    def show_case_details(self):
        app_inst = MDApp.get_running_app()
        case_details_scr = app_inst.home_screen.case_details_screen

        case_details_scr.case_list = self.case_list

        case_details_scr.case_no_field = self.case_no
        case_details_scr.comp_type_field = self.comp_type
        case_details_scr.time_field = self.time
        case_details_scr.status_field = self.status
        case_details_scr.station_field = self.station
        case_details_scr.officer_field = self.officer
        case_details_scr.all_paragraph_field = self.all_paragraph
        
        case_details_scr.manager.current = 'case_details_scr'


    def fill_media_swiper(self):
        self.ids.media_swiper.clear_widgets()

        for media_file in self.media_list:

            swiper_item =  MDSwiperItem()

            if media_file.lower().endswith(('.png', '.jpg', '.jpeg')):

                img = FitImage(source='media/{}'.format(media_file), radius=[20,0])

                swiper_item.add_widget(img)

                self.ids.media_swiper.add_widget(swiper_item)

            elif media_file.lower().endswith(('.mkv', '.avi', '.mp4')):

                video = Video_Player(source='media/{}'.format(media_file))
                swiper_item.add_widget(video)

                self.ids.media_swiper.add_widget(swiper_item)


        if self.media_list == []:
            self.ids.media_swiper.height = 0
            self.height = 420-150 # new height