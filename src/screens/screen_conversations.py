from kivy.metrics import dp
from kivy.properties import StringProperty, NumericProperty  # @UnresolvedImport

from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.list import TwoLineIconListItem

from lib import api_client

from components import screen

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

class ConversationItem(TwoLineIconListItem):

    type = StringProperty()
    conversation_id = StringProperty()
    key_id = StringProperty()
    state = StringProperty()
    label = StringProperty()
    automat_index = NumericProperty(None, allownone=True)
    automat_id = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.height = dp(48) if not self._height else self._height

    def get_secondary_text(self):
        sec_text = 'connecting...'
        sec_color = 'bbbf'
        if self.state in ['IN_SYNC!', 'CONNECTED', ]:
            sec_text = 'on-line'
            sec_color = 'adaf'
        elif self.state in ['OFFLINE', 'DISCONNECTED', ]:
            sec_text = 'offline'
        if _Debug:
            print('ConversationItem.get_secondary_text', self.key_id, sec_text)
        return '[size=10sp][color=%s]%s[/color][/size]' % (sec_color, sec_text, )

    def on_pressed(self):
        if _Debug:
            print('ConversationItem.on_pressed', self)
        automat_index = self.automat_index or None
        automat_index = int(automat_index) if automat_index is not None else None
        if self.type in ['group_message', 'personal_message', ]:
            screen.select_screen(
                screen_id=self.key_id,
                screen_type='group_chat_screen',
                global_id=self.key_id,
                label=self.label,
                automat_index=automat_index,
                automat_id=self.automat_id or None,
            )
        elif self.type in ['private_message', ]:
            screen.select_screen(
                screen_id='private_chat_{}'.format(self.key_id.replace('master$', '')),
                screen_type='private_chat_screen',
                global_id=self.key_id,
                username=self.label,
                automat_index=automat_index,
            )


class NewPrivateChat(OneLineIconListItem):

    def on_pressed(self):
        if _Debug:
            print('NewFriendItem.on_pressed', self)
        screen.select_screen('search_people_screen')


class NewGroupChat(OneLineIconListItem):

    def on_pressed(self):
        if _Debug:
            print('NewGroupItem.on_pressed', self)
        screen.select_screen('create_group_screen')


class ConversationsScreen(screen.AppScreen):

    def get_title(self):
        return 'conversations'

    # def get_icon(self):
    #     return 'comment-text-multiple'

    def populate(self, *args, **kwargs):
        self.ids.conversations_list_view.clear_widgets()
        self.ids.conversations_list_view.add_widget(NewGroupChat())
        self.ids.conversations_list_view.add_widget(NewPrivateChat())
        for snap_info in self.model('conversation').values():
            if snap_info:
                self.on_conversation(snap_info)

    def on_created(self):
        api_client.add_model_listener('conversation', listener_cb=self.on_conversation)
        api_client.add_model_listener('online_status', listener_cb=self.on_online_status)
        self.populate()

    def on_destroying(self):
        api_client.remove_model_listener('online_status', listener_cb=self.on_online_status)
        api_client.remove_model_listener('conversation', listener_cb=self.on_conversation)

    def on_enter(self, *args):
        self.ids.state_panel.attach(automat_id='service_message_history')

    def on_leave(self, *args):
        self.ids.state_panel.release()

    def on_online_status(self, payload):
        if _Debug:
            print('ConversationsScreen.on_online_status', payload)
        item_found = None
        for w in self.ids.conversations_list_view.children:
            if isinstance(w.instance_item, ConversationItem):
                if w.instance_item.key_id == payload['data']['global_id']:
                    item_found = w
                    break
        if item_found:
            prev_state = item_found.instance_item.state
            if prev_state != payload['data']['state']:
                item_found.instance_item.state = payload['data']['state']
                item_found.instance_item.secondary_text = item_found.instance_item.get_secondary_text()
                if _Debug:
                    print('ConversationsScreen.on_online_status %r updated : %r -> %r' % (
                        item_found.instance_item.key_id, prev_state, payload['data']['state'], ))

    def on_conversation(self, payload):
        if _Debug:
            print('ConversationsScreen.on_conversation', payload)
        conv = payload['data']
        conv['automat_index'] = conv.pop('index', None) or None
        conv['automat_id'] = str(conv.pop('id', '') or '')
        item_found = None
        for w in self.ids.conversations_list_view.children:
            if isinstance(w.instance_item, ConversationItem):
                if w.instance_item.key_id == conv['key_id']:
                    item_found = w
                    break
        if item_found:
            item_found.instance_item.type = conv['type']
            item_found.instance_item.conversation_id = conv['conversation_id']
            item_found.instance_item.key_id = conv['key_id']
            item_found.instance_item.state = conv['state']
            item_found.instance_item.label = conv['label']
            if conv['automat_index']:
                item_found.instance_item.automat_index = conv['automat_index']
            if conv['automat_id']:
                item_found.instance_item.automat_id = conv['automat_id']
            item_found.instance_item.secondary_text = item_found.instance_item.get_secondary_text()
            if _Debug:
                print('ConversationsScreen.on_conversation updated existing item',
                      conv['key_id'], item_found.instance_item.automat_id, item_found.instance_item.automat_index)
            return
        self.ids.conversations_list_view.add_widget(ConversationItem(
            type=conv['type'],
            conversation_id=conv['conversation_id'],
            key_id=conv['key_id'],
            state=conv['state'],
            label=conv['label'],
            automat_index=conv['automat_index'],
            automat_id=conv['automat_id'],
        ))
        if _Debug:
            print('ConversationsScreen.on_conversation added new item', conv['key_id'], conv['automat_id'], conv['automat_index'])

    def on_group_state_changed(self, event_id, group_key_id, old_state, new_state):
        if _Debug:
            print('ConversationsScreen.on_group_state_changed', event_id, group_key_id)
        item_found = None
        for w in self.ids.conversations_list_view.children:
            if isinstance(w.instance_item, ConversationItem):
                if w.instance_item.key_id == group_key_id:
                    item_found = w
                    break
        if item_found:
            prev_state = item_found.instance_item.state
            item_found.instance_item.state = new_state
            item_found.instance_item.secondary_text = item_found.instance_item.get_secondary_text()
            if _Debug:
                print('ConversationsScreen.on_group_state_changed %r updated : %r -> %r' % (group_key_id, prev_state, new_state, ))
