from kivy.clock import Clock

from kivymd.uix.tab import MDTabsBase
from kivymd.uix.floatlayout import MDFloatLayout

#------------------------------------------------------------------------------

from lib import system
from lib import web_sock_remote

from components import screen
from components import dialogs
from components import snackbar

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

class TabLocalDevice(MDFloatLayout, MDTabsBase):

    def on_local_device_button_clicked(self, *args):
        if _Debug:
            print('TabLocalDevice.on_local_device_button_clicked', args)
        screen.main_window().state_node_local = True
        screen.my_app().client_info['local'] = screen.main_window().state_node_local
        screen.my_app().save_client_info()
        screen.stack_clear()
        screen.stack_append('welcome_screen')
        screen.my_app().do_start_controller()

#------------------------------------------------------------------------------

class TabRemoteDevice(MDFloatLayout, MDTabsBase):

    server_code_input_dialog = None
    confirmation_code_dialog = None
    spinner_dialog = None
    device_check_task = None

    def on_remote_device_button_clicked(self, *args):
        if _Debug:
            print('TabRemoteDevice.on_remote_device_button_clicked', args)
        screen.my_app().load_client_info()
        screen.my_app().client_info['local'] = False
        screen.my_app().client_info.pop('client_code', None)
        screen.my_app().save_client_info()
        screen.main_window().state_node_local = False
        screen.main_window().state_device_authorized = True
        screen.stack_clear()
        screen.stack_append('welcome_screen')
        screen.my_app().do_start_controller()

    def on_qr_scan_open_button_clicked(self, *args):
        if _Debug:
            print('TabRemoteDevice.on_qr_scan_open_button_clicked', args)
        screen.select_screen(
            screen_id='scan_qr_screen',
            scan_qr_callback=self.on_scan_qr_ready,
            cancel_callback=self.on_scan_qr_cancel,
        )

    def on_scan_qr_cancel(self, *args):
        if _Debug:
            print('TabRemoteDevice.on_scan_qr_cancel', args)
        screen.screen_back()

    def on_scan_qr_ready(self, *args):
        if _Debug:
            print('TabRemoteDevice.on_scan_qr_ready', args)
        router_url = None
        if args:
            router_url = args[0].strip()
        screen.screen_back()
        screen.main_window().state_node_local = False
        screen.my_app().client_info['local'] = screen.main_window().state_node_local
        if router_url:
            screen.my_app().client_info['routers'] = [router_url, ]
        screen.my_app().client_info.pop('key', None)
        screen.my_app().client_info.pop('server_public_key', None)
        screen.my_app().client_info.pop('auth_token', None)
        screen.my_app().client_info.pop('session_key', None)
        screen.my_app().save_client_info()
        self.ids.qr_scan_open_button.disabled = True
        self.spinner_dialog = dialogs.open_spinner_dialog(
            title='',
            label='connecting',
            button_cancel='[u][color=#0000dd]Cancel[/color][/u]',
            cb_cancel=self.on_cancel_spinner_dialog,
        )
        Clock.schedule_once(self.do_connect)

    def on_websocket_open(self, ws_inst):
        if _Debug:
            print('TabRemoteDevice.on_websocket_open', ws_inst)

    def on_websocket_connect(self, ws_inst):
        if _Debug:
            print('TabRemoteDevice.on_websocket_connect', ws_inst)
        if self.spinner_dialog:
            self.spinner_dialog.dismiss()
            self.spinner_dialog = None
        if web_sock_remote.is_started():
            web_sock_remote.stop()
        screen.my_app().load_client_info()
        success = bool(screen.my_app().client_info.get('auth_token'))
        self.ids.qr_scan_open_button.disabled = False
        self.ids.remote_device_button.disabled = not success
        if self.confirmation_code_dialog:
            self.confirmation_code_dialog.dismiss()
            self.confirmation_code_dialog = None
        if success:
            snackbar.info(text='device authorized successfully')
        else:
            snackbar.error(text='device was not authorized')

    def on_websocket_handshake_failed(self, ws_inst, error):
        if _Debug:
            print('TabRemoteDevice.on_websocket_handshake_failed', ws_inst, error)
        if self.spinner_dialog:
            self.spinner_dialog.dismiss()
            self.spinner_dialog = None
        snackbar.error(text=str(error))
        self.ids.qr_scan_open_button.disabled = False

    def on_websocket_error(self, ws_inst, error):
        if _Debug:
            print('TabRemoteDevice.on_websocket_error', ws_inst, error)
        if self.spinner_dialog:
            self.spinner_dialog.dismiss()
            self.spinner_dialog = None
        snackbar.error(text=str(error))
        self.ids.qr_scan_open_button.disabled = False

    def on_websocket_handshake_started(self):
        if _Debug:
            print('TabRemoteDevice.on_websocket_handshake_started')
        if self.spinner_dialog:
            self.spinner_dialog.dismiss()
            self.spinner_dialog = None
        self.server_code_input_dialog = dialogs.open_number_input_dialog(
            title='Authorization code',
            text='Enter 6-digits authorization code generated on the remote BitDust node:',
            button_confirm='Continue',
            button_cancel='Back',
            cb=self.on_server_code_entered,
        )

    def on_websocket_server_disconnected(self):
        if _Debug:
            print('TabRemoteDevice.on_websocket_server_disconnected')
        if web_sock_remote.is_started():
            web_sock_remote.stop()
        if self.device_check_task:
            self.device_check_task.cancel()
            self.device_check_task = None
        self.device_check_task = Clock.schedule_once(self.do_connect, 2)

    def on_server_code_entered(self, inp):
        if _Debug:
            print('TabRemoteDevice.on_server_code_entered', inp)
        self.server_code_input_dialog = None
        if not inp:
            self.ids.qr_scan_open_button.disabled = False
            return
        client_code = web_sock_remote.continue_handshake(server_code=inp)
        self.confirmation_code_dialog = dialogs.open_message_dialog(
            title='Confirmation code',
            text='[color=#000]Enter the confirmation code dispalyed bellow in your BitDust node Desktop app:\n\n\n[size=24sp]%s[/size][/color]' % client_code,
            button_confirm='Continue',
            cb=self.on_confirmation_code_dialog_closed,
        )

    def on_confirmation_code_dialog_closed(self, *args, **kwargs):
        self.confirmation_code_dialog = None
        self.ids.qr_scan_open_button.disabled = False

    def on_cancel_spinner_dialog(self):
        self.ids.qr_scan_open_button.disabled = False
        self.spinner_dialog = None
        if web_sock_remote.is_started():
            web_sock_remote.stop()

    def do_connect(self, interval=None):
        web_sock_remote.start(
            callbacks={
                'on_open': self.on_websocket_open,
                'on_handshake_failed': self.on_websocket_handshake_failed,
                'on_connect': self.on_websocket_connect,
                'on_error': self.on_websocket_error,
                'on_handshake_started': self.on_websocket_handshake_started,
                'on_server_disconnected': self.on_websocket_server_disconnected,
            },
            client_info_filepath=screen.my_app().client_info_file_path,
        )

#------------------------------------------------------------------------------

class TabCloudServer(MDFloatLayout, MDTabsBase):

    def on_cloud_device_button_clicked(self, *args):
        if _Debug:
            print('TabRemoteDevice.on_cloud_device_button_clicked', args)

#------------------------------------------------------------------------------

class DeviceConnectScreen(screen.AppScreen):

    def get_title(self):
        return 'BitDust node configuration'

    def on_tab_switched(self, *args):
        if _Debug:
            print('DeviceConnectScreen.on_tab_switched', args)

    def on_enter(self, *args):
        if _Debug:
            print('DeviceConnectScreen.on_enter', args)
        if system.is_android():
            self.ids.selection_tabs.ids.carousel.slides[0].ids.local_device_button.disabled = True

    def on_leave(self, *args):
        if _Debug:
            print('DeviceConnectScreen.on_leave', args)
