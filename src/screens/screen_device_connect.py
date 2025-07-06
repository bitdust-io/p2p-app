import re
import os
import base64
import time

try:
    import thread
except ImportError:
    import _thread as thread

#------------------------------------------------------------------------------

from kivy.clock import Clock, mainthread

from kivymd.uix.tab import MDTabsBase
from kivymd.uix.floatlayout import MDFloatLayout

#------------------------------------------------------------------------------

from lib import system

_USE_PYCRYPTODOME = True

if system.is_ios() or system.is_android():
    _USE_PYCRYPTODOME = False

from lib import strng
from lib import jsn
from lib import util
from lib import web_sock_remote

if _USE_PYCRYPTODOME:
    from lib import rsa_key
    from lib import cipher
    from lib import hashes
else:
    from lib import rsa_key_slow as rsa_key
    from lib import cipher_slow as cipher
    from lib import hashes_slow as hashes

from components import screen
from components import dialogs
from components import snackbar

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

class WebSocketConnectorController(object):

    server_code_input_dialog = None
    confirmation_code_dialog = None
    spinner_dialog = None
    device_check_task = None
    busy = False
    callback_on_success = None
    callback_on_fail = None
    connecting_client_info_file_path = None

    def load_client_info_from_access_code(self, inp):
        try:
            url, encrypted_payload, client_code, client_key_body, client_key_label, client_key_size, server_public_key, signature = inp.split('&')
        except:
            raise Exception('invalid access key format')
        if not client_key_body.startswith('-----BEGIN RSA PRIVATE KEY-----'):
            client_key_body = '-----BEGIN RSA PRIVATE KEY-----\\n' + client_key_body
        if not client_key_body.endswith('-----END RSA PRIVATE KEY-----'):
            client_key_body = client_key_body + '\\n-----END RSA PRIVATE KEY-----'
        try:
            client_key_body = client_key_body.replace('\\n', '\n')            
            client_key_object = rsa_key.RSAKey()
            client_key_object.fromDict({
                'body': client_key_body,
                'label': client_key_label,
            })
        except:
            raise Exception('invalid client key')
        if str(client_key_object.size()) != str(client_key_size):
            raise Exception('invalid client key size')
        if not server_public_key.startswith('ssh-rsa '):
            server_public_key = 'ssh-rsa ' + server_public_key
        try:
            server_key_object = rsa_key.RSAKey()
            server_key_object.fromString(server_public_key)
        except:
            raise Exception('invalid server key')
        try:
            orig_encrypted_payload = base64.b64decode(strng.to_bin(encrypted_payload))
            received_salted_payload = strng.to_text(client_key_object.decrypt(orig_encrypted_payload))
            hashed_payload = hashes.sha1(strng.to_bin(received_salted_payload))
            received_client_code, auth_token, session_key_text, _ = received_salted_payload.split('#')
        except:
            raise Exception('access key verification failed')
        if received_client_code != client_code:
            raise Exception('client code is not matching')
        if not server_key_object.verify(strng.to_bin(signature), hashed_payload):
            raise Exception('signature verification failed')
        auth_info = {
            'state': 'authorized',
            'auth_token': auth_token,
            'session_key': session_key_text,
        }
        return url, auth_info

    def start_connecting(self, router_url, auth_info, on_success=None, on_fail=None): 
        if not router_url:
            if on_fail:
                on_fail(None)
            return
        if self.busy:
            if on_fail:
                on_fail(None)
            return
        self.busy = True
        self.callback_on_success = on_success
        self.callback_on_fail = on_fail
        router_url = util.unpack_device_url(router_url.strip())
        _client_info = {}
        _client_info.update(auth_info)
        _client_info['local'] = False
        _client_info['name'] = util.shorten_device_url(router_url.strip()) + '_' + time.strftime('%Y%m%d%I%M%S', time.localtime())
        _client_info['listeners'] = [router_url, ]
        self.connecting_client_info_file_path = os.path.join(system.get_app_data_path(), 'connecting_info')
        system.WriteTextFile(self.connecting_client_info_file_path, jsn.dumps(_client_info, indent=2))
        self.spinner_dialog = dialogs.open_spinner_dialog(
            title='',
            label='connecting',
            button_cancel='Cancel',
            cb_cancel=self.on_cancel_spinner_dialog,
        )
        if web_sock_remote.is_started():
            web_sock_remote.stop()
        Clock.schedule_once(self._do_connect, 1)

    def on_websocket_open(self, ws_inst):
        if _Debug:
            print('WebSocketConnectorController.on_websocket_open', ws_inst)

    def on_websocket_connect(self, ws_inst):
        if _Debug:
            print('WebSocketConnectorController.on_websocket_connect', ws_inst, self.callback_on_success)
        if self.spinner_dialog:
            self.spinner_dialog.dismiss()
            self.spinner_dialog = None
        if web_sock_remote.is_started():
            web_sock_remote.stop()
        connecting_info = jsn.loads(system.ReadTextFile(self.connecting_client_info_file_path) or '{}')
        if not connecting_info:
            if self.callback_on_fail:
                self.callback_on_fail(Exception('device connection info loading failed'), (ws_inst, ))
                self.callback_on_fail = None
            return
        success = bool(connecting_info.get('auth_token'))
        if self.confirmation_code_dialog:
            self.confirmation_code_dialog.dismiss()
            self.confirmation_code_dialog = None
        if success:
            snackbar.info(text='device authorized successfully')
        else:
            snackbar.error(text='device was not authorized')
        if success:
            if self.callback_on_success:
                self.callback_on_success(True)
                self.callback_on_success = None
        else:
            if self.callback_on_fail:
                self.callback_on_fail(Exception('device was not authorized'), (ws_inst, ))
                self.callback_on_fail = None

    def on_websocket_handshake_failed(self, ws_inst, error):
        if _Debug:
            print('WebSocketConnectorController.on_websocket_handshake_failed', ws_inst, error)
        self.busy = False
        if self.spinner_dialog:
            self.spinner_dialog.dismiss()
            self.spinner_dialog = None
        if self.confirmation_code_dialog:
            self.confirmation_code_dialog.dismiss()
            self.confirmation_code_dialog = None
        if self.server_code_input_dialog:
            self.server_code_input_dialog.dismiss()
            self.server_code_input_dialog = None
        if self.callback_on_fail:
            self.callback_on_fail(error, (ws_inst, ))
            self.callback_on_fail = None

    def on_websocket_error(self, ws_inst, error):
        if _Debug:
            print('WebSocketConnectorController.on_websocket_error', ws_inst, error)
        self.busy = False
        if self.spinner_dialog:
            self.spinner_dialog.dismiss()
            self.spinner_dialog = None
        snackbar.error(text=str(error))
        # self.ids.qr_scan_open_button.disabled = not system.is_mobile()

    def on_websocket_handshake_started(self, ws_inst):
        if _Debug:
            print('WebSocketConnectorController.on_websocket_handshake_started', ws_inst)
        if self.spinner_dialog:
            self.spinner_dialog.dismiss()
            self.spinner_dialog = None
        self.server_code_input_dialog = dialogs.open_number_input_dialog(
            title='Device authorization code',
            text='Please enter the 4-digits authorization code generated in BitDust node running on your desktop/server computer:',
            min_text_length=4,
            max_text_length=4,
            button_confirm='Continue',
            button_cancel='Back',
            cb=self.on_server_code_entered,
        )

    def on_websocket_server_disconnected(self, ws_inst):
        if _Debug:
            print('WebSocketConnectorController.on_websocket_server_disconnected', ws_inst)
        if web_sock_remote.is_started():
            web_sock_remote.stop()
        if self.device_check_task:
            self.device_check_task.cancel()
            self.device_check_task = None
        self.device_check_task = Clock.schedule_once(self._do_connect, 2)

    def on_server_code_entered(self, inp):
        if _Debug:
            print('WebSocketConnectorController.on_server_code_entered', inp, self.server_code_input_dialog)
        if not self.server_code_input_dialog:
            return
        self.server_code_input_dialog = None
        if not inp:
            self.busy = False
            if web_sock_remote.is_started():
                web_sock_remote.stop()
            return
        client_code = web_sock_remote.continue_handshake(server_code=inp)
        self.confirmation_code_dialog = dialogs.open_message_dialog(
            title='Device confirmation code',
            text='[color=#000]Here is your device confirmation code:\n\n[size=24sp]%s[/size]\n\nEnter those 4 digits in the BitDust node running on your desktop/server computer to complete device authorization procedure.[/color]' % client_code,
            button_confirm='Continue',
            cb=self.on_confirmation_code_dialog_closed,
        )

    def on_confirmation_code_dialog_closed(self, *args, **kwargs):
        self.confirmation_code_dialog = None
        self.busy = False

    def on_cancel_spinner_dialog(self):
        self.busy = False
        self.spinner_dialog = None
        if web_sock_remote.is_started():
            web_sock_remote.stop()

    def _do_connect(self, interval=None):
        if _Debug:
            print('WebSocketConnectorController._do_connect')
        web_sock_remote.start(
            callbacks={
                'on_open': self.on_websocket_open,
                'on_handshake_failed': self.on_websocket_handshake_failed,
                'on_connect': self.on_websocket_connect,
                'on_error': self.on_websocket_error,
                'on_handshake_started': self.on_websocket_handshake_started,
                'on_server_disconnected': self.on_websocket_server_disconnected,
            },
            client_info_filepath=self.connecting_client_info_file_path,
        )

