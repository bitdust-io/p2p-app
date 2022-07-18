import os
import time

#------------------------------------------------------------------------------

from kivy.clock import Clock

#------------------------------------------------------------------------------

from lib import system
from lib import websock
from lib import api_client

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------
# create new screen step-by-step:
# 1. add new item in screens.controller.all_screens()
# 2. create new file screens/screen_xxx.kv
# 3. create new file screens/screen_xxx.py
# 4. make changes in components.main_win.MainWin.select_screen() if it is required for screen identification
# 5. to open screen use: screen.main_window().select_screen(screen_id='xxx_screen')
#------------------------------------------------------------------------------ 

def all_screens():
    return {
        'startup_screen': (
            'screens/screen_startup.kv', 'screens.screen_startup', 'StartUpScreen', ),
        'engine_status_screen': (
            'screens/screen_engine_status.kv', 'screens.screen_engine_status', 'EngineStatusScreen', ),
        'connecting_screen': (
            'screens/screen_connecting.kv', 'screens.screen_connecting', 'ConnectingScreen', ),
        'new_identity_screen': (
            'screens/screen_new_identity.kv', 'screens.screen_new_identity', 'NewIdentityScreen', ),
        'recover_identity_screen': (
            'screens/screen_recover_identity.kv', 'screens.screen_recover_identity', 'RecoverIdentityScreen', ),
        'welcome_screen': (
            'screens/screen_welcome.kv', 'screens.screen_welcome', 'WelcomeScreen', ),
        'settings_screen': (
            'screens/screen_settings.kv', 'screens.screen_settings', 'SettingsScreen', ),
        'my_id_screen': (
            'screens/screen_my_id.kv', 'screens.screen_my_id', 'MyIDScreen', ),
        'search_people_screen': (
            'screens/screen_search_people.kv', 'screens.screen_search_people', 'SearchPeopleScreen', ),
        'friends_screen': (
            'screens/screen_friends.kv', 'screens.screen_friends', 'FriendsScreen', ),
        'select_friend_screen': (
            'screens/screen_select_friend.kv', 'screens.screen_select_friend', 'SelectFriendScreen', ),
        'conversations_screen': (
            'screens/screen_conversations.kv', 'screens.screen_conversations', 'ConversationsScreen', ),
        'create_group_screen': (
            'screens/screen_create_group.kv', 'screens.screen_create_group', 'CreateGroupScreen', ),
        'private_chat_screen': (
            'screens/screen_private_chat.kv', 'screens.screen_private_chat', 'PrivateChatScreen', ),
        'group_chat_screen': (
            'screens/screen_group_chat.kv', 'screens.screen_group_chat', 'GroupChatScreen', ),
        'group_info_screen': (
            'screens/screen_group_info.kv', 'screens.screen_group_info', 'GroupInfoScreen', ),
        'private_files_screen': (
            'screens/screen_private_files.kv', 'screens.screen_private_files', 'PrivateFilesScreen', ),
        'single_private_file_screen': (
            'screens/screen_single_private_file.kv', 'screens.screen_single_private_file', 'SinglePrivateFileScreen', ),
        'shares_screen': (
            'screens/screen_shares.kv', 'screens.screen_shares', 'SharesScreen', ),
        'create_share_screen': (
            'screens/screen_create_share.kv', 'screens.screen_create_share', 'CreateShareScreen', ),
        'shared_location_screen': (
            'screens/screen_shared_location.kv', 'screens.screen_shared_location', 'SharedLocationScreen', ),
        'single_shared_file_screen': (
            'screens/screen_single_shared_file.kv', 'screens.screen_single_shared_file', 'SingleSharedFileScreen', ),
    }

#------------------------------------------------------------------------------

