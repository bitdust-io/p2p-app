from kivy.uix.screenmanager import Screen

class AppScreen(Screen):

    def __init__(self, **kw):
        super(AppScreen, self).__init__(**kw)

    def get_title(self):
        return self.name
