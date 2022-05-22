from components import screen

#------------------------------------------------------------------------------

class StartUpScreen(screen.AppScreen):

    # def get_icon(self):
    #     return 'progress-clock'

    def get_title(self):
        return 'initializing ...'

    def is_closable(self):
        return False

    def on_enter(self, *args):
        self.ids.state_panel.attach(automat_id='initializer')

    def on_leave(self, *args):
        self.ids.state_panel.release()