#------------------------------------------------------------------------------

class TabLocalDevice(MDFloatLayout, MDTabsBase):

    def on_local_device_button_clicked(self, *args):
        if _Debug:
            print('TabLocalDevice.on_local_device_button_clicked', args)
        screen.my_app().set_client_info({
            'local': True,
            'name': 'local',
        })
        screen.main_window().state_node_local = 1
        screen.stack_clear()
        screen.stack_append('welcome_screen')
        screen.my_app().do_start_controller()

#------------------------------------------------------------------------------

class TabRemoteDevice(MDFloatLayout, MDTabsBase, WebSocketConnectorController):

    def on_remote_device_text_ref_pressed(self, *args):
        if _Debug:
            print('TabRemoteDevice.on_remote_device_text_ref_pressed', args)
        if args[1] == 'web_site_link':
            system.open_url('https://bitdust.io')
        
    def on_qr_scan_open_button_clicked(self, *args):
        if _Debug:
            print('TabRemoteDevice.on_qr_scan_open_button_clicked', args)
        screen.select_screen(
            screen_id='scan_qr_screen',
            scan_qr_callback=self.on_scan_qr_ready,
        )

    def on_scan_qr_ready(self, *args):
        if _Debug:
            print('TabRemoteDevice.on_scan_qr_ready', args)
        screen.screen_back()
        router_url = None
        if args:
            router_url = args[0].strip()
        if not router_url:
            return
        self.start_connecting(
            router_url=router_url,
            auth_info={},
            on_success=self.on_remote_device_connection_success,
            on_fail=self.on_remote_device_connection_failed,
        )

    def on_remote_device_connection_success(self, args):
        if _Debug:
            print('TabRemoteDevice.on_remote_device_connection_success', args)
        connecting_info = jsn.loads(system.ReadTextFile(self.connecting_client_info_file_path) or '{}')
        if not connecting_info:
            snackbar.error(text='client info update failed')
            return
        screen.my_app().set_client_info(connecting_info)
        screen.main_window().state_node_local = 0
        screen.main_window().state_device_authorized = True
        screen.stack_clear()
        screen.stack_append('welcome_screen')
        screen.my_app().do_start_controller()
        try:
            os.remove(self.connecting_client_info_file_path)
            self.connecting_client_info_file_path = None
        except Exception as exc:
            if _Debug:
                print('TabRemoteDevice.on_remote_device_connection_success failed: %r' % exc)

    def on_remote_device_connection_failed(self, err, args):
        if _Debug:
            print('TabRemoteDevice.on_remote_device_connection_failed', err, args)
        snackbar.error(text=str(err))
        try:
            os.remove(self.connecting_client_info_file_path)
            self.connecting_client_info_file_path = None
        except Exception as exc:
            if _Debug:
                print('TabRemoteDevice.on_remote_device_connection_failed: %r' % exc)

