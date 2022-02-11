import time

from lib import colorhash
from lib import api_client

from fonts import all_fonts

from components import screen
from components import labels
from components import snackbar

#------------------------------------------------------------------------------

_Debug = False

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

    def get_hot_button(self):
        return {'icon': 'send', 'color': 'green', }

    def populate(self, **kwargs):
        selected_messages = []
        for snap_info in self.model('message').values():
            if not snap_info:
                continue
            msg = snap_info['data']
            if msg['payload']['msg_type'] != 'group_message':
                continue
            if msg['recipient']['glob_id'] != self.global_id:
                continue
            selected_messages.append(snap_info)
        updated = False
        for snap_info in sorted(selected_messages, key=lambda snap_info: snap_info['id']):
            if self.on_message(snap_info):
                updated = True
        if updated:
            self.ids.chat_messages_view.scroll_y = 0

    def on_enter(self, *args):
        self.ids.state_panel.attach(automat_id=self.automat_id)
        api_client.add_model_listener('message', listener_cb=self.on_message)
        self.populate()
        self.ids.chat_input.focus = True

    def on_leave(self, *args):
        api_client.remove_model_listener('message', listener_cb=self.on_message)
        self.ids.state_panel.release()

    def on_message(self, payload):
        if _Debug:
            print('GroupChatScreen.on_message', payload)
        msg = payload['data']
        msg_id = int(msg['payload']['message_id'])
        if msg['payload']['msg_type'] != 'group_message':
            return False
        if msg['recipient']['glob_id'] != self.global_id:
            return False
        children_index = {}
        latest_message_id = None
        recent_min_message_id = None
        msg_found = False
        for i, w in enumerate(self.ids.chat_messages.children):
            if isinstance(w, labels.ChatMessageLabel):
                children_index[w.message_id] = i
                if not latest_message_id:
                    latest_message_id = w.message_id
                if latest_message_id < w.message_id:
                    latest_message_id = w.message_id
                if not recent_min_message_id:
                    recent_min_message_id = w.message_id
                if w.message_id > msg_id and w.message_id - msg_id < recent_min_message_id - msg_id:
                    recent_min_message_id = w.message_id
                if w.message_id == msg_id:
                    msg_found = True
                    break
        if msg_found:
            children_index.clear()
            return False
        new_index = len(self.ids.chat_messages.children)
        if not latest_message_id or latest_message_id < msg_id:
            new_index = 0
        else:
            if recent_min_message_id:
                if recent_min_message_id < msg_id:
                    new_index = children_index[recent_min_message_id]
                else:
                    new_index = children_index[recent_min_message_id] + 1
        children_index.clear()
        sender_name = msg['sender']['glob_id']
        sender_name, _ = sender_name.split('@')
        sender_clr = colorhash.ColorHash(sender_name).hex
        self.ids.chat_messages.add_widget(
            widget=labels.ChatMessageLabel(
                conversation_id=msg['conversation_id'],
                message_id=msg_id,
                message_time=msg['payload']['time'],
                text='[color={}]{}[/color]  [color=#DDDDDD]{} #{}[/color]\n{}'.format(
                    # jet_brains.PragmataPro_I_ttf_filepath,
                    sender_clr,
                    sender_name,
                    time.strftime('%d %B at %H:%M:%S', time.localtime(msg['payload']['time'])),
                    msg_id,
                    # jet_brains.PragmataPro_ttf_filepath,
                    msg['payload']['data']['message'],
                ),
            ),
            index=new_index,
        )
        return True

    def on_hot_button_clicked(self, *args):
        msg = self.ids.chat_input.text
        if _Debug:
            print('GroupChatScreen.on_hot_button_clicked', self.global_id, msg)
        api_client.message_send_group(
            group_key_id=self.global_id,
            data={'message': msg, },
            cb=self.on_group_message_sent,
        )
        self.ids.chat_input.text = ''
        self.ids.chat_input.refresh_height()

    def on_group_message_sent(self, resp):
        if _Debug:
            print('GroupChatScreen.on_group_message_sent', resp)
        if not api_client.is_ok(resp):
            snackbar.error(text='message was not sent: %s' % api_client.response_err(resp))

    def on_drop_down_menu_item_clicked(self, btn):
        if _Debug:
            print('GroupChatScreen.on_drop_down_menu_item_clicked', btn.icon)
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
            print('GroupChatScreen.on_user_selected', user_global_id)
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
            print('GroupChatScreen.on_group_share_result', resp)
        if api_client.is_ok(resp):
            snackbar.success(text='group key shared with %s' % user_global_id)
        else:
            snackbar.error(text=api_client.response_err(resp))

    def on_group_join_result(self, resp):
        if not api_client.is_ok(resp):
            snackbar.error(text='failed to join the group: %s' % api_client.response_err(resp))
        else:
            self.ids.state_panel.release()
            self.ids.state_panel.attach(automat_id=api_client.result(resp).get('id'))

    def on_group_leave_result(self, resp):
        if not api_client.is_ok(resp):
            snackbar.error(text=api_client.response_err(resp))
        else:
            self.main_win().select_screen('conversations_screen')
            self.main_win().close_screen(screen_id=self.global_id)

    def on_group_close_result(self, resp):
        if not api_client.is_ok(resp):
            snackbar.error(text=api_client.response_err(resp))
        else:
            self.main_win().select_screen('conversations_screen')
            self.main_win().close_screen(screen_id=self.global_id)

    def on_group_reconnect_result(self, resp):
        if not api_client.is_ok(resp):
            snackbar.error(text='failed connect to the group: %s' % api_client.response_err(resp))
        else:
            self.ids.state_panel.release()
            self.ids.state_panel.attach(automat_id=api_client.result(resp).get('id'))
