from kivy.properties import BooleanProperty  # @UnresolvedImport
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager

from kivymd.uix.chip import MDChip
from kivymd.uix.button import MDFillRoundFlatIconButton

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

class ScreenManagement(ScreenManager):
    pass

#------------------------------------------------------------------------------

class NavButtonWrap(GridLayout):

    selected = BooleanProperty(False)

    def __init__(self, **kwargs):
        self.screen = kwargs.pop('screen')
        self.nav_btn_text = kwargs.pop('text')
        super(NavButtonWrap, self).__init__(**kwargs)

    def get_main_window(self):
        return self.parent.parent.parent

    def get_screen_manager(self):
        return self.get_main_window().ids.screen_manager

    def on_action_area_pressed(self):
        self.get_main_window().select_screen(self.screen)


class NavButtonCloseArea(Button):
    pass


class NavButtonActiveOld(NavButtonWrap):
    pass


class NavButtonClosableOld(NavButtonWrap):

    def on_close_area_pressed(self):
        prev_screen_name = self.get_screen_manager().previous()
        if _Debug:
            print('on_close_area_pressed', prev_screen_name)
        if prev_screen_name:
            self.get_main_window().select_screen(prev_screen_name)
        self.get_main_window().close_screen(self.screen)

#------------------------------------------------------------------------------

class NavButtonBase(MDFillRoundFlatIconButton):

    selected = BooleanProperty(False)

    def __init__(self, **kwargs):
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
