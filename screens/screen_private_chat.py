from components.screen import AppScreen
from components.text_input import BasicTextInput
from components.webfont import fa_icon

#------------------------------------------------------------------------------

class PrivateChatScreen(AppScreen):

    def __init__(self, **kwargs):
        self.global_id = kwargs.pop('global_id', '')
        self.username = kwargs.pop('username', '')
        super(PrivateChatScreen, self).__init__(**kwargs)

    def get_title(self):
        return f"{fa_icon('comment', with_spaces=False)} {self.username}"


class DynamicHeightTextInput(BasicTextInput):

    def insert_text(self, substring, from_undo=False):
        result = BasicTextInput.insert_text(self, substring, from_undo=from_undo)
        self.height = self.line_height * min(self.max_lines, int(len(self.text.split('\n')))) + self.text_padding_y * 2
        return result

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder
Builder.load_file('./screens/screen_private_chat.kv')
