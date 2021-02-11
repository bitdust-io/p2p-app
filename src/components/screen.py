from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivymd.theming import ThemableBehavior

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

def my_app():
    return App.get_running_app()


def main_window():
    return my_app().main_window


def toolbar():
    return main_window().ids.toolbar


def manager():
    return main_window().ids.screen_manager


def control():
    return my_app().control

#------------------------------------------------------------------------------

class AppScreen(ThemableBehavior, Screen):

    def __init__(self, **kw):
        kw = self.init_kwargs(**kw)
        kw.pop('id', None)
        if _Debug:
            print('AppScreen.init   %r creating with kwargs=%r' % (kw.get('name'), kw))
        super(AppScreen, self).__init__(**kw)

    def init_kwargs(self, **kw):
        return kw

    def get_icon(self):
        return ''

    def get_icon_pack(self):
        return 'Icons'

    def get_title(self):
        return ''

    def is_closable(self):
        return True

    def app(self):
        return my_app()

    def main_win(self):
        return main_window()

    def scr_manager(self):
        return manager()

    def control(self):
        return control()

    def on_opened(self):
        pass

    def on_closed(self):
        pass

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./components/screen.kv')
