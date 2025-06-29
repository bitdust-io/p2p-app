import os

#------------------------------------------------------------------------------

from lib import api_client
from lib import system
from lib import jsn

from components import screen
from components import styles

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

class EngineStatusScreen(screen.AppScreen):

    state_panel_attached = False

    # def get_title(self):
    #     return 'status'

    def get_statuses(self):
        return {
            None: 'main process is not started yet',
            'AT_STARTUP': 'starting the application',
            'LOCAL': 'initializing local environment',
            'MODULES': 'starting sub-modules',
            'INSTALL': 'installing application',
            'READY': 'application is ready',
            'STOPPING': 'application is shutting down',
            'SERVICES': 'starting network services',
            'INTERFACES': 'starting application interfaces',
            'EXIT': 'application is closed',
        }

    def populate(self):
        if _Debug:
            print('EngineStatusScreen.populate state_panel_attached=%r' % self.state_panel_attached)
        if screen.main_window().state_node_local == 1:
            self.ids.button_engine_on.disabled = False
            self.on_service(None)
        else:
            self.ids.button_engine_on.disabled = True
        _t = ''
        _s = self.app().selected_client
        for client_info_name in self.app().list_client_info_records():
            if self.main_win().state_node_local == 1 or self.main_win().state_device_authorized:
                if client_info_name == _s:
                    continue
            _t += f'  [u][color=#0000ff][ref={client_info_name}_link]{self.shorten_client_info_name(client_info_name)}[/ref][/color][/u]'
            if client_info_name == 'local' or client_info_name == _s:
                _t += '\n'
            else:
                _t += f'  [u][color=#ff0000][ref={client_info_name}_delete][delete][/ref][/color][/u]\n'
        if self.main_win().state_node_local == 1:
            if _t:
                _t = f'\nBitDust node is currently configured to run on this device. You can add [u][color=#0000ff][ref=add_new_configuration_link]new configuration[/ref][/color][/u] or select one of the known configurations:\n' + _t
            else:
                _t = '\nBitDust node is currently configured to run on this device, but you can add [u][color=#0000ff][ref=add_new_configuration_link]new configuration[/ref][/color][/u] to run it remotely.\n'
        else:
            if self.main_win().state_device_authorized:
                if _t:
                    _t = f'\nBitDust node is currently configured to run on a remote device [b]{self.shorten_client_info_name(_s)}[/b]. You can add [u][color=#0000ff][ref=add_new_configuration_link]new configuration[/ref][/color][/u] or select one of the known configurations:\n' + _t
                else:
                    _t = f'\nBitDust node is currently configured to run on a remote device [b]{self.shorten_client_info_name(_s)}[/b]. Also a [u][color=#0000ff][ref=add_new_configuration_link]new configuration[/ref][/color][/u] can be added.\n'
            else:
                _t = '\nBitDust node is not configured yet, click [u][color=#0000ff][ref=add_new_configuration_link]new configuration[/ref][/color][/u] to start.\n'
        self.ids.device_configurations_content_label.text = _t

    def set_nw_progress(self, v):
        self.ids.connection_progress.value = v
        if v == 100:
            self.ids.connection_progress.color = styles.app.color_success_green
        else:
            self.ids.connection_progress.color = self.theme_cls.primary_color

    def shorten_client_info_name(self, inp):
        if '_' not in inp:
            return inp
        h, _, _ = inp.rpartition('_')
        return h

    def on_enter(self, *args):
        if _Debug:
            print('EngineStatusScreen.on_enter')
        if self.main_win().engine_is_on:
            if not self.state_panel_attached:
                self.state_panel_attached = self.ids.state_panel.attach(automat_id='initializer')
        api_client.add_model_listener('service', listener_cb=self.on_service)
        self.populate()

    def on_leave(self, *args):
        if _Debug:
            print('EngineStatusScreen.on_leave')
        api_client.remove_model_listener('service', listener_cb=self.on_service)
        if self.state_panel_attached:
            self.ids.state_panel.release()
        self.state_panel_attached = False

    def on_engine_on_off(self, *args):
        if _Debug:
            print('EngineStatusScreen.on_engine_on_off', args)
        st = args[0]
        if st:
            self.app().start_engine()
            self.state_panel_attached = self.ids.state_panel.attach(automat_id='initializer')
            self.populate()
        else:
            self.set_nw_progress(0)
            if self.state_panel_attached:
                self.ids.state_panel.release()
            self.state_panel_attached = False
            self.app().stop_engine()
            self.set_nw_progress(0)

    def on_network_connection_status_pressed(self, *args):
        if _Debug:
            print('EngineStatusScreen.on_network_connection_status_pressed', args)
        screen.select_screen('connecting_screen')

    def on_service(self, payload):
        if _Debug:
            print('EngineStatusScreen.on_service')
        if not self.main_win().engine_is_on:
            self.set_nw_progress(0)
            return
        services_by_state = {}
        count_total = 0.0
        count_on = 0.0
        for snap_info in self.model('service').values():
            if snap_info:
                svc = snap_info['data']
                st = svc.get('state')
                if not svc.get('installed'):
                    continue
                if not svc.get('enabled'):
                    continue
                if st not in services_by_state:
                    services_by_state[st] = {}
                services_by_state[st][svc['name']] = svc
                count_total += 1.0
                if st == 'ON':
                    count_on += 1.0
        if count_total:
            self.set_nw_progress(int(100.0 * count_on / count_total))
        else:
            self.set_nw_progress(0)

    def on_device_configurations_content_link_pressed(self, *args):
        if _Debug:
            print('EngineStatusScreen.on_device_configurations_content_link_pressed', args)
        if args[1] == 'add_new_configuration_link':
            self.app().selected_client = None
            if self.control().enabled:
                self.control().stop()
            self.main_win().state_node_local = -1
            self.main_win().state_device_authorized = False
            self.main_win().state_process_health = -1
            self.main_win().state_identity_get = -1
            self.main_win().state_rebuilding = False
            self.main_win().state_file_transfering = False
            self.main_win().state_network_connected = -1
            self.main_win().state_entangled_dht = -1
            self.main_win().state_proxy_transport = -1
            self.main_win().state_my_data = -1
            self.main_win().state_message_history = -1
            self.main_win().select_screen('device_connect_screen', clear_stack=True)
            self.main_win().close_active_screens(exclude_screens=['device_connect_screen', ])
            self.main_win().update_menu_items()
            screen.stack_clear()
        elif args[1].endswith('_delete'):
            _n = args[1].replace('_delete', '')
            _fn = os.path.join(system.get_app_data_path(), _n + '.client_info')
            if os.path.exists(_fn):
                try:
                    os.remove(_fn)
                except Exception as exc:
                    if _Debug:
                        print(exc)
            self.populate()
        elif args[1].endswith('_link'):
            _n = args[1].replace('_link', '')
            _fn = os.path.join(system.get_app_data_path(), _n + '.client_info')
            _info = jsn.loads(system.ReadTextFile(_fn) or '{}')
            if not _info:
                return
            if not _info.get('local') and not _info.get('auth_token'):
                return
            if self.control().enabled:
                self.control().stop()
            screen.my_app().set_client_info(_info)
            self.main_win().state_node_local = 1 if _info.get('local') else 0
            self.main_win().state_device_authorized = True
            self.main_win().state_process_health = -1
            self.main_win().state_rebuilding = False
            self.main_win().state_file_transfering = False
            self.main_win().state_identity_get = -1
            self.main_win().state_network_connected = -1
            self.main_win().state_entangled_dht = -1
            self.main_win().state_proxy_transport = -1
            self.main_win().state_my_data = -1
            self.main_win().state_message_history = -1
            self.main_win().update_menu_items()
            screen.stack_clear()
            screen.stack_append('welcome_screen')
            self.control().start()
