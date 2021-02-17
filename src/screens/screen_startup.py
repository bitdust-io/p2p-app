from components import screen

#------------------------------------------------------------------------------

class StartUpScreen(screen.AppScreen):

    def get_icon(self):
        return 'progress-clock'

    def get_title(self):
        return 'initializing...'

    def is_closable(self):
        return False
