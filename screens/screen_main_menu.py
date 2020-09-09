from kivy.app import App

from kivy.uix.screenmanager import Screen

from components import buttons


KVMainMenuScreen = """
<MainMenuScreen>:
    GridLayout:
        cols: 1
        padding: 10
        spacing: 2
        row_force_default: True
        row_default_height: 40
        Button:
            text: 'menuA'
            # on_press: root.on_menu_item_clicked()
"""

class MainMenuScreen(Screen):

    def get_title(self):
        return 'menu'
