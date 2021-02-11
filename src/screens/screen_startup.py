from components import screen

#------------------------------------------------------------------------------

class StartUpScreen(screen.AppScreen):

    def get_icon(self):
        return 'progress-clock'

    def get_title(self):
        return 'initializing...'

    def is_closable(self):
        return False

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./screens/screen_startup.kv')
