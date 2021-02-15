from components import screen
from components import list_view
from components import styles

from lib import api_client
from lib import websock

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

class ConversationRecord(list_view.SelectableHorizontalRecord):

    def get_icon_color(self, state):
        if state in ['IN_SYNC!', 'CONNECTED', ]:
            return styles.app.color_circle_online
        if state in ['OFFLINE', 'DISCONNECTED', ]:
            return styles.app.color_circle_offline
        return styles.app.color_circle_connecting

    def on_chat_button_clicked(self, *args):
        if _Debug:
            print('ConversationRecord.on_chat_button_clicked', self.key_id)
        self.clear_selection()
        if self.type in ['group_message', 'personal_message', ]:
            screen.main_window().select_screen(
                screen_id=self.key_id,
                screen_type='group_chat_screen',
                global_id=self.key_id,
                label=self.label,
            )
        elif self.type in ['private_message', ]:
            screen.main_window().select_screen(
                screen_id='private_chat_{}'.format(self.key_id.replace('master$', '')),
                screen_type='private_chat_screen',
                global_id=self.key_id,
                username=self.label,
            )

    def on_join_button_clicked(self, *args):
        if _Debug:
            print('ConversationRecord.on_join_button_clicked', self.key_id, )
        self.clear_selection()
        api_client.group_join(group_key_id=self.key_id, publish_events=True, cb=self.on_group_join_result)

    def on_group_join_result(self, resp):
        self.get_root().ids.status_label.from_api_response(resp)
        self.get_root().populate()

    def on_leave_button_clicked(self, *args):
        if _Debug:
            print('ConversationRecord.on_leave_button_clicked', self.key_id)
        self.clear_selection()
        api_client.group_leave(group_key_id=self.key_id, erase_key=False, cb=self.on_group_leave_result)

    def on_group_leave_result(self, resp):
        self.get_root().ids.status_label.from_api_response(resp)
        self.get_root().populate()

    def on_group_delete_button_clicked(self, *args):
        if _Debug:
            print('ConversationRecord.on_group_delete_button_clicked', self.key_id)
        self.clear_selection()
        api_client.group_leave(group_key_id=self.key_id, erase_key=True, cb=self.on_group_leave_result)


class ConversationsListView(list_view.SelectableRecycleView):

    def on_selection_applied(self, item, index, is_selected, prev_selected):
        if self.selected_item:
            if self.selected_item.type in ['group_message', 'personal_message', ]:
                screen.main_window().select_screen(
                    screen_id=self.selected_item.key_id,
                    screen_type='group_chat_screen',
                    global_id=self.selected_item.key_id,
                    label=self.selected_item.label,
                )
            elif self.selected_item.type in ['private_message', ]:
                screen.main_window().select_screen(
                    screen_id='private_chat_{}'.format(self.selected_item.key_id.replace('master$', '')),
                    screen_type='private_chat_screen',
                    global_id=self.selected_item.key_id,
                    username=self.selected_item.label,
                )


class ConversationsScreen(screen.AppScreen):

    def get_title(self):
        return 'conversations'

    def get_icon(self):
        return 'comment-text-multiple'

    def populate(self, *args, **kwargs):
        api_client.message_conversations_list(cb=self.on_message_conversations_list_result)

    def clear_selected_item(self):
        if self.ids.conversations_list_view.selected_item:
            self.ids.conversations_list_view.selected_item.selected = False
        self.ids.conversations_list_view.clear_selection()

    def on_enter(self, *args):
        self.clear_selected_item()
        self.populate()

    def on_leave(self, *args):
        self.clear_selected_item()

    def on_message_conversations_list_result(self, resp):
        self.ids.status_label.from_api_response(resp)
        if not websock.is_ok(resp):
            self.clear_selected_item()
            self.ids.conversations_list_view.data = []
            return
        conversations_list = websock.response_result(resp)
        for one_conversation in conversations_list:
            one_conversation.pop('index', None)
            item_found = False
            for i in range(len(self.ids.conversations_list_view.data)):
                item = self.ids.conversations_list_view.data[i]
                if item['key_id'] == one_conversation['key_id']:
                    item_found = True
                    break
            if item_found:
                self.ids.conversations_list_view.data[i] = one_conversation
                if _Debug:
                    print('ConversationsScreen.on_message_conversations_list_result updated existing item at position %d' % i, one_conversation)
                continue
            self.ids.conversations_list_view.data.append(one_conversation)
            if _Debug:
                print('ConversationsScreen.on_message_conversations_list_result added new item', one_conversation)
        to_be_removed = []
        for item in self.ids.conversations_list_view.data:
            item_found = False
            for one_conversation in conversations_list:
                one_conversation.pop('index', None)
                if one_conversation['key_id'] == item['key_id']:
                    item_found = True
                    break
            if item_found:
                continue
            to_be_removed.append(item)
        for item in to_be_removed:
            self.ids.conversations_list_view.data.remove(item)
            if _Debug:
                print('ConversationsScreen.on_message_conversations_list_result erased existing item', item)
        self.ids.conversations_list_view.refresh_from_data()

    def on_create_new_group_button_clicked(self, *args):
        self.main_win().select_screen('create_group_screen')

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
                if old_state != prev_state:
                    if _Debug:
                        print('ConversationsScreen.on_group_state_changed WARNING prev_state was %r, but expected %r' % (prev_state, old_state, ))
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
                if old_state != prev_state:
                    if _Debug:
                        print('ConversationsScreen.on_friend_state_changed WARNING prev_state was %r, but expected %r' % (prev_state, old_state, ))
                self.ids.conversations_list_view.data[i]['state'] = new_state
                if _Debug:
                    print('ConversationsScreen.on_friend_state_changed %r updated : %r -> %r' % (global_id, prev_state, new_state, ))
                break
        if not item_found:
            self.populate()
        else:
            self.ids.conversations_list_view.refresh_from_data()

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./screens/screen_conversations.kv')
