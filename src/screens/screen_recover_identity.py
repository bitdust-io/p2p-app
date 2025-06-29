import os

from kivy.clock import Clock, mainthread

#------------------------------------------------------------------------------

from lib import system
from lib import api_client

from components import screen

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

class RecoverIdentityScreen(screen.AppScreen):

    # def get_title(self):
    #     return 'recover identity'

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

    def on_leave(self, *args):
        self.ids.state_panel.release()

    def on_start_recover_identity_button_clicked(self, *args):
        self.ids.recover_identity_button.disabled = True
        self.ids.recover_identity_result_message.text = ''
        api_client.identity_recover(
            private_key_source=self.ids.private_key_input.text,
            join_network=True,
            cb=self.on_identity_recover_result,
        )

    def on_identity_recover_result(self, resp):
        if _Debug:
            print('RecoverIdentityScreen.on_identity_recover_result', resp)
        self.ids.recover_identity_button.disabled = False
        self.ids.recover_identity_result_message.from_api_response(resp)
        if not api_client.is_ok(resp):
            return
        self.main_win().state_identity_get = 0
        self.control().run()
        screen.select_screen('welcome_screen')
        screen.close_screen('new_identity_screen')
        screen.close_screen('recover_identity_screen')
        screen.stack_clear()

    @mainthread
    def on_load_private_key_pressed(self, *args):
        if _Debug:
            print('RecoverIdentityScreen.on_load_private_key_pressed', args)
        if system.is_android():
            from lib import filechooser_android
            raw_path = filechooser_android.open_file(
                title="Load private key file",
                preview=True,
                show_hidden=False,
                on_selection=self.on_load_private_key_selected,
            )
        elif system.is_osx():
            from lib import filechooser_macosx
            fc = filechooser_macosx.MacFileChooser(
                title="Load private key file",
                preview=True,
                show_hidden=False,
                on_selection=self.on_upload_file_selected,
            )
            raw_path = fc.run()
        else:
            from plyer import filechooser
            if system.is_windows():
                self._latest_cwd = os.getcwd()
            raw_path = filechooser.open_file(
                title="Load private key file",
                preview=True,
                show_hidden=False,
                on_selection=self.on_load_private_key_selected,
            )
        if _Debug:
            print('    raw_path', raw_path)

    def on_load_private_key_selected(self, *args, **kwargs):
        if _Debug:
            print('RecoverIdentityScreen.on_load_private_key_selected', args, kwargs)
        if system.is_windows():
            try:
                os.chdir(self._latest_cwd)
            except:
                pass
        file_path = args[0][0]
        try:
            key_src = system.ReadTextFile(file_path)
        except:
            key_src = None
            import traceback
            traceback.print_exc()
        if _Debug:
            print('length: %r' % len(str(key_src)))
        Clock.schedule_once(lambda dt: self.do_update_input_field(key_src))

    def do_update_input_field(self, key_src):
        if _Debug:
            print('RecoverIdentityScreen.do_update_input_field: %r' % key_src)
        if not key_src:
            self.ids.recover_identity_button.disabled = False
            self.ids.recover_identity_result_message.text = '[color=#f00]loading private key failed[/color]'
            self.ids.private_key_input.text = ''
            return
        try:
            self.ids.recover_identity_button.disabled = False
            self.ids.recover_identity_result_message.text = ''
            self.ids.private_key_input.text = key_src
        except:
            import traceback
            traceback.print_exc()
        if _Debug:
            print('SUCCESS')