#------------------------------------------------------------------------------

class TabServerDevice(MDFloatLayout, MDTabsBase, WebSocketConnectorController):

    url_input_dialog = None

    def on_server_text_ref_pressed(self, *args):
        if _Debug:
            print('TabServerDevice.on_server_text_ref_pressed', args)
        if args[1] == 'wiki_install_page_link':
            system.open_url('https://bitdust.io/wiki/install.html')
        elif args[1] == 'wiki_device_config_page_link':
            system.open_url('https://bitdust.io/wiki/devices.html')
        
    def on_url_enter_button_clicked(self, *args):
        if _Debug:
            print('TabServerDevice.on_url_enter_button_clicked', args)
        self.url_input_dialog = dialogs.open_text_input_dialog(
            title='Connection info',
            text='Enter device connection URL generated on the remote BitDust node:',
            button_confirm='Continue',
            button_cancel='Back',
            cb=self.on_url_entered,
        )

    def on_url_entered(self, inp):
        if _Debug:
            print('TabServerDevice.on_url_entered', inp)
        if self.url_input_dialog:
            self.url_input_dialog.dismiss()
            self.url_input_dialog = None
        if not inp:
            return
        self.start_connecting(
            router_url=inp,
            auth_info={},
            on_success=self.on_server_device_connection_success,
            on_fail=self.on_server_device_connection_failed,
        )

    def on_server_device_connection_success(self, args):
        if _Debug:
            print('TabServerDevice.on_server_device_connection_success', args)
        connecting_info = jsn.loads(system.ReadTextFile(self.connecting_client_info_file_path) or '{}')
        if not connecting_info:
            snackbar.error(text='client info update failed')
            return
        screen.my_app().set_client_info(connecting_info)
        screen.main_window().state_node_local = 0
        screen.main_window().state_device_authorized = True
        screen.stack_clear()
        screen.stack_append('welcome_screen')
        screen.my_app().do_start_controller()
        try:
            os.remove(self.connecting_client_info_file_path)
            self.connecting_client_info_file_path = None
        except Exception as exc:
            if _Debug:
                print('TabRemoteDevice.on_server_device_connection_success failed: %r' % exc)

    def on_server_device_connection_failed(self, err, args):
        if _Debug:
            print('TabServerDevice.on_server_device_connection_failed', err, args)
        snackbar.error(text=str(err))
        try:
            os.remove(self.connecting_client_info_file_path)
            self.connecting_client_info_file_path = None
        except Exception as exc:
            if _Debug:
                print('TabRemoteDevice.on_server_device_connection_failed: %r' % exc)

