import time

#------------------------------------------------------------------------------

from components import screen

from lib import websock
from lib import api_client

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

class RecoverIdentityScreen(screen.AppScreen):

    def get_icon(self):
        return 'account-key'

    def get_title(self):
        return 'recover identity'

    def is_closable(self):
        return True

    def on_start_recover_identity_button_clicked(self, *args):
        self.ids.recover_identity_button.disabled = True
        api_client.identity_recover(
            private_key_source=self.ids.private_key_input.text,
            join_network=True,
            cb=self.on_identity_recover_result,
        )

    def on_identity_recover_result(self, resp):
        if _Debug:
            print('on_identity_recover_result', resp)
        self.ids.recover_identity_button.disabled = False
        self.ids.recover_identity_result_message.from_api_response(resp)
        if not websock.is_ok(resp):
            # self.ids.recover_identity_result_message.text =  '[color=#ff0000]{}[/color]'.format('\n'.join(websock.response_errors(resp)))
            return
        self.main_win().close_screen('new_identity_screen')
        self.main_win().close_screen('recover_identity_screen')
        self.main_win().select_screen('connecting_screen')
        self.control().identity_get_latest = time.time()
        self.main_win().state_identity_get = 1

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./screens/screen_recover_identity.kv')
