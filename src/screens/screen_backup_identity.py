import os
import time

from kivy.clock import mainthread

#------------------------------------------------------------------------------

from lib import system
from lib import api_client

from components import screen
from components import snackbar

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

class BackupIdentityScreen(screen.AppScreen):

    def get_title(self):
        return 'backup secret key'

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

    @mainthread
    def on_save_private_key_pressed(self, *args):
        if _Debug:
            print('BackupIdentityScreen.on_save_private_key_pressed', args)
        api_client.identity_get(cb=self.on_identity_get_result)

    def on_identity_get_result(self, resp):
        if _Debug:
            print('BackupIdentityScreen.on_identity_get_result', resp)
        if not api_client.is_ok(resp):
            return
        result = api_client.response_result(resp)
        if not result:
            return
        self.my_identity_name = result.get('name', '')
        filename = 'BitDust_master_key_{}.txt'.format(self.my_identity_name) if self.my_identity_name else 'BitDust_key.txt'
        if system.is_android():
            from android.storage import app_storage_path  # @UnresolvedImport
            destination_filepath = os.path.join(app_storage_path(), filename)
        else:
            destination_filepath = os.path.join(os.path.expanduser('~'), filename)
        api_client.identity_backup(
            destination_filepath=destination_filepath,
            cb=lambda resp: self.on_identity_backup_result(resp, destination_filepath),
        )

    def on_identity_backup_result(self, resp, destination_filepath):
        if _Debug:
            print('BackupIdentityScreen.on_identity_backup_result', destination_filepath, resp)
        if system.is_android():
            from androidstorage4kivy import SharedStorage  # @UnresolvedImport
            shared_path = SharedStorage().copy_to_shared(destination_filepath)
            try:
                os.remove(destination_filepath)
            except Exception as e:
                if _Debug:
                    print(e)
            destination_filepath = shared_path
        if not api_client.is_ok(resp):
            snackbar.error(text='identity backup failed: %s' % api_client.response_err(resp))
        else:
            system.open_path_in_os(destination_filepath)
        self.ids.continue_button.disabled = False

    def on_continue_pressed(self, *args):
        screen.select_screen('welcome_screen')
        screen.close_screen('new_identity_screen')
        screen.close_screen('recover_identity_screen')
        screen.close_screen('backup_identity_screen')
        screen.stack_clear()
