from kivy.uix.button import Button
from kivy.properties import (
    StringProperty,  # @UnresolvedImport
)

#------------------------------------------------------------------------------

from components.layouts import VerticalLayout
from components.screen import AppScreen
from components.buttons import RaisedIconButton, TransparentIconButton, LabeledIconButton

#------------------------------------------------------------------------------

class MainMenuIconButton(TransparentIconButton):
    pass


class MainMenuButton(LabeledIconButton):
    pass


class MainMenuScreen(AppScreen):
    pass

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./screens/screen_main_menu.kv')
