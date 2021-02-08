from components.buttons import TransparentIconButton
from components.screen import AppScreen
from components.list_view import SelectableRecycleView, SelectableHorizontalRecord
from components.styles import style

from lib import api_client
from lib import websock

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

class ConversationActionButton(TransparentIconButton):
    pass


class ConversationRecord(SelectableHorizontalRecord):

    def __init__(self, **kwargs):
        super(ConversationRecord, self).__init__(**kwargs)
        self.visible_buttons = []

    def get_root(self):
        return self.parent.parent.parent.parent.parent.parent

    def get_icon_color(self, state):
        if state in ['IN_SYNC!', 'CONNECTED', ]:
            return style.color_circle_online
        if state in ['OFFLINE', 'DISCONNECTED', ]:
            return style.color_circle_offline
        return style.color_circle_connecting

    def clear_selection(self):
        self.hide_buttons()
        self.selected = False
        self.parent.clear_selection()

    def show_buttons(self):
        if _Debug:
            print('ConversationRecord.show_buttons', self.key_id, self.state, len(self.visible_buttons))
        if not self.visible_buttons:
            chat_button = ConversationActionButton(
                icon='comment-multiple',
                on_release=self.on_chat_button_clicked,
            )
            self.visible_buttons.append(chat_button)
            self.add_widget(chat_button)
            if self.type in ['group_message', 'personal_message', ]:
                join_button = ConversationActionButton(
                    icon='access-point-network',
                    disabled=self.state in ['IN_SYNC!', 'CONNECTED', ],
                    on_release=self.on_join_button_clicked,
                )
                self.visible_buttons.append(join_button)
                self.add_widget(join_button)
                leave_button = ConversationActionButton(
                    icon='lan-disconnect',
                    disabled=self.state in ['OFFLINE', 'DISCONNECTED', ],
                    on_release=self.on_leave_button_clicked,
                )
                self.visible_buttons.append(leave_button)
                self.add_widget(leave_button)
                delete_button = ConversationActionButton(
                    icon='trash-can',
                    on_release=self.on_group_delete_button_clicked,
                )
                self.visible_buttons.append(delete_button)
                self.add_widget(delete_button)


    def hide_buttons(self):
        if _Debug:
            print('ConversationRecord.hide_buttons', self.key_id, self.state, len(self.visible_buttons))
        if self.visible_buttons:
            for w in self.visible_buttons:
                self.remove_widget(w)
            self.visible_buttons.clear()

    def on_chat_button_clicked(self, *args):
        if _Debug:
            print('ConversationRecord.on_chat_button_clicked', self.key_id)
        self.clear_selection()
        if self.type in ['group_message', 'personal_message', ]:
            self.get_root().main_win().select_screen(
                screen_id=self.key_id,
                screen_type='group_chat_screen',
                global_id=self.key_id,
                label=self.label,
            )
        elif self.type in ['private_message', ]:
            self.get_root().main_win().select_screen(
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


class ConversationsListView(SelectableRecycleView):

    def on_selection_applied(self, item, index, is_selected, prev_selected):
        if _Debug:
            print('ConversationsListView.on_selection_applied',
                  item, index, is_selected, prev_selected, item.selected if item else None, self.ids.selectable_layout.selected_nodes)
        if is_selected != prev_selected:
            if is_selected:
                item.show_buttons()
            else:
                item.hide_buttons()


class ConversationsScreen(AppScreen):

    def get_title(self):
        return 'conversations'

    def get_icon(self):
        return 'comment-text-multiple'

    def populate(self, *args, **kwargs):
        api_client.message_conversations_list(cb=self.on_message_conversations_list_result)

    def clear_selected_item(self):
        if self.ids.conversations_list_view.selected_item:
            self.ids.conversations_list_view.selected_item.hide_buttons()
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
