from components.screen import AppScreen
from service import websock


class RecoverIdentityScreen(AppScreen):

    def is_closable(self):
        return False

    def on_start_recover_identity_button_clicked(self, *args):
        self.ids.recover_identity_button.disabled = True
        websock.ws_call(
            json_data={
                "command": "api_call",
                "method": "identity_recover",
                "kwargs": {
                    "private_key_source": self.ids.private_key_input.text,
                },
            },
            cb=self.on_identity_recover_result,
        )

    def on_identity_recover_result(self, resp):
        self.ids.recover_identity_button.disabled = False
        if not isinstance(resp, dict):
            self.ids.recover_identity_result_message.text =  '[color=#ff0000]{}[/color]'.format('\n'.join(websock.response_errors(resp)))
            return
        if not websock.is_ok(resp):
            self.ids.recover_identity_result_message.text =  '[color=#ff0000]{}[/color]'.format('\n'.join(websock.response_errors(resp)))
            return
        self.main_win().close_screen('new_identity_screen')
        self.main_win().close_screen('recover_identity_screen')
        self.main_win().select_screen('welcome_screen')
        self.control().run()


from kivy.lang.builder import Builder 
Builder.load_file('./screens/screen_recover_identity.kv')
