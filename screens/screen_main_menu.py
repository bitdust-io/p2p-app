from components.screen import AppScreen


KVMainMenuScreen = """
<MainMenuScreen>:
    GridLayout:
        cols: 3
        padding: 10
        spacing: 10
        row_force_default: True
        row_default_height: 40
        Button:
            text: 'menuA'
        Button:
            text: 'menuB'
        Button:
            text: 'menuC'
        Button:
            text: 'menuD'
        Button:
            text: 'menuE'
"""

class MainMenuScreen(AppScreen):

    def get_title(self):
        return 'menu'
