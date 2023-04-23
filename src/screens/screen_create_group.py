from lib import api_client

from components import screen
from components import snackbar

#------------------------------------------------------------------------------

class CreateGroupScreen(screen.AppScreen):

    # def get_icon(self):
    #     return 'chat-plus'

    def get_title(self):
        return 'create new group'

    def clean_view(self, clear_input_field=False):
        if clear_input_field:
            self.ids.group_label_input.text = ''
        self.ids.status_message_label.text = ''

    def on_enter(self):
        self.clean_view(clear_input_field=True)

    def on_create_group_button_clicked(self, *args):
        if not self.ids.group_label_input.text:
            return
        self.ids.status_message_label.text = ''
        self.ids.create_group_button.disabled = True
        self.ids.group_label_input.disabled = True
        api_client.group_create(
            label=self.ids.group_label_input.text,
            cb=self.on_group_create_result,
        )

    def on_group_create_result(self, resp):
        if not api_client.is_ok(resp):
            snackbar.error(text=api_client.response_err(resp))
            self.ids.create_group_button.disabled = False
            self.ids.group_label_input.disabled = False
            return
        api_client.group_join(group_key_id=api_client.response_result(resp).get('group_key_id'))
        self.ids.status_message_label.text = ''
        self.ids.create_group_button.disabled = False
        self.ids.group_label_input.disabled = False
        self.main_win().select_screen('conversations_screen')
        self.main_win().close_screen('create_group_screen')
        self.main_win().screens_stack.clear()
        self.main_win().screens_stack.append('welcome_screen')
