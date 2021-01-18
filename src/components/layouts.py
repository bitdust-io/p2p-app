from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.uix.stacklayout import StackLayout
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


class HorizontalStackLayout(StackLayout):
    pass


class HEmptySpace(Widget):
    pass


class VEmptySpace(Widget):
    pass


class HFixedEmptySpace(Widget):
    pass


class VFixedEmptySpace(Widget):
    pass


class VerticalScrollView(ScrollView):
    scroll_type = ['content', 'bars']
    effect_cls = None

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./components/layouts.kv')
