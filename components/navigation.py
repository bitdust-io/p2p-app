from kivy.properties import BooleanProperty  # @UnresolvedImport
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager

#------------------------------------------------------------------------------

class ScreenManagement(ScreenManager):

    pass

#------------------------------------------------------------------------------

class NavButton(GridLayout):

    selected = BooleanProperty(False)

    def __init__(self, **kwargs):
        self.screen = kwargs.pop('screen')
        self.nav_btn_text = kwargs.pop('text')
        super(NavButton, self).__init__(**kwargs)

    def get_main_window(self):
        return self.parent.parent.parent

    def get_screen_manager(self):
        return self.get_main_window().ids.screen_manager

    def on_action_area_pressed(self):
        self.get_main_window().select_screen(self.screen)

#------------------------------------------------------------------------------

class NavClosableButton(NavButton):

    def on_close_area_pressed(self):
        self.get_main_window().close_screen(self.screen)

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./components/navigation.kv')
