from lib import api_client

from components import screen
from components import list_view
from components import styles

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

class ConversationRecord(list_view.SelectableHorizontalRecord):

    def get_icon_color(self, state):
        if state in ['IN_SYNC!', 'CONNECTED', ]:
            return styles.app.color_circle_online
        if state in ['OFFLINE', 'DISCONNECTED', ]:
            return styles.app.color_circle_offline
        return styles.app.color_circle_connecting


class ConversationsListView(list_view.SelectableRecycleView):

    def on_selection_applied(self, item, index, is_selected, prev_selected):
        if self.selected_item:
            typ = self.selected_item.type
            key_id = self.selected_item.key_id
            label = self.selected_item.label
            automat_index = self.selected_item.automat_index or None
            automat_index = int(automat_index) if automat_index is not None else None
            automat_id = self.selected_item.automat_id or None
            if typ in ['group_message', 'personal_message', ]:
                screen.main_window().select_screen(
                    screen_id=key_id,
                    screen_type='group_chat_screen',
                    global_id=key_id,
                    label=label,
                    automat_index=automat_index,
                    automat_id=automat_id,
                )
            elif typ in ['private_message', ]:
                screen.main_window().select_screen(
                    screen_id='private_chat_{}'.format(key_id.replace('master$', '')),
                    screen_type='private_chat_screen',
                    global_id=key_id,
                    username=label,
                    automat_index=automat_index,
                )
        self.clear_selection()
        self.ids.selectable_layout.clear_selection()


class ConversationsScreen(screen.AppScreen):

    def get_title(self):
        return 'conversations'

    def get_icon(self):
        return 'comment-text-multiple'

    def populate(self, *args, **kwargs):
        for snap_info in self.model('conversation').values():
            if snap_info:
                self.on_conversation(snap_info)

    def clear_selected_item(self):
        self.ids.conversations_list_view.clear_selection()
        self.ids.conversations_list_view.ids.selectable_layout.clear_selection()

    def on_enter(self, *args):
        self.ids.action_button.close_stack()
        self.ids.state_panel.attach(automat_id='service_message_history')
        self.clear_selected_item()
        api_client.add_model_listener('conversation', listener_cb=self.on_conversation)
        self.populate()

    def on_leave(self, *args):
        api_client.remove_model_listener('conversation', listener_cb=self.on_conversation)
        self.ids.action_button.close_stack()
        self.ids.state_panel.release()
        self.clear_selected_item()

    def on_conversation(self, payload):
        one_conversation = payload['data']
        one_conversation['automat_index'] = str(one_conversation.pop('index', '') or '')
        one_conversation['automat_id'] = str(one_conversation.pop('id', '') or '')
        item_found = False
        for i in range(len(self.ids.conversations_list_view.data)):
            item = self.ids.conversations_list_view.data[i]
            if item['key_id'] == one_conversation['key_id']:
                item_found = True
                break
        if item_found:
            self.ids.conversations_list_view.data[i] = one_conversation
            self.ids.conversations_list_view.refresh_from_data()
            if _Debug:
                print('ConversationsScreen.on_conversation updated existing item at position %d' % i, one_conversation['key_id'])
            return
        self.ids.conversations_list_view.data.append(one_conversation)
#         to_be_removed = []
#         for item in self.ids.conversations_list_view.data:
#             item_found = False
#             for one_conversation in conversations_list:
#                 one_conversation.pop('index', None)
#                 if one_conversation['key_id'] == item['key_id']:
#                     item_found = True
#                     break
#             if item_found:
#                 continue
#             to_be_removed.append(item)
#         for item in to_be_removed:
#             self.ids.conversations_list_view.data.remove(item)
#             if _Debug:
#                 print('ConversationsScreen.on_message_conversations_list_result erased existing item', item['key_id'])
        self.ids.conversations_list_view.refresh_from_data()
        if _Debug:
            print('ConversationsScreen.on_conversation added new item', one_conversation['key_id'])

