from components.screen import AppScreen
from components.buttons import LabeledIconButton

#------------------------------------------------------------------------------

class MainMenuButton(LabeledIconButton):
    pass


class MainMenuScreen(AppScreen):
    pass

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./screens/screen_main_menu.kv')
