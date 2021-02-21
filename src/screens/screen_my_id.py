import os

#------------------------------------------------------------------------------

from kivy.metrics import dp
from kivy.core.window import Window

from kivymd.uix.snackbar import Snackbar

#------------------------------------------------------------------------------

from components import screen

from lib import system
from lib import api_client
from lib import websock

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

identity_details_temlate_text = """
[size={text_size}][color=#909090]name:[/color] [b]{name}[/b]

[color=#909090]global ID:[/color] [b]{global_id}[/b]

[color=#909090]incoming channels:[/color]
{contacts}

[color=#909090]sources:[/color]
{sources}

[color=#909090]created:[/color] {date}

[color=#909090]revision:[/color] {revision}

[color=#909090]version:[/color]
[size={small_text_size}]{version}[/size]

[color=#909090]public key:[/color]
[size={small_text_size}][font=RobotoMono-Regular]{publickey}[/font][/size]

[/size]
"""

#------------------------------------------------------------------------------

class MyIDScreen(screen.AppScreen):

    def get_icon(self):
        return 'account-box'

    def get_title(self):
        return 'my identity'

    def get_dropdown_menu_items(self):
        return [
            {'text': 'reconnect', },
            {'text': 'restart engine', },
            {'text': 'key backup', },
            {'text': 'erase my ID', },
        ]

    def on_enter(self, *args):
        api_client.identity_get(cb=self.on_identity_get_result)

    def on_identity_get_result(self, resp):
        if not websock.is_ok(resp):
            self.ids.my_id_details.text = str(resp)
            return
        result = websock.response_result(resp)
        if not result:
            self.ids.my_id_details.text = websock.response_err(resp)
            return
        self.ids.my_id_details.text = identity_details_temlate_text.format(
            text_size='{}sp'.format(self.app().font_size_normal_absolute),
            small_text_size='{}sp'.format(self.app().font_size_small_absolute),
            name=result.get('name', ''),
            global_id=result.get('global_id', ''),
            publickey=result.get('publickey', ''),
            date=result.get('date', ''),
            version=result.get('version', ''),
            revision=result.get('revision', ''),
            sources='\n'.join(result.get('sources', [])),
            contacts='\n'.join(result.get('contacts', [])),
        )

    def on_dropdown_menu_item_clicked(self, menu_inst, item_inst):
        if item_inst.text == 'key backup':
            destination_filepath = os.path.join(os.path.expanduser('~'), 'bitdust_key.txt')
            if system.is_android():
                destination_filepath = os.path.join('/storage/emulated/0/', 'bitdust_key.txt')
            api_client.identity_backup(
                destination_filepath=destination_filepath,
                cb=lambda resp: self.on_identity_backup_result(resp, destination_filepath),
            )
        elif item_inst.text == 'erase my ID':
            api_client.process_stop(cb=self.on_process_stop_result_erase_my_id)
        elif item_inst.text == 'reconnect':
            api_client.network_reconnect()
        elif item_inst.text == 'restart engine':
            api_client.process_stop(cb=self.on_process_stop_result_start_engine)
        

    def on_identity_backup_result(self, resp, destination_filepath):
        if not websock.is_ok(resp):
            self.ids.my_id_details.text = str(resp)
            Snackbar(
                text='identity backup failed: %s' % websock.response_err(resp),
                bg_color=self.theme_cls.error_color,
                duration=5,
                snackbar_x="10dp",
                snackbar_y="10dp",
                size_hint_x=(
                    Window.width - (dp(10) * 2)
                ) / Window.width
            ).open()
        else:
            Snackbar(
                text='backup copy of the private key stored in: %s' % destination_filepath,
                bg_color=self.theme_cls.accent_color,
                duration=5,
                snackbar_x="10dp",
                snackbar_y="10dp",
                size_hint_x=(
                    Window.width - (dp(10) * 2)
                ) / Window.width
            ).open()

    def on_process_stop_result_start_engine(self, resp):
        self.app().start_engine()
        Snackbar(
            text='BitDust node process restarted',
            bg_color=self.theme_cls.accent_color,
            duration=5,
            snackbar_x="10dp",
            snackbar_y="10dp",
            size_hint_x=(
                Window.width - (dp(10) * 2)
            ) / Window.width
        ).open()
        

    def on_process_stop_result_erase_my_id(self, resp):
        home_folder_path = os.path.join(os.path.expanduser('~'), '.bitdust')
        if system.is_android():
            home_folder_path = os.path.join('/storage/emulated/0/', '.bitdust')
        system.rmdir_recursive(os.path.join(home_folder_path, 'backups'))
        system.rmdir_recursive(os.path.join(home_folder_path, 'config'))
        system.rmdir_recursive(os.path.join(home_folder_path, 'identitycache'))
        system.rmdir_recursive(os.path.join(home_folder_path, 'identityhistory'))
        system.rmdir_recursive(os.path.join(home_folder_path, 'keys'))
        system.rmdir_recursive(os.path.join(home_folder_path, 'metadata'))
        system.rmdir_recursive(os.path.join(home_folder_path, 'messages'))
        system.rmdir_recursive(os.path.join(home_folder_path, 'servicedata'))
        system.rmdir_recursive(os.path.join(home_folder_path, 'suppliers'))
        system.rmdir_recursive(os.path.join(home_folder_path, 'customers'))
        system.rmdir_recursive(os.path.join(home_folder_path, 'temp'))
        Snackbar(
            text='your identity and private key were erased',
            bg_color=self.theme_cls.accent_color,
            duration=5,
            snackbar_x="10dp",
            snackbar_y="10dp",
            size_hint_x=(
                Window.width - (dp(10) * 2)
            ) / Window.width
        ).open()
        self.app().start_engine()
