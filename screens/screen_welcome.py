from components.screen import AppScreen


KVWelcomeScreen = """
<WelcomeScreen>:
    Label:
        color: 0, 0, 0, 1 
        markup: True
        text: '[size=24]BitDust[/size]'

"""

class WelcomeScreen(AppScreen):

    def get_title(self):
        return 'welcome'
