import time

#------------------------------------------------------------------------------

from lib import api_client

from components import screen

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

class NewIdentityScreen(screen.AppScreen):

    def get_title(self):
        return 'create new identity'

    def get_statuses(self):
        return {
            None: '',
            'AT_STARTUP': 'starting',
            'LOCAL': 'initializing local environment',
            'MODULES': 'starting sub-modules',
            'INSTALL': 'installing application',
            'READY': 'application is ready',
            'STOPPING': 'application is shutting down',
            'SERVICES': 'starting network services',
            'INTERFACES': 'starting application interfaces',
            'EXIT': 'application is closed',
        }

    def on_enter(self, *args):
        self.ids.state_panel.attach(automat_id='initializer')
        self.ids.create_identity_button.disabled = False
        self.ids.create_identity_result_message.text = ''

    def on_leave(self, *args):
        self.ids.state_panel.release()

    def on_username_input_key_enter_pressed(self, *args):
        self.ids.create_identity_button.disabled = True
        self.ids.create_identity_result_message.text = ''
        api_client.identity_create(
            username=self.ids.username_input.text,
            join_network=True,
            cb=self.on_identity_create_result,
        )

    def on_create_identity_button_clicked(self, *args):
        self.ids.create_identity_button.disabled = True
        self.ids.create_identity_result_message.text = ''
        api_client.identity_create(
            username=self.ids.username_input.text,
            join_network=True,
            cb=self.on_identity_create_result,
        )

    def on_identity_create_result(self, resp):
        if _Debug:
            print('on_identity_create_result', resp)
        self.ids.create_identity_button.disabled = False
        self.ids.create_identity_result_message.from_api_response(resp)
        if not api_client.is_ok(resp):
            return
        self.main_win().state_identity_get = 0
        self.control().run()
        screen.select_screen('backup_identity_screen')
        screen.close_screen('new_identity_screen')
        screen.close_screen('recover_identity_screen')
        screen.stack_clear()
