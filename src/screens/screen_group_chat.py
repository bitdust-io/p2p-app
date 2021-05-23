from components import screen
from components import labels
from components import snackbar

from lib import colorhash
from lib import api_client
from lib import websock

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

class GroupChatScreen(screen.AppScreen):

    def __init__(self, **kwargs):
        self.global_id = ''
        self.label = ''
        self.automat_index = None
        self.automat_id = None
        super(GroupChatScreen, self).__init__(**kwargs)

    def init_kwargs(self, **kw):
        if not self.global_id and kw.get('global_id'):
            self.global_id = kw.pop('global_id', '')
        if not self.label and kw.get('label'):
            self.label = kw.pop('label', '')
        if 'automat_index' in kw:
            self.automat_index = kw.pop('automat_index', None)
        if 'automat_id' in kw:
            self.automat_id = kw.pop('automat_id', None)
        return kw

    def get_icon(self):
        return 'account-group'

    def get_title(self):
        l = self.label
        if len(l) > 20:
            l = l[:20] + '...'
        return l

    def on_enter(self, *args):
        self.ids.action_button.close_stack()
        self.ids.state_panel.attach(automat_id=self.automat_id)
        self.control().add_callback('on_group_message_received', self.on_group_message_received)
        self.populate()

    def on_leave(self, *args):
        self.ids.action_button.close_stack()
        self.ids.state_panel.release()
        self.control().remove_callback('on_group_message_received', self.on_group_message_received)

    def populate(self, **kwargs):
        api_client.message_history(
            recipient_id=self.global_id,
            message_type='group_message',
            cb=self.on_message_history_result,
        )

    def on_message_history_result(self, resp):
        if not websock.is_ok(resp):
            return
        self.ids.chat_messages.clear_widgets()
        current_sender = None
        current_messages = []
        msg_list = list(websock.response_result(resp))
        if _Debug:
            print('GroupChatScreen.on_message_history_result', len(msg_list))
        for item in msg_list:
            # msg_id = item['doc']['payload']['message_id']
            msg = item['doc']['payload']['data']['message']
            sender = item['doc']['sender']['glob_id']
            if current_sender is None:
                current_sender = sender
            sender_name, _ = current_sender.split('@')
            if current_sender == sender:
                current_messages.append(msg)
            else:
                sender_clr = colorhash.ColorHash(sender_name).hex
                self.ids.chat_messages.add_widget(labels.ChatMessageLabel(
                    text='[color={}]{}[/color]\n{}'.format(sender_clr, sender_name, '\n'.join(current_messages)),
                ))
                current_sender = sender
                sender_name, _ = current_sender.split('@')
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
        self.ids.chat_input.text = ''
        self.ids.chat_input.refresh_height()

    def on_group_message_sent(self, resp):
        if _Debug:
            print('on_group_message_sent', resp)
        if not websock.is_ok(resp):
            return
        self.populate()

    def on_group_message_received(self, json_data):
        if _Debug:
            print('on_group_message_received', json_data)
        self.populate()

    def on_action_button_clicked(self, btn):
        if _Debug:
            print('GroupChatScreen.on_action_button_clicked', btn.icon)
        self.ids.action_button.close_stack()
        if btn.icon == 'account-plus':
            self.main_win().select_screen(
                screen_id='select_friend_screen',
                result_callback=self.on_user_selected,
                screen_header='Invite user to the group:'
            )
        elif btn.icon == 'human-greeting-proximity':
            api_client.group_join(
                group_key_id=self.global_id,
                wait_result=False,
                cb=self.on_group_join_result,
            )
        elif btn.icon == 'exit-run':
            api_client.group_leave(
                group_key_id=self.global_id,
                erase_key=False,
                cb=self.on_group_leave_result,
            )
        elif btn.icon == 'lan-check':
            api_client.group_reconnect(
                group_key_id=self.global_id,
                cb=self.on_group_reconnect_result,
            )
        elif btn.icon == 'trash-can-outline':
            api_client.group_leave(
                group_key_id=self.global_id,
                erase_key=True,
                cb=self.on_group_close_result,
            )
        elif btn.icon == 'information':
            self.main_win().select_screen(
                screen_id='info_'+self.global_id,
                screen_type='group_info_screen',
                global_id=self.global_id,
                label=self.label,
                automat_index=self.automat_index,
                automat_id=self.automat_id,
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
        self.main_win().close_screen(screen_id='select_friend_screen')
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
            snackbar.error(text=websock.response_err(resp))

    def on_group_join_result(self, resp):
        if not websock.is_ok(resp):
            snackbar.error(text='failed to join the group: %s' % websock.response_err(resp))
        else:
            self.ids.state_panel.release()
            self.ids.state_panel.attach(automat_id=websock.result(resp).get('id'))

    def on_group_leave_result(self, resp):
        if not websock.is_ok(resp):
            snackbar.error(text=websock.response_err(resp))
        else:
            self.main_win().select_screen('conversations_screen')
            self.main_win().close_screen(screen_id=self.global_id)

    def on_group_close_result(self, resp):
        if not websock.is_ok(resp):
            snackbar.error(text=websock.response_err(resp))
        else:
            self.main_win().select_screen('conversations_screen')
            self.main_win().close_screen(screen_id=self.global_id)

    def on_group_reconnect_result(self, resp):
        if not websock.is_ok(resp):
            snackbar.error(text='failed connect to the group: %s' % websock.response_err(resp))
        else:
            self.ids.state_panel.release()
            self.ids.state_panel.attach(automat_id=websock.result(resp).get('id'))
