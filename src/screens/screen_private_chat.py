from lib import colorhash
from lib import api_client
from lib import websock

from components import screen
from components import labels
from components import snackbar

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

class PrivateChatScreen(screen.AppScreen):

    def __init__(self, **kwargs):
        self.global_id = ''
        self.recipient_id = ''
        self.username = ''
        self.automat_index = None
        super(PrivateChatScreen, self).__init__(**kwargs)

    def init_kwargs(self, **kw):
        if 'global_id' in kw:
            self.global_id = kw.pop('global_id', '')
        self.recipient_id = self.global_id
        if not self.recipient_id.count('$'):
            self.recipient_id = 'master${}'.format(self.recipient_id)
        if 'username' in kw:
            self.username = kw.pop('username', '')
        if 'automat_index' in kw:
            self.automat_index = kw.pop('automat_index', None)
        return kw

    def get_icon(self):
        return ''

    def get_title(self):
        return self.username

    def on_enter(self, *args):
        self.ids.state_panel.attach(self.automat_index)
        self.control().add_callback('on_private_message_received', self.on_private_message_received)
        self.populate()

    def on_leave(self, *args):
        self.ids.state_panel.release()
        self.control().remove_callback('on_private_message_received', self.on_private_message_received)

    def populate(self, **kwargs):
        api_client.message_history(
            recipient_id=self.recipient_id,
            message_type='private_message',
            cb=self.on_message_history_result,
        )

    def on_message_history_result(self, resp):
        if not websock.is_ok(resp):
            snackbar.error(text='failed reading message history: %s' % websock.response_err(resp))
            return
        self.ids.chat_messages.clear_widgets()
        current_direction = None
        current_sender = None
        current_messages = []
        msg_list = list(websock.response_result(resp))
        if _Debug:
            print('PrivateChatScreen.on_message_history_result', len(msg_list))
        for item in msg_list:
            msg = item['doc']['payload']['data']['message']
            sender = item['doc']['sender']['glob_id'].replace('master$', '')
            direction = item['doc']['direction']
            if current_direction is None:
                current_direction = direction
            if current_sender is None:
                current_sender = sender
            sender_name, _ = current_sender.split('@')
            if current_direction == direction:
                current_messages.append(msg)
            else:
                if current_direction == 'in':
                    sender_clr = colorhash.ColorHash(sender_name).hex
                    self.ids.chat_messages.add_widget(labels.ChatMessageLabel(
                        text='[color={}]{}[/color]\n{}'.format(sender_clr, sender_name, '\n'.join(current_messages)),
                    ))
                else:
                    sender_clr = colorhash.ColorHash(sender_name).hex
                    self.ids.chat_messages.add_widget(labels.ChatMessageLabel(
                        text='[color={}]{}[/color]\n{}'.format(sender_clr, sender_name, '\n'.join(current_messages)),
                    ))
                current_direction = direction
                current_sender = sender
                sender_name, _ = current_sender.split('@')
                current_messages = []
                current_messages.append(msg)
        if current_messages:
            if current_direction == 'in':
                sender_clr = colorhash.ColorHash(sender_name).hex
                self.ids.chat_messages.add_widget(labels.ChatMessageLabel(
                    text='[color={}]{}[/color]\n{}'.format(sender_clr, sender_name, '\n'.join(current_messages)),
                ))
            else:
                sender_clr = colorhash.ColorHash(sender_name).hex
                self.ids.chat_messages.add_widget(labels.ChatMessageLabel(
                    text='[color={}]{}[/color]\n{}'.format(sender_clr, sender_name, '\n'.join(current_messages)),
                ))
        self.ids.chat_messages_view.scroll_y = 0

    def on_chat_send_button_clicked(self, *args):
        msg = self.ids.chat_input.text
        if _Debug:
            print('PrivateChatScreen.on_chat_send_button_clicked', self.recipient_id, msg)
        api_client.message_send(
            recipient_id=self.recipient_id,
            data={'message': msg, },
            cb=self.on_message_sent,
        )
        self.ids.chat_input.text = ''
        self.ids.chat_input.refresh_height()

    def on_message_sent(self, resp):
        if _Debug:
            print('PrivateChatScreen.on_message_sent', resp)
        if not websock.is_ok(resp):
            snackbar.error(text='message was not sent: %s' % websock.response_err(resp))
            return
        self.populate()

    def on_private_message_received(self, json_data):
        if _Debug:
            print('PrivateChatScreen.on_private_message_received', json_data)
        self.populate()

    def on_action_button_clicked(self, btn):
        if _Debug:
            print('PrivateChatScreen.on_action_button_clicked', btn.icon)
        self.ids.action_button.close_stack()
        if btn.icon == 'trash-can-outline':
            api_client.friend_remove(global_user_id=self.recipient_id, cb=self.on_friend_remove_result)

    def on_friend_remove_result(self, resp):
        if _Debug:
            print('PrivateChatScreen.on_friend_remove_result', resp)
        if not websock.is_ok(resp):
            snackbar.error(text='contact was not deleted: %s' % websock.response_err(resp))
            return
        self.main_win().select_screen('friends_screen')
