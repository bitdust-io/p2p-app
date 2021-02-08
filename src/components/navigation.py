from kivy.properties import BooleanProperty  # @UnresolvedImport
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.button import BasePressedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.behaviors.elevation import RectangularElevationBehavior
from kivymd.uix.behaviors.backgroundcolor_behavior import SpecificBackgroundColorBehavior

from components.labels import CustomIcon

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

class ScreenManagement(ScreenManager):
    pass


class NavIcon(ButtonBehavior, CustomIcon):
    pass


class NavLabel(ButtonBehavior, MDLabel):
    pass


class NavCloseIcon(ButtonBehavior, CustomIcon):
    pass


class NavBaseRectangularButton(RectangularElevationBehavior, SpecificBackgroundColorBehavior, BasePressedButton):

    icon_left_size = 17
    increment_width = dp(1)
    _radius = dp(2)


class NavButtonBase(NavBaseRectangularButton):

    selected = BooleanProperty(False)

    def __init__(self, **kwargs):
        self.button_label = True
        self.screen = kwargs.pop('screen')
        self.text = kwargs.pop('text')
        self.icon = kwargs.pop('icon')
        super(NavButtonBase, self).__init__(**kwargs)

    def get_main_window(self):
        return self.parent.parent.parent.parent

    def get_screen_manager(self):
        return self.get_main_window().ids.screen_manager

    def on_action_area_pressed(self):
        if _Debug:
            print('NavButtonBase.on_action_area_pressed', self.screen)
        self.get_main_window().select_screen(self.screen)


class NavButtonActive(NavButtonBase):
    pass


class NavButtonClosable(NavButtonBase):

    def on_close_area_pressed(self):
        prev_screen_name = self.get_screen_manager().previous()
        if _Debug:
            print('NavButtonClosable.on_close_area_pressed', prev_screen_name)
        if prev_screen_name:
            self.get_main_window().select_screen(prev_screen_name)
        self.get_main_window().close_screen(self.screen)


#------------------------------------------------------------------------------

from kivy.lang.builder import Builder
Builder.load_file('./components/navigation.kv')
