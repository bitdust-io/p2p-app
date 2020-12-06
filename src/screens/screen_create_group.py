from components.screen import AppScreen

from lib import api_client
from lib import websock

#------------------------------------------------------------------------------

class CreateGroupScreen(AppScreen):

    def get_icon(self):
        return 'chat-plus'

    def get_title(self):
        return 'create group'

    def clean_view(self, clear_input_field=False):
        if clear_input_field:
            self.ids.group_label_input.text = ''
        self.ids.status_message_label.text = ''

    def on_enter(self):
        self.clean_view(clear_input_field=True)

    def on_create_group_button_clicked(self, *args):
        self.ids.status_message_label.text = ''
        self.ids.create_group_button.disabled = True
        self.ids.group_label_input.disabled = True
        api_client.group_create(
            label=self.ids.group_label_input.text or None,
            cb=self.on_group_create_result,
        )

    def on_group_create_result(self, resp):
        if not websock.is_ok(resp):
            self.ids.status_message_label.text = str(websock.response_errors(resp))
            self.ids.status_message_label.text = ''
            self.ids.create_group_button.disabled = False
            self.ids.group_label_input.disabled = False
            return
        self.ids.status_message_label.text = ''
        self.ids.create_group_button.disabled = False
        self.ids.group_label_input.disabled = False
        self.main_win().select_screen('conversations_screen')
        self.main_win().close_screen('create_group_screen')

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./screens/screen_create_group.kv')
