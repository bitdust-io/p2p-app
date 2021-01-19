from components.screen import AppScreen

#------------------------------------------------------------------------------

class StartUpScreen(AppScreen):

    def get_icon(self):
        return 'progress-clock'

    def get_title(self):
        return 'initializing...'

    def is_closable(self):
        return False

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./screens/screen_startup.kv')
