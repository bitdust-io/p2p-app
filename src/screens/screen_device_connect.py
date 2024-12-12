from kivymd.uix.tab import MDTabsBase
from kivymd.uix.floatlayout import MDFloatLayout

#------------------------------------------------------------------------------

from lib import system
from lib import web_sock_remote

from components import screen
from components import dialogs

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

    def on_remote_device_button_clicked(self, *args):
        if _Debug:
            print('TabRemoteDevice.on_remote_device_button_clicked', args)

    def on_qr_scan_open_button_clicked(self, *args):
        if _Debug:
            print('TabRemoteDevice.on_qr_scan_open_button_clicked', args)
        screen.select_screen(
            screen_id='scan_qr_screen',
            scan_qr_callback=self.on_scan_qr_ready,
            cancel_callback=self.on_scan_qr_cancel,
        )

    def on_scan_qr_ready(self, *args):
        if _Debug:
            print('TabRemoteDevice.on_scan_qr_ready', args)
        screen.screen_back()
        screen.main_window().state_node_local = False
        screen.my_app().client_info['local'] = screen.main_window().state_node_local
        screen.my_app().client_info['routers'] = [args[0].strip(), ]
        screen.my_app().save_client_info()
        web_sock_remote.start(
            callbacks={
                'on_open': self.on_websocket_open,
                'on_handshake_failed': self.on_websocket_handshake_failed,
                'on_connect': self.on_websocket_connect,
                'on_error': self.on_websocket_error,
                'on_handshake_started': self.on_websocket_handshake_started,
            },
            client_info_filepath=screen.my_app().client_info_file_path,
        )

    def on_scan_qr_cancel(self, *args):
        if _Debug:
            print('TabRemoteDevice.on_scan_qr_cancel', args)
        screen.screen_back()

    def on_websocket_open(self, ws_inst):
        if _Debug:
            print('TabRemoteDevice.on_websocket_open', ws_inst)

    def on_websocket_connect(self, ws_inst):
        if _Debug:
            print('TabRemoteDevice.on_websocket_connect', ws_inst)
        screen.my_app().load_client_info()
        screen.my_app().client_info['local'] = False
        screen.main_window().state_node_local = False
        screen.main_window().state_device_authorized = True
        web_sock_remote.stop()

    def on_websocket_handshake_started(self):
        if _Debug:
            print('TabRemoteDevice.on_websocket_handshake_started')
        dialogs.open_number_input_dialog(
            title='Authorization code',
            text='Enter 6-digits authorization code generated on the remote BitDust node:',
            cb=self.on_auth_code_entered,
        )

    def on_websocket_handshake_failed(self, ws_inst, err):
        if _Debug:
            print('TabRemoteDevice.on_websocket_handshake_failed', ws_inst, err)

    def on_websocket_error(self, ws_inst, error):
        if _Debug:
            print('TabRemoteDevice.on_websocket_error', ws_inst, error)

    def on_auth_code_entered(self, inp):
        if _Debug:
            print('TabRemoteDevice.on_auth_code_entered', inp)
        web_sock_remote.continue_handshake(inp)

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
        if system.is_android():
            self.ids.selection_tabs.ids.carousel.slides[0].ids.local_device_button.disabled = True
