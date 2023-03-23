from kivy.lang import Builder
from kivy.uix.recycleview import RecycleView
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivymd.uix.list import OneLineListItem

KV = '''
BoxLayout:
    orientation: "vertical"
    spacing: dp(10)

    MDTopAppBar:
        title: "Search"
        md_bg_color: app.theme_cls.primary_color
        background_palette: "Primary"

    MDTextField:
        id: search_field
        hint_text: "Search..."
        pos_hint: {"center_x": 0.5}
        on_text: app.update_search_results(self.text)

    RecycleView:
        id: search_results
        viewclass: 'ScrollView'
        RecycleBoxLayout:
            default_size: None, dp(48)
            default_size_hint: 1, None
            size_hint_y: None
            height: self.minimum_height
            orientation: 'vertical'
            spacing: dp(2)
'''

class SearchApp(MDApp):
    def build(self):
        return Builder.load_string(KV)

    def update_search_results(self, query):
        search_result_list = self.root.ids['search_results']
        search_result_list.clear_widgets()
        search_results = self.search(query)

        for result in search_results:
            item = OneLineListItem(text=result)
            search_result_list.add_widget(item)

    def search(self, query):
        # Implement your search logic here.
        # For demonstration purposes, let's use a sample list of data.
        sample_data = ["apple", "banana", "cherry", "date", "fig", "grape", "kiwi"]

        return [item for item in sample_data if query.lower() in item.lower()]

if __name__ == '__main__':
    SearchApp().run()

