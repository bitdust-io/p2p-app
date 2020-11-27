from kivy.properties import BooleanProperty  # @UnresolvedImport
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.button import BaseRectangularButton, BaseRaisedButton, BasePressedButton
from kivymd.uix.label import MDIcon, MDLabel
from kivymd.uix.behaviors.elevation import RectangularElevationBehavior

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

class ScreenManagement(ScreenManager):
    pass


class NavLabel(MDLabel):
    pass

class NavCloseIcon(MDIcon, ButtonBehavior):
    pass


class NavBaseRectangularButton(BaseRectangularButton):

    icon_left_size = 16
    increment_width = dp(1)
    _radius = dp(3)
    _height = dp(24)


class NavButtonBase(NavBaseRectangularButton, RectangularElevationBehavior, BaseRaisedButton, BasePressedButton):

    selected = BooleanProperty(False)

    def __init__(self, **kwargs):
        self.button_label = True
        self.screen = kwargs.pop('screen')
        self.text = kwargs.pop('text')
        self.icon = kwargs.pop('icon')
        super(NavButtonBase, self).__init__(**kwargs)

    def get_main_window(self):
        return self.parent.parent.parent

    def get_screen_manager(self):
        return self.get_main_window().ids.screen_manager

    def on_action_area_pressed(self):
        self.get_main_window().select_screen(self.screen)


class NavButtonActive(NavButtonBase):
    pass


class NavButtonClosable(NavButtonBase):

    icon_right_size = 16

    def on_close_area_pressed(self):
        prev_screen_name = self.get_screen_manager().previous()
        if _Debug:
            print('on_close_area_pressed', prev_screen_name)
        if prev_screen_name:
            self.get_main_window().select_screen(prev_screen_name)
        self.get_main_window().close_screen(self.screen)


#------------------------------------------------------------------------------

from kivy.lang.builder import Builder
Builder.load_file('./components/navigation.kv')
