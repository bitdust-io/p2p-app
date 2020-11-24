from kivy.uix.scrollview import ScrollView
from kivymd.uix.boxlayout import BoxLayout

#------------------------------------------------------------------------------

class HorizontalLayout(BoxLayout):
    pass


class VerticalLayout(BoxLayout):
    pass


class VerticalScrollView(ScrollView):
    pass

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./components/layouts.kv')
