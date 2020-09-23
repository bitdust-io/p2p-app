from kivy.uix.button import Button

#------------------------------------------------------------------------------

from components.screen import AppScreen

#------------------------------------------------------------------------------

class MainMenuButton(Button):

    pass


class MainMenuScreen(AppScreen):

    pass


from kivy.lang.builder import Builder 
Builder.load_file('./screens/screen_main_menu.kv')
