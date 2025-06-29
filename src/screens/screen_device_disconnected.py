from kivy.clock import Clock
from kivy.clock import mainthread

#------------------------------------------------------------------------------

from lib import web_sock_remote

from components import screen

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

class DeviceDisconnectedScreen(screen.AppScreen):

    device_check_task = None
    device_process_health_task = None

    # def get_title(self):
    #     return 'connecting to BitDust node'

    def on_enter(self, *args):
        if screen.main_window().state_node_local == 1:
            self.do_start_controller()
            return
        if not screen.main_window().state_device_authorized:
            self.do_open_device_connect_screen()
            return
        self.counter = 0
        self.ids.spinner.start(label='connecting')
        if self.device_check_task:
            self.device_check_task.cancel()
            self.device_check_task = None
        self.device_check_task = Clock.schedule_once(self.do_connect)

    def on_leave(self, *args):
        self.ids.spinner.stop()

    def on_websocket_open(self, ws_inst):
        if _Debug:
            print('DeviceDisconnectedScreen.on_websocket_open', ws_inst)

    def on_websocket_connect(self, ws_inst):
        if _Debug:
            print('DeviceDisconnectedScreen.on_websocket_connect', ws_inst)
        if self.device_process_health_task:
            self.device_process_health_task.cancel()
            self.device_process_health_task = None
        self.device_process_health_task = Clock.schedule_once(self.do_process_health, 0)

    def do_process_health(self, *args, **kwargs):
        if _Debug:
            print('DeviceDisconnectedScreen.do_process_health', args, kwargs)
        jd = {'command': 'api_call', 'method': 'process_health', 'kwargs': {}, }
        web_sock_remote.ws_call(json_data=jd, cb=self.on_process_health_result)
        if self.device_process_health_task:
            self.device_process_health_task.cancel()
            self.device_process_health_task = None
        self.device_process_health_task = Clock.schedule_once(self.do_process_health, 5)

    def on_process_health_result(self, resp):
        if _Debug:
            print('DeviceDisconnectedScreen.on_process_health_result %r' % resp)
        if self.device_process_health_task:
            self.device_process_health_task.cancel()
            self.device_process_health_task = None
        if web_sock_remote.is_started():
            web_sock_remote.stop()
        if not isinstance(resp, dict):
            self.do_populate_text_label()
            if self.device_check_task:
                self.device_check_task.cancel()
                self.device_check_task = None
            self.device_check_task = Clock.schedule_once(self.do_connect, 5)
            return False
        if resp.get('payload', {}).get('response', {}).get('status', '') != 'OK':
            self.do_populate_text_label()
            if self.device_check_task:
                self.device_check_task.cancel()
                self.device_check_task = None
            self.device_check_task = Clock.schedule_once(self.do_connect, 5)
            return False
        self.do_start_controller()

    def on_websocket_handshake_failed(self, ws_inst, error):
        if _Debug:
            print('DeviceDisconnectedScreen.on_websocket_handshake_failed', ws_inst, error)
        if web_sock_remote.is_started():
            web_sock_remote.stop()
        self.do_open_device_connect_screen()

    def on_websocket_error(self, ws_inst, error):
        if _Debug:
            print('DeviceDisconnectedScreen.on_websocket_error', ws_inst, error)
        if web_sock_remote.is_started():
            web_sock_remote.stop()
        self.do_populate_text_label()
        if self.device_check_task:
            self.device_check_task.cancel()
            self.device_check_task = None
        self.device_check_task = Clock.schedule_once(self.do_connect, 5)

    def on_websocket_handshake_started(self, ws_inst):
        if _Debug:
            print('DeviceDisconnectedScreen.on_websocket_handshake_started', ws_inst)
        if web_sock_remote.is_started():
            web_sock_remote.stop()
        self.do_open_device_connect_screen()

    def on_websocket_server_disconnected(self, ws_inst):
        if _Debug:
            print('DeviceDisconnectedScreen.on_websocket_server_disconnected', ws_inst)
        if web_sock_remote.is_started():
            web_sock_remote.stop()
        self.do_populate_text_label()
        if self.device_check_task:
            self.device_check_task.cancel()
            self.device_check_task = None
        self.device_check_task = Clock.schedule_once(self.do_connect, 5)

    def on_text_label_ref_pressed(self, *args):
        if _Debug:
            print('DeviceDisconnectedScreen.on_text_label_ref_pressed', args)
        if web_sock_remote.is_started():
            web_sock_remote.stop()
        self.do_open_device_connect_screen()

    def do_populate_text_label(self):
        if self.counter > 0:
            self.ids.text_label.text = 'The application is trying to connect to a remote BitDust node.\n' \
            'Make sure the BitDust app is running on your remote machine and the Internet is stable on both devices.\n' \
            'You can also [u][color=#0000ff][ref=link]re-authorize[/ref][/color][/u] your device again.'

    def do_start_controller(self):
        if _Debug:
            print('DeviceDisconnectedScreen.do_start_controller')
        if self.device_check_task:
            self.device_check_task.cancel()
            self.device_check_task = None
        screen.stack_clear()
        screen.stack_append('welcome_screen')
        screen.my_app().do_start_controller()
        screen.close_screen('device_disconnected_screen')

    def do_open_device_connect_screen(self):
        if _Debug:
            print('DeviceDisconnectedScreen.do_open_device_connect_screen')
        if self.device_check_task:
            self.device_check_task.cancel()
            self.device_check_task = None
        screen.select_screen('device_connect_screen', clear_stack=True)
        screen.close_active_screens(exclude_screens=['device_connect_screen', ])
        screen.stack_clear()

    def do_connect(self, interval=None):
        if _Debug:
            print('DeviceDisconnectedScreen.do_connect')
        if web_sock_remote.is_started():
            web_sock_remote.stop()
            Clock.schedule_once(self.do_start_connecting, .1)
        else:
            self.do_start_connecting()

    @mainthread
    def do_start_connecting(self, interval=None):
        if _Debug:
            print('DeviceDisconnectedScreen.do_start_connecting', self.counter)
        self.counter += 1
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
