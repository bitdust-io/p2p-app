from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.uix.stacklayout import StackLayout

from kivymd.uix.boxlayout import BoxLayout

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


class HorizontalMinimumHeightLayout(HorizontalLayout):
    pass


class VerticalMinimumWidthLayout(VerticalLayout):
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

class StatusPanelLayout(HorizontalLayout):
    pass

#------------------------------------------------------------------------------

class VerticalScrollView(ScrollView):
    pass
