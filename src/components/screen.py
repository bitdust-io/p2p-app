from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty  # @UnresolvedImport

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------


class AppScreen(Screen):

    title = StringProperty('')

    def __init__(self, **kw):
        super(AppScreen, self).__init__(**kw)
        if _Debug:
            print('screen %r created' % self.name)

    def get_title(self):
        return self.title

    def is_closable(self):
        return True

    def app(self):
        return App.get_running_app()

    def main_win(self):
        return self.app().main_window

    def scr_manager(self):
        return self.main_win().ids.screen_manager

    def control(self):
        return self.app().control

    def on_opened(self):
        pass

    def on_closed(self):
        pass
