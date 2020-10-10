from components.screen import AppScreen

#------------------------------------------------------------------------------

class WelcomeScreen(AppScreen):

    def get_title(self):
        return 'welcome'

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./screens/screen_welcome.kv')