class Controller(object):

    process_health_errors = 0
    process_health_latest = 0
    identity_get_latest = 0
    network_connected_latest = 0

    def __init__(self, app):
        self.enabled = False
        self.connecting = False
        self.app = app
        self.callbacks = {}
        self.state_changed_callbacks = {}
        self.state_changed_callbacks_by_id = {}
        self.model_data = {}
        self.private_files_index = {}
        self.shared_files_index = {}
        self.remote_versions_index = {}
        self.remote_files_details = {}

    def mw(self):
        return self.app.main_window

    def start(self):
        if _Debug:
            print('Controller.start')
        self.enabled = True
        websock.start(
            callbacks={
                'on_open': self.on_websocket_open,
                'on_error': self.on_websocket_error,
                'on_stream_message': self.on_websocket_stream_message,
                'on_event': self.on_websocket_event,
                'on_model_update': self.on_model_update,
            },
            api_secret_filepath=os.path.join(system.get_app_data_path(), 'metadata', 'apisecret'),
        )
        self.mw().update_menu_items()
        self.mw().select_screen('welcome_screen')
        self.run()

    def stop(self):
        if _Debug:
            print('Controller.stop')
        self.enabled = False
        websock.stop()

    def run(self):
        if _Debug:
            print('Controller.run %r %r %r' % (self.mw().state_process_health, self.mw().state_identity_get, self.mw().state_network_connected, ))
        # BitDust node process must be running already
        if self.mw().state_process_health == 0:
            return self.verify_process_health()
        if self.mw().state_process_health == -1:
            if time.time() - self.process_health_latest > 30.0:
                return self.verify_process_health()
            return None
        # user identity must be already existing
        if self.mw().state_identity_get == 0:
            return self.verify_identity_get()
        if self.mw().state_identity_get == -1:
            if time.time() - self.identity_get_latest > 600.0:
                return self.verify_identity_get()
            return None
        # BitDust node must be already connected to the network
        if self.mw().state_network_connected == 0:
            return None
            # return self.verify_network_connected()
        if self.mw().state_network_connected == -1:
            if time.time() - self.network_connected_latest > 30.0 and not self.connecting:
                return self.verify_network_connected()
            return None
        # all is good
        return True

    #------------------------------------------------------------------------------

    def verify_process_health(self, *args, **kwargs):
        self.mw().state_process_health = 0
        return api_client.process_health(cb=self.on_process_health_result)

    def verify_identity_get(self, *args, **kwargs):
        self.mw().state_identity_get = 0
        return api_client.identity_get(cb=self.on_identity_get_result)

    def verify_network_connected(self, *args, **kwargs):
        dt = 0
        if self.network_connected_latest:
            dt = time.time() - self.network_connected_latest
        if self.connecting:
            self.mw().state_network_connected = 0
            if _Debug:
                print('Controller.verify_network_connected skipped, already connecting', dt, time.asctime())
            return False
        if _Debug:
            print('Controller.verify_network_connected', dt, time.asctime())
        self.mw().state_network_connected = 0
        self.connecting = True
        return api_client.network_connected(cb=self.on_network_connected_result)

    #------------------------------------------------------------------------------

    def add_callback(self, target, cb, cb_id=None):
        if target not in self.callbacks:
            self.callbacks[target] = []
        self.callbacks[target].append((cb, cb_id, ))

    def remove_callback(self, target, cb=None, cb_id=None):
        if target not in self.callbacks:
            return False
        for pos in range(len(self.callbacks[target])):
            cur_cb, cur_cb_id = self.callbacks[target][pos]
            if cb is not None and cur_cb == cb:
                self.callbacks[target].pop(pos)
                return True
            if cb_id is not None and cur_cb_id == cb_id:
                self.callbacks[target].pop(pos)
                return True
        return False

    #------------------------------------------------------------------------------

    def add_state_changed_callback(self, automat_index, cb, cb_id=None):
        if automat_index not in self.state_changed_callbacks:
            self.state_changed_callbacks[automat_index] = []
        self.state_changed_callbacks[automat_index].append((cb, cb_id, ))

    def remove_state_changed_callback(self, automat_index, cb=None, cb_id=None):
        if automat_index not in self.state_changed_callbacks:
            return False
        for pos in range(len(self.state_changed_callbacks[automat_index])):
            cur_cb, cur_cb_id = self.state_changed_callbacks[automat_index][pos]
            if cb is not None and cur_cb == cb:
                self.state_changed_callbacks[automat_index].pop(pos)
                return True
            if cb_id is not None and cur_cb_id == cb_id:
                self.state_changed_callbacks[automat_index].pop(pos)
                return True
        return False

    def add_state_changed_callback_by_id(self, automat_id, cb, cb_id=None):
        if automat_id not in self.state_changed_callbacks_by_id:
            self.state_changed_callbacks_by_id[automat_id] = []
        self.state_changed_callbacks_by_id[automat_id].append((cb, cb_id, ))

    def remove_state_changed_callback_by_id(self, automat_id, cb=None, cb_id=None):
        if automat_id not in self.state_changed_callbacks_by_id:
            return False
        for pos in range(len(self.state_changed_callbacks_by_id[automat_id])):
            cur_cb, cur_cb_id = self.state_changed_callbacks_by_id[automat_id][pos]
            if cb is not None and cur_cb == cb:
                self.state_changed_callbacks_by_id[automat_id].pop(pos)
                return True
            if cb_id is not None and cur_cb_id == cb_id:
                self.state_changed_callbacks_by_id[automat_id].pop(pos)
                return True
        return False

    #------------------------------------------------------------------------------

    def on_process_health_result(self, resp):
        if _Debug:
            print('Controller.on_process_health_result %r' % resp)
        if not api_client.is_ok(resp):
            self.process_health_latest = 0
            self.process_health_errors += 1
            if api_client.is_exception(resp, 'web socket is closed'):
                self.mw().state_process_health = 0
            else:
                self.mw().state_process_health = -1
            return
        self.process_health_latest = time.time() if api_client.is_ok(resp) else 0
        self.mw().state_process_health = 1 if api_client.is_ok(resp) else -1
        if self.mw().state_process_health == 1:
            self.process_health_errors = 0
        self.run()

    def on_identity_get_result(self, resp):
        if _Debug:
            print('Controller.on_identity_get_result', api_client.is_ok(resp))
        self.identity_get_latest = time.time()
        if not api_client.is_ok(resp):
            self.identity_get_latest = 0
            if api_client.response_errors(resp).count('local identity is not valid or not exist'):
                self.mw().state_identity_get = 0
            else:
                self.mw().state_identity_get = -1
            return
        self.identity_get_latest = time.time()
        self.mw().state_identity_get = 1 if api_client.is_ok(resp) else -1
        self.run()

    def on_network_connected_result(self, resp):
        if _Debug:
            print('Controller.on_network_connected_result', time.asctime(), resp)
        self.connecting = False
        self.network_connected_latest = time.time()
        if not api_client.is_ok(resp):
            self.network_connected_latest = 0
            if api_client.response_errors(resp).count('local identity is not valid or not exist'):
                self.mw().state_network_connected = 0
            if api_client.response_errors(resp).count('disconnected'):
                self.mw().state_network_connected = 0
                Clock.schedule_once(lambda x: self.verify_network_connected(), 5.0)
            else:
                self.mw().state_network_connected = -1
            return
        self.network_connected_latest = time.time()
        self.mw().state_network_connected = 1
        self.run()

    def on_websocket_open(self, websocket_instance):
        if _Debug:
            print('Controller.on_websocket_open', websocket_instance)
        if self.mw().state_process_health != 1:
            self.process_health_latest = 0
            self.identity_get_latest = 0
            self.network_connected_latest = 0
            self.verify_process_health()
        api_client.start_model_streaming('service', request_all=True)
        api_client.start_model_streaming('key', request_all=True)
        api_client.start_model_streaming('conversation', request_all=True)
        api_client.start_model_streaming('message', request_all=True)
        api_client.start_model_streaming('correspondent', request_all=True)
        api_client.start_model_streaming('online_status', request_all=True)
        api_client.start_model_streaming('private_file', request_all=True)
        api_client.start_model_streaming('shared_file', request_all=True)
        api_client.start_model_streaming('remote_version', request_all=True)

    def on_websocket_error(self, websocket_instance, error):
        if _Debug:
            print('Controller.on_websocket_error', self.process_health_errors, error)
        if self.mw().state_process_health != -1:
            self.process_health_latest = 0
            self.identity_get_latest = 0
            self.network_connected_latest = 0
            if self.mw().engine_is_on:
                self.mw().state_process_health = 0
            else:
                self.mw().state_process_health = -1
        # if self.process_health_errors >= 3:
        #     self.mw().engine_is_on = False
        # else:
        Clock.schedule_once(lambda x: self.verify_process_health(), 1.0)

    def on_websocket_event(self, json_data):
        if _Debug:
            print('Controller.on_websocket_event', json_data)
        event_id = json_data.get('payload', {}).get('event_id', '')
        event_data = json_data.get('payload', {}).get('data', {})
        if not event_id:
            return
        if event_id in ['service-started', 'service-stopped', ]:
            if self.mw().is_screen_active('settings_screen'):
                self.mw().get_active_screen('settings_screen').on_service_started_stopped(
                    event_id=event_id,
                    service_name=event_data.get('name', ''),
                )
        elif event_id == 'state-changed':
            automat_index = event_data.get('index')
            automat_id = event_data.get('id')
            if automat_index is not None and automat_index in self.state_changed_callbacks:
                for cb_info in self.state_changed_callbacks[automat_index]:
                    cb_info[0](event_data)
            if automat_id is not None and automat_id in self.state_changed_callbacks_by_id:
                for cb_info in self.state_changed_callbacks_by_id[automat_id]:
                    cb_info[0](event_data)
            # if event_data.get('name', '') in ['GroupMember', 'OnlineStatus', ]:
            #     if self.mw().is_screen_active('conversations_screen'):
            #         self.mw().get_active_screen('conversations_screen').on_state_changed(event_data)
            #     elif self.mw().is_screen_active('friends_screen'):
            #         self.mw().get_active_screen('friends_screen').on_state_changed(event_data)
        elif event_id in ['group-synchronized', 'group-connecting', 'group-disconnected', ]:
            if self.mw().is_screen_active('conversations_screen'):
                self.mw().get_active_screen('conversations_screen').on_group_state_changed(
                    event_id=event_id,
                    group_key_id=event_data.get('group_key_id', ''),
                    old_state=event_data.get('old_state', ''),
                    new_state=event_data.get('new_state', ''),
                )
        # elif event_id in ['friend-connected', 'friend-disconnected', ]:
            # if self.mw().is_screen_active('friends_screen'):
            #     self.mw().get_active_screen('friends_screen').on_friend_state_changed(
            #         event_id=event_id,
            #         idurl=event_data.get('idurl', ''),
            #         global_id=event_data.get('global_id', ''),
            #         old_state=event_data.get('old_state', ''),
            #         new_state=event_data.get('new_state', ''),
            #     )
            # if self.mw().is_screen_active('conversations_screen'):
            #     self.mw().get_active_screen('conversations_screen').on_friend_state_changed(
            #         event_id=event_id,
            #         idurl=event_data.get('idurl', ''),
            #         global_id=event_data.get('global_id', ''),
            #         old_state=event_data.get('old_state', ''),
            #         new_state=event_data.get('new_state', ''),
            #     )

    def on_websocket_stream_message(self, json_data):
        if _Debug:
            print('Controller.on_websocket_stream_message', json_data)
        msg_type = json_data.get('payload', {}).get('payload', {}).get('msg_type', '')
        if msg_type == 'private_message':
            self.on_private_message_received(json_data)
            return
        if msg_type == 'group_message':
            self.on_group_message_received(json_data)
            return

    def on_private_message_received(self, json_data):
        if _Debug:
            print('Controller.on_private_message_received', json_data)
        cb_list = self.callbacks.get('on_private_message_received', [])
        for cb, _ in cb_list:
            cb(json_data)

    def on_group_message_received(self, json_data):
        if _Debug:
            print('Controller.on_group_message_received', json_data)
        cb_list = self.callbacks.get('on_group_message_received', [])
        for cb, _ in cb_list:
            cb(json_data)

    def on_model_update(self, json_data):
        model_name = json_data['payload']['name']
        snap_id = json_data['payload']['id']
        d = json_data['payload']['data']
        if model_name not in self.model_data:
            self.model_data[model_name] = {}
        deleted = json_data['payload'].get('deleted')
        if _Debug:
            print('Controller.on_model_update [%s] %s deleted=%r\n    %r' % (model_name, snap_id, deleted, d, ))
        if deleted:
            self.model_data[model_name].pop(snap_id)
            if model_name == 'private_file':
                _, _, path = d['remote_path'].rpartition(':')
                self.private_files_index.pop(path, None)
            elif model_name == 'shared_file':
                self.shared_files_index.pop(d['remote_path'], None)
            elif model_name == 'remote_version':
                self.remote_versions_index.pop(d['global_id'], None)
                self.remote_files_details.pop(d['global_id'], None)
        else:
            if snap_id not in self.model_data[model_name]:
                self.model_data[model_name][snap_id] = {}
            self.model_data[model_name][snap_id]['id'] = snap_id
            self.model_data[model_name][snap_id]['data'] = d
            self.model_data[model_name][snap_id]['created'] = json_data['payload']['created']
            if model_name == 'service':
                def _st(d):
                    return 1 if d['state'] == 'ON' else (
                        -1 if d['state'] in ['OFF', 'NOT_INSTALLED', 'DEPENDS_OFF', 'CLOSED', ] else 0)
                if snap_id == 'service_my_data':
                    self.mw().state_my_data = _st(d)
                elif snap_id == 'service_message_history':
                    self.mw().state_message_history = _st(d)
                elif snap_id == 'service_entangled_dht':
                    self.mw().state_entangled_dht = _st(d)
                elif snap_id == 'service_proxy_transport':
                    self.mw().state_proxy_transport = _st(d)
            elif model_name == 'private_file':
                _, _, path = d['remote_path'].rpartition(':')
                self.private_files_index[path] = d['global_id']
            elif model_name == 'shared_file':
                self.shared_files_index[d['remote_path']] = d['global_id']
            elif model_name == 'remote_version':
                global_id = d['global_id']
                _, _, version_id = d['backup_id'].rpartition('/')
                if global_id not in self.remote_versions_index:
                    self.remote_versions_index[global_id] = {}
                self.remote_versions_index[global_id][version_id] = snap_id
                sz = 0
                delivered = 0.0
                reliable = 0.0
                total_file_versions = 0
                for one_snap_id in self.remote_versions_index[global_id].values():
                    version_details = self.model_data['remote_version'].get(one_snap_id)
                    if version_details:
                        sz += version_details['data']['size']
                        delivered += float(version_details['data']['delivered'].replace('%', ''))
                        reliable += float(version_details['data']['reliable'].replace('%', ''))
                        total_file_versions += 1
                if total_file_versions:
                    self.remote_files_details[global_id] = dict(
                        size=sz,
                        delivered=system.percent2string(delivered / total_file_versions),
                        reliable=system.percent2string(reliable / total_file_versions),
                        count=total_file_versions,
                    )
                else:
                    self.remote_files_details.pop(global_id, None)

    def on_state_process_health(self, instance, value):
        if _Debug:
            print('Controller.on_state_process_health', value)
        if value == -1:
            # if self.mw().selected_screen:
                # if self.mw().selected_screen not in ['process_dead_screen', 'connecting_screen', 'welcome_screen', ]:
                #     self.mw().latest_screen = self.mw().selected_screen
            self.mw().state_identity_get = -1
            self.mw().state_network_connected = -1
            self.mw().state_entangled_dht = -1
            self.mw().state_proxy_transport = -1
            self.mw().state_my_data = -1
            self.mw().state_message_history = -1
            self.mw().update_menu_items()
            self.model_data.clear()
            self.mw().latest_screen = 'welcome_screen'
            # self.mw().select_screen('engine_status_screen')
            # self.mw().close_active_screens(exclude_screens=['engine_status_screen', ])
            return
        if value == 1:
            self.mw().update_menu_items()
            self.on_state_success()
            return
        if value == 0:
            self.mw().state_identity_get = -1
            self.mw().state_network_connected = -1
            self.run()
            return
        raise Exception('unexpected process_health state: %r' % value)

    def on_state_identity_get(self, instance, value):
        if _Debug:
            print('Controller.on_state_identity_get', value)
        if self.mw().state_process_health != 1:
            return
        if value == -1:
            # if self.mw().selected_screen:
                # if self.mw().selected_screen not in ['process_dead_screen', 'connecting_screen', 'welcome_screen', 'startup_screen', ]:
                #     self.mw().latest_screen = self.mw().selected_screen
            self.mw().state_network_connected = -1
            self.mw().update_menu_items()
            self.mw().latest_screen = 'welcome_screen'
            # self.mw().select_screen('new_identity_screen')
            # self.mw().close_screens(['engine_status_screen', 'connecting_screen', 'startup_screen', ])
            return
        if value == 1:
            self.mw().update_menu_items()
            self.on_state_success()
            return
        if value == 0:
            self.mw().state_network_connected = -1
            self.run()
            return
        raise Exception('unexpected identity_get state: %r' % value)

    def on_state_network_connected(self, instance, value):
        if _Debug:
            print('Controller.on_state_network_connected', value)
        if value == -1:
            self.mw().state_entangled_dht = -1
            self.mw().state_proxy_transport = -1
            self.mw().state_my_data = -1
            self.mw().state_message_history = -1
        if self.mw().state_process_health != 1:
            return
        if self.mw().state_identity_get != 1:
            return
        if value == -1:
            # if self.mw().selected_screen:
            #     if self.mw().selected_screen not in ['engine_status_screen', 'connecting_screen', 'welcome_screen', 'startup_screen', ]:
            #         self.mw().latest_screen = self.mw().selected_screen
            self.mw().update_menu_items()
            self.mw().latest_screen = 'welcome_screen'
            # if self.mw().selected_screen != 'welcome_screen':
            #     self.mw().select_screen('connecting_screen')
            # self.mw().close_screens(['engine_status_screen', 'new_identity_screen', 'recover_identity_screen', 'startup_screen', ])
            return
        if value == 1:
            self.mw().update_menu_items()
            self.on_state_success()
            return
        if value == 0:
            self.run()
            return
        raise Exception('unexpected network_connected state: %r' % value)

    def on_state_success(self):
        if _Debug:
            print('Controller.on_state_success %r %r %r, latest_screen=%r selected_screen=%r' % (
                self.mw().state_process_health, self.mw().state_identity_get, self.mw().state_network_connected,
                self.mw().latest_screen, self.mw().selected_screen, ))
        # self.mw().update_menu_items()
        # if self.mw().state_process_health == 1 and self.mw().state_identity_get == 1 and self.mw().state_network_connected == 1:
            # if self.mw().latest_screen in ['engine_status_screen', 'connecting_screen', 'new_identity_screen', 'recover_identity_screen', 'startup_screen', ]:
            #     self.mw().latest_screen = 'welcome_screen'
            # if self.mw().selected_screen != 'welcome_screen':
            #     if self.mw().selected_screen == 'connecting_screen':
            #         self.mw().get_active_screen('connecting_screen').on_state_verify_success(self.mw().latest_screen or 'welcome_screen')
            #     else:
            #         self.mw().select_screen(self.mw().latest_screen or 'welcome_screen')
            # self.mw().close_screens(['engine_status_screen', 'new_identity_screen', 'recover_identity_screen', 'startup_screen', ])
            # return
        # if self.mw().state_process_health == 1 and self.mw().state_identity_get == 1 and self.mw().state_network_connected in [-1, 0, ]:
            # if self.mw().selected_screen:
            #     if self.mw().selected_screen not in ['process_dead_screen', 'connecting_screen', 'welcome_screen', 'startup_screen', ]:
            #         self.mw().latest_screen = self.mw().selected_screen
            # self.mw().latest_screen = 'welcome_screen'
            # if self.mw().selected_screen != 'welcome_screen':
            #     self.mw().select_screen('connecting_screen')
            # self.mw().close_screens(['engine_status_screen', 'new_identity_screen', 'recover_identity_screen', 'startup_screen', ])
            # return
        # if self.mw().state_process_health == 1 and self.mw().state_identity_get == -1:
            # if self.mw().selected_screen:
            #     if self.mw().selected_screen not in ['process_dead_screen', 'connecting_screen', 'welcome_screen', 'startup_screen', ]:
            #         self.mw().latest_screen = self.mw().selected_screen
            # self.mw().latest_screen = 'welcome_screen'
            # self.mw().select_screen('new_identity_screen')
            # self.mw().close_screens(['engine_status_screen', 'connecting_screen', 'recover_identity_screen', 'startup_screen', ])
            # return
        # if self.mw().selected_screen != 'welcome_screen':
        #     self.mw().select_screen('connecting_screen')
        # self.mw().close_screens(['engine_status_screen', 'new_identity_screen', 'recover_identity_screen', 'startup_screen', ])
