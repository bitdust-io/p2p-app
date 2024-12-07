from lib import api_client

from components import screen
from components import snackbar

#------------------------------------------------------------------------------

class DeviceConnectScreen(screen.AppScreen):

    # def get_icon(self):
    #     return 'chat-plus'

    def get_title(self):
        return 'connect to BitDust Node'

    def clean_view(self, clear_input_field=False):
        if clear_input_field:
            self.ids.url_input.text = ''
        self.ids.status_message_label.text = ''

    def on_enter(self):
        self.clean_view(clear_input_field=True)