#------------------------------------------------------------------------------

class TabDemoDevice(MDFloatLayout, MDTabsBase, WebSocketConnectorController):

    access_key_input_dialog = None

    def on_demo_text_ref_pressed(self, *args):
        if _Debug:
            print('TabDemoDevice.on_demo_text_ref_pressed', args)
        if args[1] == 'bitdust_email_link':
            system.open_url('mailto:bitdust.io@gmail.com')
        elif args[1] == 'bitdust_telegram_link':
            system.open_url('https://t.me/bitdust')

    def on_access_key_enter_button_clicked(self, *args):
        if _Debug:
            print('TabDemoDevice.on_access_key_enter_button_clicked', args)
        self.access_key_input_dialog = dialogs.open_text_input_dialog(
            title='Access key',
            text='Paste access key text content:',
            multiline=True,
            button_confirm='Continue',
            button_cancel='Back',
            cb=self.on_access_key_entered,
        )

    def on_access_key_entered(self, inp):
        if _Debug:
            print('TabDemoDevice.on_access_key_entered', inp)
        if self.access_key_input_dialog:
            self.access_key_input_dialog.dismiss()
            self.access_key_input_dialog = None
        if not inp:
            return
        inp = inp.replace('-----BEGIN DEVICE ACCESS KEY-----', '').replace('-----END DEVICE ACCESS KEY-----', '').strip()
        try:
            router_url, auth_info = self.load_client_info_from_access_code(inp)
        except Exception as err:
            snackbar.error(text=str(err))
            return
        self.start_connecting(
            router_url=router_url,
            auth_info=auth_info,
            on_success=self.on_demo_device_connection_success,
            on_fail=self.on_demo_device_connection_failed,
        )

    def on_demo_device_connection_success(self, args):
        if _Debug:
            print('TabDemoDevice.on_demo_device_connection_success', args)
        connecting_info = jsn.loads(system.ReadTextFile(self.connecting_client_info_file_path) or '{}')
        if not connecting_info:
            snackbar.error(text='client info update failed')
            return
        screen.my_app().set_client_info(connecting_info)
        screen.main_window().state_node_local = 0
        screen.main_window().state_device_authorized = True
        screen.stack_clear()
        screen.stack_append('welcome_screen')
        screen.my_app().do_start_controller()
        try:
            os.remove(self.connecting_client_info_file_path)
            self.connecting_client_info_file_path = None
        except Exception as exc:
            if _Debug:
                print('TabDemoDevice.on_demo_device_connection_success failed: %r' % exc)

    def on_demo_device_connection_failed(self, err, args):
        if _Debug:
            print('TabDemoDevice.on_demo_device_connection_failed', err, args)
        snackbar.error(text=str(err))
        try:
            os.remove(self.connecting_client_info_file_path)
            self.connecting_client_info_file_path = None
        except Exception as exc:
            if _Debug:
                print('TabDemoDevice.on_demo_device_connection_failed: %r' % exc)

