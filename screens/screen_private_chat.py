from components.screen import AppScreen
from components.webfont import fa_icon


class PrivateChatScreen(AppScreen):

    def get_title(self):
        return f"{fa_icon('comment')} Alice"


from kivy.lang.builder import Builder 
Builder.load_file('./screens/screen_private_chat.kv')
