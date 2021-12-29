from functools import partial

from kivy.clock import Clock
from kivy.properties import ObjectProperty, NumericProperty  # @UnresolvedImport
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.stacklayout import StackLayout
from kivy.uix.widget import Widget

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

#------------------------------------------------------------------------------

class DelayedResizeLayout(AnchorLayout):

    do_layout_event = ObjectProperty(None, allownone=True)
    layout_delay_s = NumericProperty(0.1)
    root_widget = None
    initialized = False

    def do_layout(self, *args, **kwargs):
        if not self.initialized:
            self.initialized = True
            super().do_layout(*args, **kwargs)
            return
        if self.do_layout_event is not None:
            self.do_layout_event.cancel()
        real_do_layout = super().do_layout
        self.do_layout_event = Clock.schedule_once(lambda dt: real_do_layout(*args, **kwargs), self.layout_delay_s)

    def add_root_widget(self, w):
        self.root_widget = w
        self.add_widget(self.root_widget)
