from components.screen import AppScreen
from components.labels import NormalLabel
from components.text_input import BasicTextInput
from components.webfont import fa_icon

from service import api_client
from service import websock

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

class DynamicHeightTextInput(BasicTextInput):

    def insert_text(self, substring, from_undo=False):
        result = BasicTextInput.insert_text(self, substring, from_undo=from_undo)
        self.refresh_height()
        return result

    def refresh_height(self):
        self.height = self.line_height * min(self.max_lines, int(len(self.text.split('\n')))) + self.text_padding_y * 2


class ChatMessageLabel(NormalLabel):
    pass


class PrivateChatScreen(AppScreen):

    def __init__(self, **kwargs):
        self.global_id = kwargs.pop('global_id', '')
        self.recipient_id = 'master${}'.format(self.global_id)
        self.username = kwargs.pop('username', '')
        super(PrivateChatScreen, self).__init__(**kwargs)

    def get_title(self):
        return f"{fa_icon('comment', with_spaces=False)} {self.username}"

    def on_enter(self, *args):
        self.control().add_callback('on_private_message_received', self.on_private_message_received)
        self.populate()

    def on_leave(self, *args):
        self.control().remove_callback('on_private_message_received', self.on_private_message_received)

    def populate(self, **kwargs):
        api_client.message_history(
            recipient_id=self.recipient_id,
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
        msg_list = list(reversed(websock.response_result(resp)))
        if _Debug:
            print('on_message_history_result', len(msg_list))
        for item in msg_list:
            msg_id = item['doc']['payload']['message_id']
            msg = item['doc']['payload']['data']['message']
            sender = item['doc']['sender']['glob_id'].replace('master$', '')
            direction = item['doc']['direction']
            if current_direction is None:
                current_direction = direction
            if current_sender is None:
                current_sender = sender
            sender_name, sender_host = current_sender.split('@')
            if current_direction == direction:
                current_messages.append(msg)
            else:
                if current_direction == 'in':
                    self.ids.chat_messages.add_widget(ChatMessageLabel(
                        id=msg_id,
                        text='[color=#3f4eda]{}[/color][color=#b0b0b0]@{}[/color]\n{}'.format(sender_name, sender_host, '\n'.join(current_messages)),
                    ))
                else:
                    self.ids.chat_messages.add_widget(ChatMessageLabel(
                        id=msg_id,
                        text='[color=#00b11c]{}[/color][color=#b0b0b0]@{}[/color]\n{}'.format(sender_name, sender_host, '\n'.join(current_messages)),
                    ))
                current_direction = direction
                current_sender = sender
                sender_name, sender_host = current_sender.split('@')
                current_messages = []
                current_messages.append(msg)
        if current_messages:
            if current_direction == 'in':
                self.ids.chat_messages.add_widget(ChatMessageLabel(
                    id=msg_id,
                    text='[color=#3f4eda]{}[/color][color=#b0b0b0]@{}[/color]\n{}'.format(sender_name, sender_host, '\n'.join(current_messages)),
                ))
            else:
                self.ids.chat_messages.add_widget(ChatMessageLabel(
                    id=msg_id,
                    text='[color=#00b11c]{}[/color][color=#b0b0b0]@{}[/color]\n{}'.format(sender_name, sender_host, '\n'.join(current_messages)),
                ))
        self.ids.chat_messages_view.scroll_y = 0

    def on_chat_send_button_clicked(self, *args):
        api_client.message_send(
            recipient_id=self.recipient_id,
            data={'message': self.ids.chat_input.text, },
            cb=self.on_message_sent,
        )
        self.ids.chat_input.text = ''
        self.ids.chat_input.refresh_height()

    def on_message_sent(self, resp):
        if not websock.is_ok(resp):
            return
        if _Debug:
            print('on_message_sent', resp)
        self.populate()

    def on_private_message_received(self, json_data):
        if _Debug:
            print('chat.on_private_message_received', json_data)
        self.populate()

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder
Builder.load_file('./screens/screen_private_chat.kv')
