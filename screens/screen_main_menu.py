from components.screen import AppScreen


class MainMenuScreen(AppScreen):

    def get_title(self):
        return 'menu'


from kivy.lang.builder import Builder 
Builder.load_file('./screens/screen_main_menu.kv')
