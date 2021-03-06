from components import screen
from components import labels
from components import snackbar

from lib import colorhash
from lib import api_client
from lib import websock

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

class GroupChatScreen(screen.AppScreen):

    def __init__(self, **kwargs):
        self.global_id = ''
        self.label = ''
        super(GroupChatScreen, self).__init__(**kwargs)

    def init_kwargs(self, **kw):
        if not self.global_id and kw.get('global_id'):
            self.global_id = kw.pop('global_id', '')
        if not self.label and kw.get('label'):
            self.label = kw.pop('label', '')
        return kw

    def get_icon(self):
        return 'comment'

    def get_title(self):
        l = self.label
        if len(l) > 20:
            l = l[:20] + '...'
        return l

    def get_dropdown_menu_items(self):
        return [
            {'text': 'activate', },
            {'text': 'deactivate', },
            {'text': 'reconnect', },
            {'text': 'close', },
        ]

    def on_enter(self, *args):
        self.ids.chat_status_label.text = ''
        self.control().add_callback('on_group_message_received', self.on_group_message_received)
        self.populate()

    def on_leave(self, *args):
        self.control().remove_callback('on_group_message_received', self.on_group_message_received)

    def populate(self, **kwargs):
        api_client.message_history(
            recipient_id=self.global_id,
            message_type='group_message',
            cb=self.on_message_history_result,
        )

    def on_message_history_result(self, resp):
        self.ids.chat_status_label.from_api_response(resp)
        if not websock.is_ok(resp):
            return
        self.ids.chat_messages.clear_widgets()
        current_sender = None
        current_messages = []
        msg_list = list(websock.response_result(resp))
        if _Debug:
            print('on_message_history_result', len(msg_list))
        for item in msg_list:
            msg_id = item['doc']['payload']['message_id']
            msg = item['doc']['payload']['data']['message']
            sender = item['doc']['sender']['glob_id']
            if current_sender is None:
                current_sender = sender
            sender_name, sender_host = current_sender.split('@')
            if current_sender == sender:
                current_messages.append(msg)
            else:
                sender_clr = colorhash.ColorHash(sender_name).hex
                self.ids.chat_messages.add_widget(labels.ChatMessageLabel(
                    text='[color={}]{}[/color]\n{}'.format(sender_clr, sender_name, '\n'.join(current_messages)),
                ))
                current_sender = sender
                sender_name, sender_host = current_sender.split('@')
                current_messages = []
                current_messages.append(msg)
        if current_messages:
            sender_clr = colorhash.ColorHash(sender_name).hex
            self.ids.chat_messages.add_widget(labels.ChatMessageLabel(
                text='[color={}]{}[/color]\n{}'.format(sender_clr, sender_name, '\n'.join(current_messages)),
            ))
        self.ids.chat_messages_view.scroll_y = 0

    def on_chat_send_button_clicked(self, *args):
        msg = self.ids.chat_input.text
        if _Debug:
            print('on_chat_send_button_clicked', self.global_id, msg)
        api_client.message_send_group(
            group_key_id=self.global_id,
            data={'message': msg, },
            cb=self.on_group_message_sent,
        )
        self.ids.chat_status_label.text = ''
        self.ids.chat_input.text = ''
        self.ids.chat_input.refresh_height()

    def on_group_message_sent(self, resp):
        if _Debug:
            print('on_group_message_sent', resp)
        if not websock.is_ok(resp):
            self.ids.chat_status_label.text = '[color=#f00]%s[/color]' % (', '.join(websock.response_errors(resp)))
            return
        self.populate()

    def on_group_message_received(self, json_data):
        if _Debug:
            print('on_group_message_received', json_data)
        self.populate()

    def on_invite_user_button_clicked(self, *args):
        if _Debug:
            print('on_invite_user_button_clicked')
        self.main_win().select_screen(
            screen_id='select_friend_screen',
            result_callback=self.on_user_selected,
            screen_header='Invite user to the group'
        )

    def on_user_selected(self, user_global_id):
        if _Debug:
            print('on_user_selected', user_global_id)
        self.main_win().select_screen(
            screen_id=self.global_id,
            screen_type='group_chat_screen',
            global_id=self.global_id,
            label=self.label,
        )
        self.main_win().close_screen('select_friend_screen')
        api_client.group_share(
            group_key_id=self.global_id,
            trusted_user_id=user_global_id,
            cb=lambda resp: self.on_group_share_result(resp, user_global_id),
        )

    def on_group_share_result(self, resp, user_global_id):
        if _Debug:
            print('on_group_share_result', resp)
        if websock.is_ok(resp):
            snackbar.success(text='group key shared with %s' % user_global_id)
        else:
            snackbar.error(text=websock.response_errors(resp))

    def on_dropdown_menu_item_clicked(self, menu_inst, item_inst):
        if item_inst.text == 'activate':
            api_client.group_join(
                group_key_id=self.global_id,
                cb=self.on_group_join_result,
            )
        elif item_inst.text == 'deactivate':
            api_client.group_leave(
                group_key_id=self.global_id,
                erase_key=False,
                cb=self.on_group_leave_result,
            )
        elif item_inst.text == 'close':
            api_client.group_leave(
                group_key_id=self.global_id,
                erase_key=True,
                cb=self.on_group_close_result,
            )

    def on_group_join_result(self, resp):
        if not websock.is_ok(resp):
            snackbar.error(text='failed to join the group: %s' % websock.response_errors(resp))
        else:
            snackbar.success(text='group activated')

    def on_group_leave_result(self, resp):
        if not websock.is_ok(resp):
            snackbar.error(text='failed to deactivate the group: %s' % websock.response_errors(resp))
        else:
            snackbar.success(text='group deactivated')

    def on_group_close_result(self, resp):
        if not websock.is_ok(resp):
            snackbar.error(text='failed to close the group: %s' % websock.response_errors(resp))
        else:
            snackbar.success(text='group closed')

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder
Builder.load_file('./screens/screen_group_chat.kv')
