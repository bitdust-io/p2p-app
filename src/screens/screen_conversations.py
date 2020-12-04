from components.buttons import RoundedButton, CustomIconButton
from components.screen import AppScreen
from components.list_view import SelectableRecycleView, SelectableHorizontalRecord
from components.webfont import fa_icon

from lib import api_client

#------------------------------------------------------------------------------

class ConversationActionButton(CustomIconButton):
    pass


class ConversationRecord(SelectableHorizontalRecord):

    def __init__(self, **kwargs):
        super(ConversationRecord, self).__init__(**kwargs)
        self.visible_buttons = []

    def show_buttons(self):
        if not self.visible_buttons:
            chat_button = ConversationActionButton(
                icon='comments-multiple',
                on_release=self.on_chat_button_clicked,
            )
            self.visible_buttons.append(chat_button)
            self.add_widget(chat_button)

    def hide_buttons(self):
        if self.visible_buttons:
            for w in self.visible_buttons:
                self.remove_widget(w)
            self.visible_buttons.clear()

    def on_chat_button_clicked(self, *args):
        if self.global_id.startswith('master$'):
            self.parent.parent.parent.parent.parent.parent.main_win().select_screen(
                screen_id='private_chat_{}'.format(self.global_id.replace('master$', '')),
                screen_type='private_chat_screen',
                global_id=self.global_id,
                username=self.label,
            )


class ConversationsListView(SelectableRecycleView):

    def on_selection_applied(self, item, index, is_selected, prev_selected):
        if is_selected != prev_selected:
            if is_selected:
                item.show_buttons()
            else:
                item.hide_buttons()


class ConversationsScreen(AppScreen):

    def get_icon(self):
        return 'comment-text-multiple'

    def get_title(self):
        return 'conversations'


    def populate(self, *args, **kwargs):
        api_client.message_conversations_list(cb=self.on_message_conversations_list_result)

    def on_pre_enter(self, *args):
        self.populate()

    def on_message_conversations_list_result(self, resp):
        if not isinstance(resp, dict):
            self.ids.conversations_list_view.data = []
            return
        result = resp.get('payload', {}).get('response' , {}).get('result', {})
        if not result:
            self.ids.conversations_list_view.data = []
            return
        self.ids.conversations_list_view.data = []
        for one_conversation in result:
            self.ids.conversations_list_view.data.append(one_conversation)

    def on_create_new_group_button_clicked(self, *args):
        self.main_win().select_screen('create_group_screen')

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./screens/screen_conversations.kv')