#     def on_message_conversations_list_result(self, resp):
#         if _Debug:
#             print('ConversationsScreen.on_message_conversations_list_result  %s...' % str(resp)[:100])
#         if not api_client.is_ok(resp):
#             self.clear_selected_item()
#             self.ids.conversations_list_view.data = []
#             return
#         conversations_list = api_client.response_result(resp)
#         for one_conversation in conversations_list:
#             one_conversation['automat_index'] = str(one_conversation.pop('index') or '')
#             one_conversation['automat_id'] = str(one_conversation.pop('id') or '')
#             item_found = False
#             for i in range(len(self.ids.conversations_list_view.data)):
#                 item = self.ids.conversations_list_view.data[i]
#                 if item['key_id'] == one_conversation['key_id']:
#                     item_found = True
#                     break
#             if item_found:
#                 self.ids.conversations_list_view.data[i] = one_conversation
#                 if _Debug:
#                     print('ConversationsScreen.on_message_conversations_list_result updated existing item at position %d' % i, one_conversation['key_id'])
#                 continue
#             self.ids.conversations_list_view.data.append(one_conversation)
#             if _Debug:
#                 print('ConversationsScreen.on_message_conversations_list_result added new item', one_conversation['key_id'])
#         to_be_removed = []
#         for item in self.ids.conversations_list_view.data:
#             item_found = False
#             for one_conversation in conversations_list:
#                 one_conversation.pop('index', None)
#                 if one_conversation['key_id'] == item['key_id']:
#                     item_found = True
#                     break
#             if item_found:
#                 continue
#             to_be_removed.append(item)
#         for item in to_be_removed:
#             self.ids.conversations_list_view.data.remove(item)
#             if _Debug:
#                 print('ConversationsScreen.on_message_conversations_list_result erased existing item', item['key_id'])
#         self.ids.conversations_list_view.refresh_from_data()

    def on_action_button_clicked(self, btn):
        if _Debug:
            print('ConversationsScreen.on_action_button_clicked', btn.icon)
        self.ids.action_button.close_stack()
        if btn.icon == 'chat-plus-outline':
            self.main_win().select_screen('create_group_screen')
        elif btn.icon == 'account-key-outline':
            self.main_win().select_screen('select_friend_screen')
        elif btn.icon == 'account-box-multiple':
            self.main_win().select_screen('friends_screen')

    def on_state_changed(self, event_data):
        if _Debug:
            print('ConversationsScreen.on_state_changed', event_data)

    def on_group_state_changed(self, event_id, group_key_id, old_state, new_state):
        if _Debug:
            print('ConversationsScreen.on_group_state_changed', event_id, group_key_id)
        item_found = False
        for i in range(len(self.ids.conversations_list_view.data)):
            item = self.ids.conversations_list_view.data[i]
            if item['type'] not in ['group_message', 'personal_message', ]:
                continue
            if item['key_id'] == group_key_id:
                item_found = True
                prev_state = self.ids.conversations_list_view.data[i]['state']
                # if old_state != prev_state:
                #     if _Debug:
                #         print('ConversationsScreen.on_group_state_changed WARNING prev_state was %r, but expected %r' % (prev_state, old_state, ))
                self.ids.conversations_list_view.data[i]['state'] = new_state
                if _Debug:
                    print('ConversationsScreen.on_group_state_changed %r updated : %r -> %r' % (group_key_id, prev_state, new_state, ))
                break
        if not item_found:
            self.populate()
        else:
            self.ids.conversations_list_view.refresh_from_data()

    def on_friend_state_changed(self, event_id, idurl, global_id, old_state, new_state):
        if _Debug:
            print('ConversationsScreen.on_friend_state_changed', event_id, idurl, global_id)
        item_found = False
        for i in range(len(self.ids.conversations_list_view.data)):
            item = self.ids.conversations_list_view.data[i]
            if item['type'] not in ['private_message', ]:
                continue
            if item['key_id'] == global_id:
                item_found = True
                prev_state = self.ids.conversations_list_view.data[i]['state']
                # if old_state != prev_state:
                #     if _Debug:
                #         print('ConversationsScreen.on_friend_state_changed WARNING prev_state was %r, but expected %r' % (prev_state, old_state, ))
                self.ids.conversations_list_view.data[i]['state'] = new_state
                if _Debug:
                    print('ConversationsScreen.on_friend_state_changed %r updated : %r -> %r' % (global_id, prev_state, new_state, ))
                break
        if not item_found:
            self.populate()
        else:
            self.ids.conversations_list_view.refresh_from_data()
