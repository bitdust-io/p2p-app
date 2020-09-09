from kivy.uix.screenmanager import Screen

from components.webfont import fa_icon

KVPrivateChatScreen = """
<PrivateChatScreen>:
    BoxLayout:
        orientation: 'vertical'
        size_hint: 1, 1
        Label:
            color: 0, 0, 0, 1 
            markup: True
            text: '[size=24]bla \\n bla bla[/size]'
        BoxLayout:
            orientation: 'horizontal'
            height: 60
            size_hint: 1, None
            TextInput:
                id: chat_input
                size_hint: 1, 1
            Button:
                width: 60
                height: 60
                size_hint: None, None
                text: 'send'

"""

class PrivateChatScreen(Screen):

    def get_title(self):
        return f"{fa_icon('comment')} Alice"
