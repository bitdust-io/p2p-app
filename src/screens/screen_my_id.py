import os

#------------------------------------------------------------------------------

from kivy.clock import Clock

#------------------------------------------------------------------------------

from lib import system
from lib import api_client

from components import screen
from components import dialogs
from components import snackbar

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

identity_details_temlate_text = """
[size={text_size}][color=#909090]name:[/color] [b]{name}[/b]

[color=#909090]global ID:[/color] [b]{global_id}[/b]

[color=#909090]network interfaces:[/color]
{contacts}

[color=#909090]identity servers:[/color]
{sources}

[color=#909090]created:[/color] {date}

[color=#909090]revision:[/color] {revision}

[color=#909090]version:[/color]
[size={small_text_size}]{version}[/size]

[color=#909090]public key:[/color]
[size={small_text_size}][font=RobotoMono-Regular]{publickey}[/font][/size]

[color=#909090]digital signature:[/color]
[size={small_text_size}][font=RobotoMono-Regular]{signature}[/font][/size]

[/size]
"""

create_new_identity_text = """
To be able to start using BitDust,
please [u][color=#0000ff][ref=new_identity]create new identity[/ref][/color][/u] or
[u][color=#0000ff][ref=recover_identity]recover from backup copy[/ref][/color][/u] first
"""

#------------------------------------------------------------------------------

class MyIDScreen(screen.AppScreen):

    my_identity_name = None

    # def get_icon(self):
    #     return 'account-box'

    def get_title(self):
        return 'my identity'

    def get_statuses(self):
        return {
            None: "identity-propagate service is not started",
            "ON": "identity file is synchronized",
            "OFF": "identity-propagate service is switched off",
            "NOT_INSTALLED": "identity not exist",
            "INFLUENCE": "turning off dependent network services",
            "STARTING": "identity-propagate service is starting",
            "DEPENDS_OFF": "related network services were not started yet",
            "STOPPING": "identity-propagate service is stopping",
            "CLOSED": "identity-propagate service is closed",
        }

    def on_enter(self, *args):
        self.ids.state_panel.attach(automat_id='service_identity_propagate')
        api_client.identity_get(cb=self.on_identity_get_result)

    def on_leave(self, *args):
        self.ids.state_panel.release()

    def on_identity_get_result(self, resp):
        if not api_client.is_ok(resp):
            self.ids.my_id_details.text = create_new_identity_text
            return
        result = api_client.response_result(resp)
        if not result:
            self.ids.my_id_details.text = create_new_identity_text
            return
        self.my_identity_name = result.get('name', '')
        self.ids.my_id_details.text = identity_details_temlate_text.format(
            text_size='{}sp'.format(self.app().font_size_normal_absolute),
            small_text_size='{}sp'.format(self.app().font_size_small_absolute),
            name=result.get('name', ''),
            global_id=result.get('global_id', ''),
            publickey=result.get('publickey', ''),
            signature=result.get('signature', ''),
            date=result.get('date', ''),
            version=result.get('version', ''),
            revision=result.get('revision', ''),
            sources='\n'.join(result.get('sources', [])),
            contacts='\n'.join(result.get('contacts', [])),
        )

    def on_my_id_details_ref_pressed(self, *args):
        if _Debug:
            print('MyIDScreen.on_my_id_details_ref_pressed', args)
        if args[1] == 'new_identity':
            self.main_win().select_screen('new_identity_screen')
        elif args[1] == 'recover_identity':
            self.main_win().select_screen('recover_identity_screen')

    def on_drop_down_menu_item_clicked(self, btn):
        if _Debug:
            print('MyIDScreen.on_drop_down_menu_item_clicked', btn.icon)
        if btn.icon == 'shield-key':
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
        elif btn.icon == 'cellphone-remove':
            dialogs.open_yes_no_dialog(
                title='Erase my identity and the private key',
                text='WARNING!\n\nAll your data will become\ncompletely inaccessible\nwithout a private key!\n\nMake sure you already\nhave a backup copy\nof your private key.',
                cb=self.on_confirm_erase_my_id,
            )
        elif btn.icon == 'lan-pending':
            api_client.network_reconnect(cb=self.on_network_reconnect_result)
        elif btn.icon == 'cog-refresh':
            self.app().restart_engine()
            snackbar.info(text='BitDust background process is restarting')
        elif btn.icon == 'power':
            self.app().stop_engine()
            snackbar.info(text='BitDust background process will be stopped')

    def on_confirm_erase_my_id(self, answer):
        if _Debug:
            print('MyIDScreen.on_confirm_erase_my_id', answer)
        if answer == 'yes':
            api_client.process_stop()
            self.main_win().engine_is_on = False
            Clock.schedule_once(self.on_process_stop_result_erase_my_id, 1)

    def on_network_reconnect_result(self, resp):
        if not api_client.is_ok(resp):
            snackbar.error(text='disconnected: %s' % api_client.response_err(resp))
        else:
            snackbar.info(text='network connection refreshed')

    def on_identity_backup_result(self, resp, destination_filepath):
        if _Debug:
            print('MyIDScreen.on_identity_backup_result', destination_filepath, resp)
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

    def on_process_stop_result_start_engine(self, resp):
        if _Debug:
            print('MyIDScreen.on_process_stop_result_start_engine', resp)
        self.app().start_engine()
        snackbar.info(text='BitDust node process restarted')

    def on_process_stop_result_erase_my_id(self, *args):
        if _Debug:
            print('MyIDScreen.on_process_stop_result_erase_my_id', args)
        home_folder_path = os.path.join(os.path.expanduser('~'), '.bitdust')
        if system.is_android():
            from android.storage import app_storage_path  # @UnresolvedImport
            home_folder_path = os.path.join(app_storage_path(), '.bitdust')
        try:
            current_network = open(os.path.join(home_folder_path, 'current_network'), 'r').read().strip()
        except:
            current_network = 'default'
        system.rmdir_recursive(os.path.join(home_folder_path, current_network, 'metadata'), ignore_errors=False)
        system.rmdir_recursive(os.path.join(home_folder_path, current_network, 'backups'), ignore_errors=True)
        system.rmdir_recursive(os.path.join(home_folder_path, current_network, 'config'), ignore_errors=True)
        system.rmdir_recursive(os.path.join(home_folder_path, current_network, 'identitycache'), ignore_errors=True)
        system.rmdir_recursive(os.path.join(home_folder_path, current_network, 'identityhistory'), ignore_errors=True)
        system.rmdir_recursive(os.path.join(home_folder_path, current_network, 'keys'), ignore_errors=True)
        system.rmdir_recursive(os.path.join(home_folder_path, current_network, 'messages'), ignore_errors=True)
        system.rmdir_recursive(os.path.join(home_folder_path, current_network, 'servicedata'), ignore_errors=True)
        system.rmdir_recursive(os.path.join(home_folder_path, current_network, 'suppliers'), ignore_errors=True)
        system.rmdir_recursive(os.path.join(home_folder_path, current_network, 'customers'), ignore_errors=True)
        system.rmdir_recursive(os.path.join(home_folder_path, 'temp'), ignore_errors=True)
        snackbar.info(text='private key erased')
        self.app().start_engine()
        self.main_win().select_screen('welcome_screen')
        self.main_win().close_screen('new_identity_screen')
        self.main_win().close_screen('recover_identity_screen')
        self.main_win().screens_stack.clear()