#------------------------------------------------------------------------------

class TabWebdockIODevice(MDFloatLayout, MDTabsBase, WebSocketConnectorController):

    api_token_input_dialog = None
    log_progress_dialog = None

    def _webdock_io_run_thread(self, on_progress, on_check_stopped, on_result):
        if _Debug:
            print('TabWebdockIODevice._webdock_io_run_thread STARTED')
        try:
            from lib import webdock_io
            full_log = webdock_io.run(
                api_token=self.api_token,
                cb_progress=on_progress,
                cb_check_stopped=on_check_stopped,
            )
        except Exception as exc:
            if _Debug:
                print('TabWebdockIODevice._webdock_io_run_thread returned: %r' % exc)
            full_log = exc
            if on_progress:
                on_progress(str(exc))
        if on_result:
            on_result(full_log)
        if _Debug:
            print('TabWebdockIODevice._webdock_io_run_thread ENDING')

    def on_webdock_io_text_ref_pressed(self, *args):
        if _Debug:
            print('TabWebdockIODevice.on_webdock_io_text_ref_pressed', args)
        if args[1] == 'webdock_io_link':
            system.open_url('https://webdock.io')
        elif args[1] == 'webdock_io_profile_page_link':
            system.open_url('https://webdock.io/en/dash/profile')
        elif args[1] == 'webdock_io_signup_link':
            system.open_url('https://webdock.io/en/signup')

    def on_webdock_io_api_token_enter_button_clicked(self):
        if _Debug:
            print('TabWebdockIODevice.on_webdock_io_api_token_enter_button_clicked')
        self.api_token_input_dialog = dialogs.open_text_input_dialog(
            title='Webdock.io API token',
            text='Copy & paste here API token from Webdock.io > Account > API & Integrations section:',
            button_confirm='Continue',
            button_cancel='Back',
            cb=self.on_webdock_io_api_token_entered,
        )

    def on_webdock_io_api_token_entered(self, inp):
        if _Debug:
            print('TabWebdockIODevice.on_webdock_io_api_token_entered', inp)
        if self.api_token_input_dialog:
            self.api_token_input_dialog.dismiss()
            self.api_token_input_dialog = None
        if not inp:
            return
        t = inp.strip()
        if not t:
            return
        self.api_token = t
        self.thread_cancelled = False
        if self.log_progress_dialog:
            self.log_progress_dialog.dismiss()
            self.log_progress_dialog = None
        self.log_progress_dialog = dialogs.open_log_progress_dialog(
            title='Webdock.io server configuration',
            button_cancel='Cancel',
            cb_open=self.on_log_progress_dialog_opened,
            cb_cancel=self.on_cancel_webdock_io_log_progress_dialog,
        )

    def on_log_progress_dialog_opened(self, content):
        if _Debug:
            print('TabWebdockIODevice.on_log_progress_dialog_opened', content)
        self.log_progress_dialog_content = content
        thread.start_new_thread(self._webdock_io_run_thread, (
            self.on_log_progress_callback,
            self.on_check_webdock_io_thread_stopped,
            self.on_webdock_io_thread_result,
        ))

    @mainthread
    def on_log_progress_callback(self, input_text):
        if _Debug:
            print('TabWebdockIODevice.on_log_progress_callback', self.log_progress_dialog_content, input_text)
        if self.log_progress_dialog_content:
            self.log_progress_dialog_content.ids.log_content.text += input_text

    def on_check_webdock_io_thread_stopped(self):
        if _Debug:
            print('TabWebdockIODevice.on_check_webdock_io_thread_stopped', self.thread_cancelled)
        return self.thread_cancelled

    @mainthread
    def on_cancel_webdock_io_log_progress_dialog(self):
        if _Debug:
            print('TabWebdockIODevice.on_cancel_webdock_io_log_progress_dialog')
        self.thread_cancelled = True
        self.log_progress_dialog = None
        self.log_progress_dialog_content = None

    @mainthread
    def on_webdock_io_thread_result(self, result):
        access_code_lookup = re.search('-----BEGIN DEVICE ACCESS KEY-----(.+?)-----END DEVICE ACCESS KEY-----', str(result), flags=(re.MULTILINE | re.DOTALL))
        if _Debug:
            print('TabWebdockIODevice.on_webdock_io_thread_result with %d bytes: %r' % (len(str(result)), access_code_lookup))
        if not access_code_lookup:
            if self.log_progress_dialog:
                self.log_progress_dialog.ids.button_box.children[0].text = 'Close'
            return
        access_code = access_code_lookup.group(1).strip()
        if self.log_progress_dialog:
            self.log_progress_dialog.dismiss()
            self.log_progress_dialog = None
        try:
            router_url, auth_info = self.load_client_info_from_access_code(access_code)
        except Exception as err:
            snackbar.error(text=str(err))
            return
        self.start_connecting(
            router_url=router_url,
            auth_info=auth_info,
            on_success=self.on_webdock_io_device_connection_success,
            on_fail=self.on_webdock_io_device_connection_failed,
        )

    def on_webdock_io_device_connection_success(self, args):
        if _Debug:
            print('TabWebdockIODevice.on_webdock_io_device_connection_success', args)
        connecting_info = jsn.loads(system.ReadTextFile(self.connecting_client_info_file_path) or '{}')
        if not connecting_info:
            snackbar.error(text='client info update failed')
            return
        screen.my_app().set_client_info(connecting_info)
        screen.main_window().state_node_local = 0
        screen.main_window().state_device_authorized = True
        screen.stack_clear()
        screen.stack_append('welcome_screen')
        screen.my_app().do_start_controller()
        try:
            os.remove(self.connecting_client_info_file_path)
            self.connecting_client_info_file_path = None
        except Exception as exc:
            if _Debug:
                print('TabWebdockIODevice.on_webdock_io_device_connection_success failed: %r' % exc)

    def on_webdock_io_device_connection_failed(self, err, args):
        if _Debug:
            print('TabWebdockIODevice.on_webdock_io_device_connection_failed', err, args)
        snackbar.error(text=str(err))
        try:
            os.remove(self.connecting_client_info_file_path)
            self.connecting_client_info_file_path = None
        except Exception as exc:
            if _Debug:
                print('TabWebdockIODevice.on_webdock_io_device_connection_failed: %r' % exc)

#------------------------------------------------------------------------------

class DeviceConnectScreen(screen.AppScreen):

    # def get_title(self):
    #     return 'node configuration'

    def on_tab_switched(self, *args):
        if _Debug:
            print('DeviceConnectScreen.on_tab_switched', args)

    def on_enter(self, *args):
        if _Debug:
            print('DeviceConnectScreen.on_enter', args)
        if not self.ids.selection_tabs.ids.carousel.slides:
            if not system.is_mobile():
                self.ids.selection_tabs.add_widget(TabLocalDevice(title='This device'))
            if system.is_mobile():
                self.ids.selection_tabs.add_widget(TabRemoteDevice(title='Remote desktop'))
            self.ids.selection_tabs.add_widget(TabServerDevice(title='Remote server'))
            self.ids.selection_tabs.add_widget(TabWebdockIODevice(title='Webdock.io'))
            self.ids.selection_tabs.add_widget(TabDemoDevice(title='Demo'))

    def on_leave(self, *args):
        if _Debug:
            print('DeviceConnectScreen.on_leave', args)
