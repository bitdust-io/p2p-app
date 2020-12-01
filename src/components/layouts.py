from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivymd.uix.boxlayout import BoxLayout

#------------------------------------------------------------------------------

class HorizontalLayout(BoxLayout):
    pass


class HLayout(HorizontalLayout):
    pass


class VerticalLayout(BoxLayout):
    pass


class VLayout(BoxLayout):
    pass


class HEmptySpace(Widget):
    pass


class VEmptySpace(Widget):
    pass


class VerticalScrollView(ScrollView):
    pass

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./components/layouts.kv')
