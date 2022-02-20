from kivy.properties import StringProperty, NumericProperty  # @UnresolvedImport

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

    def get_secondary_text(self):
        if self.state in ['IN_SYNC!', 'CONNECTED', ]:
            sec_text = 'on-line'
        elif self.state in ['OFFLINE', 'DISCONNECTED', ]:
            sec_text = 'offline'
        else:
            sec_text = 'connecting'
        if _Debug:
            print('ConversationItem.get_secondary_text', self.key_id, sec_text)
        return '[color=dddf]%s[/color]' % sec_text

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


class ConversationsScreen(screen.AppScreen):

    def get_title(self):
        return 'conversations'

    def get_icon(self):
        return 'comment-text-multiple'

    def get_hot_button(self):
        return {'icon': 'chat-plus-outline', 'color': 'green', }

    def populate(self, *args, **kwargs):
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

#     def on_drop_down_menu_item_clicked(self, btn):
#         if _Debug:
#             print('ConversationsScreen.on_drop_down_menu_item_clicked', btn.icon)
#         if btn.icon == 'chat-plus-outline':
#             self.main_win().select_screen('create_group_screen')
#         elif btn.icon == 'account-key-outline':
#             self.main_win().select_screen('select_friend_screen')
#         elif btn.icon == 'account-box-multiple':
#             self.main_win().select_screen('friends_screen')

#     def on_state_changed(self, event_data):
#         if _Debug:
#             print('ConversationsScreen.on_state_changed', event_data)
#         item_found = None
#         for w in self.ids.conversations_list_view.children:
#             if w.instance_item.automat_index == event_data['index'] and w.instance_item.automat_id == event_data['id']:
#                 item_found = w
#                 break
#         if item_found:
#             item_found.instance_item.state = event_data['newstate']
#             item_found.instance_item.secondary_text = item_found.instance_item.get_secondary_text()
#             if _Debug:
#                 print('ConversationsScreen.on_state_changed updated existing item', event_data['id'], event_data['newstate'])

    def on_group_state_changed(self, event_id, group_key_id, old_state, new_state):
        if _Debug:
            print('ConversationsScreen.on_group_state_changed', event_id, group_key_id)
        item_found = None
        for w in self.ids.conversations_list_view.children:
            if w.instance_item.key_id == group_key_id:
                item_found = w
                break
        if item_found:
            prev_state = item_found.instance_item.state
            item_found.instance_item.state = new_state
            item_found.instance_item.secondary_text = item_found.instance_item.get_secondary_text()
            if _Debug:
                print('ConversationsScreen.on_group_state_changed %r updated : %r -> %r' % (group_key_id, prev_state, new_state, ))

#     def on_friend_state_changed(self, event_id, idurl, global_id, old_state, new_state):
#         if _Debug:
#             print('ConversationsScreen.on_friend_state_changed', event_id, idurl, global_id)
#         item_found = False
#         for i in range(len(self.ids.conversations_list_view.data)):
#             item = self.ids.conversations_list_view.data[i]
#             if item['type'] not in ['private_message', ]:
#                 continue
#             if item['key_id'] == global_id:
#                 item_found = True
#                 prev_state = self.ids.conversations_list_view.data[i]['state']
#                 self.ids.conversations_list_view.data[i]['state'] = new_state
#                 if _Debug:
#                     print('ConversationsScreen.on_friend_state_changed %r updated : %r -> %r' % (global_id, prev_state, new_state, ))
#                 break
#         if not item_found:
#             self.populate()
#         else:
#             self.ids.conversations_list_view.refresh_from_data()

    def on_hot_button_clicked(self, *args):
        if _Debug:
            print('ConversationsScreen.on_hot_button_clicked', *args)
        self.main_win().select_screen('friends_screen')
