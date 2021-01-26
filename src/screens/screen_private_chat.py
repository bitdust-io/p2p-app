from components.screen import AppScreen
from components.labels import ChatMessageLabel

from lib import api_client
from lib import websock

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

class PrivateChatScreen(AppScreen):

    def __init__(self, **kwargs):
        self.global_id = kwargs.pop('global_id', '')
        self.recipient_id = self.global_id
        if not self.recipient_id.count('$'):
            self.recipient_id = 'master${}'.format(self.recipient_id)
        self.username = kwargs.pop('username', '')
        super(PrivateChatScreen, self).__init__(**kwargs)

    def get_icon(self):
        return 'comment'

    def get_title(self):
        return self.username

    def on_enter(self, *args):
        self.ids.chat_status_label.text = ''
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
        self.ids.chat_status_label.from_api_response(resp)
        if not websock.is_ok(resp):
            return
        self.ids.chat_status_label.text = ''
        self.ids.chat_messages.clear_widgets()
        current_direction = None
        current_sender = None
        current_messages = []
        msg_list = list(websock.response_result(resp))
        if _Debug:
            print('on_message_history_result', len(msg_list))
        for item in msg_list:
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
                        text='[color=#3f4eda]{}[/color]\n{}'.format(sender_name, '\n'.join(current_messages)),
                    ))
                else:
                    self.ids.chat_messages.add_widget(ChatMessageLabel(
                        text='[color=#00b11c]{}[/color]\n{}'.format(sender_name, '\n'.join(current_messages)),
                    ))
                current_direction = direction
                current_sender = sender
                sender_name, sender_host = current_sender.split('@')
                current_messages = []
                current_messages.append(msg)
        if current_messages:
            if current_direction == 'in':
                self.ids.chat_messages.add_widget(ChatMessageLabel(
                    text='[color=#3f4eda]{}[/color]\n{}'.format(sender_name, '\n'.join(current_messages)),
                ))
            else:
                self.ids.chat_messages.add_widget(ChatMessageLabel(
                    text='[color=#00b11c]{}[/color]\n{}'.format(sender_name, '\n'.join(current_messages)),
                ))
        self.ids.chat_messages_view.scroll_y = 0

    def on_chat_send_button_clicked(self, *args):
        msg = self.ids.chat_input.text
        if _Debug:
            print('on_chat_send_button_clicked', self.recipient_id, msg)
        api_client.message_send(
            recipient_id=self.recipient_id,
            data={'message': msg, },
            cb=self.on_message_sent,
        )
        self.ids.chat_status_label.text = ''
        self.ids.chat_input.text = ''
        self.ids.chat_input.refresh_height()

    def on_message_sent(self, resp):
        if _Debug:
            print('on_message_sent', resp)
        if not websock.is_ok(resp):
            self.ids.chat_status_label.text = '[color=#f00]%s[/color]' % (', '.join(websock.response_errors(resp)))
            return
        self.populate()

    def on_private_message_received(self, json_data):
        if _Debug:
            print('chat.on_private_message_received', json_data)
        self.populate()

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder
Builder.load_file('./screens/screen_private_chat.kv')
