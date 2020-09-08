from kivy.uix.screenmanager import Screen


KVWelcomeScreen = """
<WelcomeScreen>:
    Label:
        color: 0, 0, 0, 1 
        markup: True
        text: '[size=24]BitDust[/size]'

"""

class WelcomeScreen(Screen):
    pass
