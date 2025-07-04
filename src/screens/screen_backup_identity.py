import os

from kivy.clock import mainthread

#------------------------------------------------------------------------------

from lib import system
from lib import api_client
from lib import api_file_transfer

from components import screen
from components import snackbar

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

class BackupIdentityScreen(screen.AppScreen):

    # def get_title(self):
    #     return 'backup secret key'

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
        self.ids.continue_button.disabled = True
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
            snackbar.error(text=api_client.response_err(resp))
            self.ids.continue_button.disabled = False
            return
        result = api_client.response_result(resp)
        if not result:
            self.ids.continue_button.disabled = False
            return
        self.my_identity_name = result.get('name', '')
        self.filename = f'BitDust_{self.my_identity_name}_master_key.txt' if self.my_identity_name else 'BitDust_master_key.txt'
        if screen.control().is_local:
            destination_filepath = os.path.join(system.get_documents_dir(), self.filename)
        else:
            destination_filepath = ''
        api_client.identity_backup(
            destination_filepath=destination_filepath,
            cb=self.on_identity_backup_result,
        )

    def on_identity_backup_result(self, resp):
        if _Debug:
            print('BackupIdentityScreen.on_identity_backup_result', resp)
        if not api_client.is_ok(resp):
            snackbar.error(text=api_client.response_err(resp))
            self.ids.continue_button.disabled = False
            return
        result = api_client.response_result(resp)
        if not result:
            self.ids.continue_button.disabled = False
            return
        downloaded_path = result.get('local_path')
        if screen.control().is_local:
            if downloaded_path and os.path.exists(downloaded_path):
                system.open_path_in_os(downloaded_path)
            self.ids.continue_button.disabled = False
            return
        destination_path = os.path.join(system.get_downloads_dir(), self.filename)
        api_file_transfer.file_download(
            source_path=downloaded_path,
            destination_path=destination_path,
            result_callback=self.on_file_transfer_result,
        )

    def on_file_transfer_result(self, result):
        if _Debug:
            print('BackupIdentityScreen.on_file_transfer_result', result)
        screen.main_window().state_file_transfering = False
        if isinstance(result, Exception):
            snackbar.error(text=str(result))
            self.ids.continue_button.disabled = False
            return
        snackbar.success(text='downloading is complete')
        self.ids.continue_button.disabled = False
        destination_path = os.path.join(system.get_downloads_dir(), self.filename)
        if system.is_android():
            from androidstorage4kivy import SharedStorage  # @UnresolvedImport
            local_uri = SharedStorage().copy_to_shared(private_file=destination_path)
            if local_uri:
                system.open_path_in_os(local_uri)
        else:
            system.open_path_in_os(destination_path)

    def on_continue_pressed(self, *args):
        screen.select_screen('welcome_screen')
        screen.close_screen('new_identity_screen')
        screen.close_screen('recover_identity_screen')
        screen.close_screen('backup_identity_screen')
        screen.stack_clear()
