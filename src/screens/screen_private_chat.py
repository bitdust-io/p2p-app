import time

from lib import colorhash
from lib import api_client

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

    # def get_icon(self):
    #     return ''

    # def get_title(self):
    #     return self.username

    def get_hot_button(self):
        return {'icon': 'send', 'color': 'green', }

    def get_statuses(self):
        return {
            None: 'connection with remote peer is not active',
            'PING?': 'waiting acknowledgment from remote peer',
            'CONNECTED': 'user is connected',
            'OFFLINE': 'user is disconnected',
            'CLOSED': 'connection with remote peer was closed',
        }

    def populate(self, **kwargs):
        selected_messages = []
        for snap_info in self.model('message').values():
            if not snap_info:
                continue
            msg = snap_info['data']
            if msg['payload']['msg_type'] != 'private_message':
                continue
            if msg['recipient']['glob_id'] == self.recipient_id or msg['sender']['glob_id'] == self.recipient_id:
                selected_messages.append(snap_info)
        updated = False
        for snap_info in sorted(selected_messages, key=lambda snap_info: snap_info['id']):
            if self.on_message(snap_info):
                updated = True
        if updated:
            self.ids.chat_messages_view.scroll_y = 0

    def on_enter(self, *args):
        self.ids.state_panel.attach(self.automat_index)
        api_client.add_model_listener('message', listener_cb=self.on_message)
        self.populate()
        self.ids.chat_input.focus = True

    def on_leave(self, *args):
        api_client.remove_model_listener('message', listener_cb=self.on_message)
        self.ids.state_panel.release()

    def on_message(self, payload):
        if _Debug:
            print('PrivateChatScreen.on_message', payload)
        msg = payload['data']
        msg_id = msg['payload']['message_id']
        msg_time = msg['payload']['time']
        if msg['payload']['msg_type'] != 'private_message':
            return False
        if msg['recipient']['glob_id'] != self.recipient_id and msg['sender']['glob_id'] != self.recipient_id:
            return False
        children_index = {}
        latest_message_id = None
        latest_message_time = None
        recent_min_message_id = None
        recent_min_message_time = None
        msg_found = False
        for i, w in enumerate(self.ids.chat_messages.children):
            if isinstance(w, labels.ChatMessageLabel):
                children_index[w.message_id] = i
                if not latest_message_id:
                    latest_message_id = w.message_id
                    latest_message_time = w.message_time
                if latest_message_time < w.message_time:
                    latest_message_id = w.message_id
                    latest_message_time = w.message_time
                if not recent_min_message_id:
                    recent_min_message_id = w.message_id
                    recent_min_message_time = w.message_time
                if w.message_time > msg_time and w.message_time - msg_time < recent_min_message_time - msg_time:
                    recent_min_message_id = w.message_id
                    recent_min_message_time = w.message_time
                if w.message_id == msg_id:
                    msg_found = True
                    break
        if msg_found:
            children_index.clear()
            return False
        new_index = len(self.ids.chat_messages.children)
        if not latest_message_id or latest_message_time < msg_time:
            new_index = 0
        else:
            if recent_min_message_id:
                if recent_min_message_time < msg_time:
                    new_index = children_index[recent_min_message_id]
                else:
                    new_index = children_index[recent_min_message_id] + 1
        children_index.clear()
        sender_name = msg['sender']['glob_id']
        sender_name, _, _ = sender_name.partition('@')
        _, _, sender_name = sender_name.partition('$')
        self.ids.chat_messages.add_widget(
            widget=labels.ChatMessageLabel(
                conversation_id=msg['conversation_id'],
                message_id=msg_id,
                message_time=msg['payload']['time'],
                text=labels.format_chat_message(
                    sender_name=sender_name,
                    sender_color=colorhash.get_user_color_hex(msg['sender']['glob_id']),
                    json_payload=msg['payload'],
                    message_id=time.strftime('%Y %d %B at %H:%M:%S', time.localtime(msg['payload']['time'])),
                )
            ),
            index=new_index,
        )
        return True

    def on_hot_button_clicked(self, *args):
        msg = self.ids.chat_input.text
        if _Debug:
            print('PrivateChatScreen.on_hot_button_clicked', self.recipient_id, msg)
        if not msg.strip():
            return
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
        if not api_client.is_ok(resp):
            snackbar.error(text='message was not sent: %s' % api_client.response_err(resp), bottom=False)

    def on_drop_down_menu_item_clicked(self, btn):
        if _Debug:
            print('PrivateChatScreen.on_drop_down_menu_item_clicked', btn.icon)
        if btn.icon == 'account-plus':
            api_client.friend_add(
                global_user_id=self.recipient_id,
                cb=self.on_friend_add_result,
            )
        elif btn.icon == 'trash-can-outline':
            api_client.friend_remove(
                global_user_id=self.recipient_id,
                cb=self.on_friend_remove_result,
            )

    def on_friend_add_result(self, resp):
        if _Debug:
            print('PrivateChatScreen.on_friend_add_result', resp)
        snackbar.success('new contact added', bottom=False)

    def on_friend_remove_result(self, resp):
        if _Debug:
            print('PrivateChatScreen.on_friend_remove_result', resp)
        # if not api_client.is_ok(resp):
        #     snackbar.error(text='contact was not deleted: %s' % api_client.response_err(resp), bottom=False)
        #     return
        screen.select_screen('friends_screen')
        screen.stack_clear()
        screen.stack_append('welcome_screen')
