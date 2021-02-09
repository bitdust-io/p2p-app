from kivy.metrics import dp
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.uix.stacklayout import StackLayout

from kivymd.uix.boxlayout import BoxLayout
from kivymd.theming import ThemableBehavior

#------------------------------------------------------------------------------

class ScreenContainerLayout(BoxLayout):
    pass


class TopEmptyScreenSpace(Widget):
    pass


class HorizontalLayout(BoxLayout):
    pass


class HorizontalWithPaddingLayout(BoxLayout):
    pass


class HLayout(HorizontalLayout):
    pass


class VerticalLayout(BoxLayout):
    pass


class VerticalWithPaddingLayout(BoxLayout):
    pass


class VerticalWithLeftPaddingLayout(BoxLayout):
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


class VerticalScreenLayout(VerticalLayout):
    pass


class VerticalScreenWithPaddingLayout(VerticalLayout):
    pass

#------------------------------------------------------------------------------

class AppScreenLayout(VerticalLayout):
    pass


class HorizontalContainerLayout(HorizontalWithPaddingLayout):
    pass


class PageContainerLayout(VerticalLayout):
    pass


class PageContainerWithPaddingLayout(VerticalLayout):
    pass


class PageContainerWithLeftPaddingLayout(VerticalLayout):
    pass


class ChatContainerLayout(VerticalLayout):
    pass

#------------------------------------------------------------------------------

class VerticalScrollView(ScrollView):
    pass

#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.do_scroll_x = False
#         self.always_overscroll = False
#         self.bar_color = self.theme_cls.primary_light
#         self.bar_inactive_color = (.8, .8, .8, 1)
#         self.bar_width = dp(10)

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./components/layouts.kv')
