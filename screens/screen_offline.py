from kivy.uix.screenmanager import Screen


KVDisconnectedScreen = """
<DisconnectedScreen>:
    Label:
        color: 0, 0, 0, 1 
        markup: True
        text: '[size=14]offline[/size]'

"""

class DisconnectedScreen(Screen):
    pass
