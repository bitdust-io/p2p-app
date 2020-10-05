from components.screen import AppScreen
from components.labels import NormalLabel
from components.text_input import BasicTextInput
from components.webfont import fa_icon

from service import api_client
from service import websock

#------------------------------------------------------------------------------

class DynamicHeightTextInput(BasicTextInput):

    def insert_text(self, substring, from_undo=False):
        result = BasicTextInput.insert_text(self, substring, from_undo=from_undo)
        self.height = self.line_height * min(self.max_lines, int(len(self.text.split('\n')))) + self.text_padding_y * 2
        return result


class ChatMessageLabel(NormalLabel):
    pass


class PrivateChatScreen(AppScreen):

    def __init__(self, **kwargs):
        self.global_id = kwargs.pop('global_id', '')
        self.username = kwargs.pop('username', '')
        super(PrivateChatScreen, self).__init__(**kwargs)

    def get_title(self):
        return f"{fa_icon('comment', with_spaces=False)} {self.username}"

    def on_enter(self, *args):
        self.populate()

    def populate(self, **kwargs):
        api_client.message_history(
            recipient_id='master${}'.format(self.global_id),
            message_type='private_message',
            cb=self.on_message_history_result,
        )

    def on_message_history_result(self, resp):
        if not websock.is_ok(resp):
            return
        self.ids.chat_messages.clear_widgets()
        current_direction = None
        current_sender = None
        current_messages = []
        for item in reversed(websock.response_result(resp)):
            msg = item['doc']['payload']['data']['message']
            sender = item['doc']['sender']['glob_id'].replace('master$', '')
            direction = item['doc']['direction']
            if current_direction is None:
                current_direction = direction
            if current_sender is None:
                current_sender = sender
            if current_direction == direction:
                current_messages.append(msg)
            else:
                if current_direction == 'in':
                    self.ids.chat_messages.add_widget(ChatMessageLabel(
                        text='[color=#F0B0B0]{}[/color]\n{}'.format(current_sender, '\n'.join(current_messages)),
                    ))
                else:
                    self.ids.chat_messages.add_widget(ChatMessageLabel(
                        text='[color=#B0F0B0]{}[/color]\n{}'.format(current_sender, '\n'.join(current_messages)),
                    ))
                current_direction = direction
                current_sender = sender
                current_messages = []
                current_messages.append(msg)
        if current_messages:
            if current_direction == 'in':
                self.ids.chat_messages.add_widget(ChatMessageLabel(
                    text='[color=#F0B0B0]{}[/color]\n{}'.format(current_sender, '\n'.join(current_messages)),
                ))
            else:
                self.ids.chat_messages.add_widget(ChatMessageLabel(
                    text='[color=#B0F0B0]{}[/color]\n{}'.format(current_sender, '\n'.join(current_messages)),
                ))

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder
Builder.load_file('./screens/screen_private_chat.kv')
