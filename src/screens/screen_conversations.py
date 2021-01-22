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

    def get_icon_color(self, state):
        if state in ['IN_SYNC!', 'CONNECTED', ]:
            return style.color_circle_online
        if state in ['OFFLINE', 'DISCONNECTED', ]:
            return style.color_circle_offline
        return style.color_circle_connecting

    def show_buttons(self):
        if not self.visible_buttons:
            chat_button = ConversationActionButton(
                icon='comment-multiple',
                # color=style.color_btn_normal,
                on_release=self.on_chat_button_clicked,
            )
            self.visible_buttons.append(chat_button)
            self.add_widget(chat_button)
            if self.key_id.startswith('group_'):
                if self.state in ['IN_SYNC!', 'CONNECTED', ]:
                    leave_button = ConversationActionButton(
                        icon='lan-disconnect',
                        # color=style.color_btn_normal_red,
                        on_release=self.on_leave_button_clicked,
                    )
                    self.visible_buttons.append(leave_button)
                    self.add_widget(leave_button)
                else:
                    join_button = ConversationActionButton(
                        icon='lan-connect',
                        # color=style.color_btn_normal,
                        on_release=self.on_join_button_clicked,
                    )
                    self.visible_buttons.append(join_button)
                    self.add_widget(join_button)
                delete_button = ConversationActionButton(
                    icon='trash-can',
                    # color=style.color_btn_normal,
                    on_release=self.on_group_delete_button_clicked,
                )
                self.visible_buttons.append(delete_button)
                self.add_widget(delete_button)


    def hide_buttons(self):
        if self.visible_buttons:
            for w in self.visible_buttons:
                self.remove_widget(w)
            self.visible_buttons.clear()

    def on_chat_button_clicked(self, *args):
        if _Debug:
            print('on_chat_button_clicked', self.key_id)
        self.parent.clear_selection()
        if self.key_id.startswith('master$'):
            self.parent.parent.parent.parent.parent.parent.main_win().select_screen(
                screen_id='private_chat_{}'.format(self.key_id.replace('master$', '')),
                screen_type='private_chat_screen',
                global_id=self.key_id,
                username=self.label,
            )
        elif self.key_id.startswith('group_'):
            self.parent.parent.parent.parent.parent.parent.main_win().select_screen(
                screen_id=self.key_id,
                screen_type='group_chat_screen',
                global_id=self.key_id,
                label=self.label,
            )

    def on_join_button_clicked(self, *args):
        if _Debug:
            print('on_join_button_clicked', self.key_id, )
        self.parent.clear_selection()
        api_client.group_join(group_key_id=self.key_id, cb=self.on_group_join_result)

    def on_group_join_result(self, resp):
        self.parent.parent.parent.parent.parent.parent.ids.chat_status_label.from_api_response(resp)
        self.parent.parent.parent.parent.parent.parent.populate()

    def on_leave_button_clicked(self, *args):
        if _Debug:
            print('on_leave_button_clicked', self.key_id)
        self.parent.clear_selection()
        api_client.group_leave(group_key_id=self.key_id, erase_key=False, cb=self.on_group_leave_result)

    def on_group_leave_result(self, resp):
        self.parent.parent.parent.parent.parent.parent.ids.chat_status_label.from_api_response(resp)
        self.parent.parent.parent.parent.parent.parent.populate()

    def on_group_delete_button_clicked(self, *args):
        if _Debug:
            print('on_group_delete_button_clicked', self.key_id)
        self.parent.clear_selection()
        api_client.group_leave(group_key_id=self.key_id, erase_key=True, cb=self.on_group_leave_result)


class ConversationsListView(SelectableRecycleView):

    def on_selection_applied(self, item, index, is_selected, prev_selected):
        if _Debug:
            print('on_selection_applied() %r %d %r %r' % (item, index, is_selected, prev_selected, ))
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

    def on_pre_enter(self, *args):
        if self.ids.conversations_list_view.selected_item:
            self.ids.conversations_list_view.selected_item.hide_buttons()
        self.ids.conversations_list_view.clear_selection()
        self.populate()

    def on_message_conversations_list_result(self, resp):
        self.ids.chat_status_label.from_api_response(resp)
        if not websock.is_ok(resp):
            self.ids.conversations_list_view.data = []
            return
        self.ids.conversations_list_view.data = []
        for one_conversation in websock.response_result(resp):
            self.ids.conversations_list_view.data.append(one_conversation)

    def on_create_new_group_button_clicked(self, *args):
        self.main_win().select_screen('create_group_screen')

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./screens/screen_conversations.kv')
