import time

#------------------------------------------------------------------------------

from lib import websock
from lib import api_client

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

def all_screens():
    return {
        'startup_screen': (
            'screens/screen_startup.kv', 'screens.screen_startup', 'StartUpScreen', ),
        'process_dead_screen': (
            'screens/screen_process_dead.kv', 'screens.screen_process_dead', 'ProcessDeadScreen', ),
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
    }

#------------------------------------------------------------------------------

class Controller(object):

    process_health_latest = 0
    identity_get_latest = 0
    network_connected_latest = 0

    def __init__(self, app):
        self.app = app
        self.callbacks = {}
        self.state_changed_callbacks = {}
        self.state_changed_callbacks_by_id = {}

    def mw(self):
        return self.app.main_window

    def start(self):
        websock.start(callbacks={
            'on_open': self.on_websocket_open,
            'on_error': self.on_websocket_error,
            'on_stream_message': self.on_websocket_stream_message,
            'on_event': self.on_websocket_event,
        })
        self.run()

    def stop(self):
        websock.stop()

    def run(self):
        if _Debug:
            print('Controller.run %r %r %r' % (self.mw().state_process_health, self.mw().state_identity_get, self.mw().state_network_connected, ))
        # BitDust node process must be running already
        if self.mw().state_process_health == 0:
            return self.verify_process_health()
        elif self.mw().state_process_health == -1:
            if time.time() - self.process_health_latest > 30.0:
                return self.verify_process_health()
            return None
        # user identity must be already existing
        if self.mw().state_identity_get == 0:
            return self.verify_identity_get()
        elif self.mw().state_identity_get == -1:
            if time.time() - self.identity_get_latest > 600.0:
                return self.verify_identity_get()
            return None
        # BitDust node must be already connected to the network
        if self.mw().state_network_connected == 0:
            return self.verify_network_connected()
        elif self.mw().state_network_connected == -1:
            if time.time() - self.network_connected_latest > 30.0:
                return self.verify_network_connected()
            return None
        # all is good
        return True

    def verify_process_health(self, *args, **kwargs):
        return api_client.process_health(cb=self.on_process_health_result)

    def verify_identity_get(self, *args, **kwargs):
        return api_client.identity_get(cb=self.on_identity_get_result)

    def verify_network_connected(self, *args, **kwargs):
        if _Debug:
            print('Controller.verify_network_connected', time.asctime())
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
        if not isinstance(resp, dict):
            if _Debug:
                print('on_process_health_result %r' % resp)
            self.process_health_latest = 0
            self.mw().state_process_health = -1
            return
        self.mw().state_process_health = 1 if websock.is_ok(resp) else -1
        self.process_health_latest = time.time() if websock.is_ok(resp) else 0
        self.run()

    def on_identity_get_result(self, resp):
        self.identity_get_latest = time.time()
        if not isinstance(resp, dict):
            if _Debug:
                print('on_identity_get_result', resp)
            self.identity_get_latest = 0
            self.mw().state_identity_get = -1
            return
        self.mw().state_identity_get = 1 if websock.is_ok(resp) else -1
        self.identity_get_latest = time.time()
        self.run()

    def on_network_connected_result(self, resp):
        self.network_connected_latest = time.time()
        if not isinstance(resp, dict):
            if _Debug:
                print('on_network_connected_result', resp)
            self.network_connected_latest = 0
            self.mw().state_network_connected = -1
            return
        self.mw().state_network_connected = 1 if websock.is_ok(resp) else -1
        self.network_connected_latest = time.time()
        self.run()

    #------------------------------------------------------------------------------

    def on_websocket_open(self, websocket_instance):
        if _Debug:
            print('Controller.on_websocket_open', websocket_instance)
        if self.mw().state_process_health != 1:
            self.process_health_latest = 0
            self.identity_get_latest = 0
            self.network_connected_latest = 0
            self.verify_process_health()

    def on_websocket_error(self, websocket_instance, error):
        if _Debug:
            print('Controller.on_websocket_error', websocket_instance, error)
        if self.mw().state_process_health != -1:
            self.mw().state_process_health = -1
            self.process_health_latest = 0
            self.identity_get_latest = 0
            self.network_connected_latest = 0
            self.verify_process_health()

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
            if event_data.get('name', '') in ['GroupMember', 'OnlineStatus', ]:
                if self.mw().is_screen_active('conversations_screen'):
                    self.mw().get_active_screen('conversations_screen').on_state_changed(event_data)
                elif self.mw().is_screen_active('friends_screen'):
                    self.mw().get_active_screen('friends_screen').on_state_changed(event_data)
        elif event_id in ['group-synchronized', 'group-connecting', 'group-disconnected', ]:
            if self.mw().is_screen_active('conversations_screen'):
                self.mw().get_active_screen('conversations_screen').on_group_state_changed(
                    event_id=event_id,
                    group_key_id=event_data.get('group_key_id', ''),
                    old_state=event_data.get('old_state', ''),
                    new_state=event_data.get('new_state', ''),
                )
        elif event_id in ['friend-connected', 'friend-disconnected', ]:
            if self.mw().is_screen_active('friends_screen'):
                self.mw().get_active_screen('friends_screen').on_friend_state_changed(
                    event_id=event_id,
                    idurl=event_data.get('idurl', ''),
                    global_id=event_data.get('global_id', ''),
                    old_state=event_data.get('old_state', ''),
                    new_state=event_data.get('new_state', ''),
                )
            if self.mw().is_screen_active('conversations_screen'):
                self.mw().get_active_screen('conversations_screen').on_friend_state_changed(
                    event_id=event_id,
                    idurl=event_data.get('idurl', ''),
                    global_id=event_data.get('global_id', ''),
                    old_state=event_data.get('old_state', ''),
                    new_state=event_data.get('new_state', ''),
                )

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
        cb_list = self.callbacks.get('on_private_message_received', [])
        for cb, _ in cb_list:
            cb(json_data)

    def on_group_message_received(self, json_data):
        cb_list = self.callbacks.get('on_group_message_received', [])
        for cb, _ in cb_list:
            cb(json_data)

    def on_state_process_health(self, instance, value):
        if _Debug:
            print('Controller.on_state_process_health', value)
        if value == -1:
            if self.mw().selected_screen:
                if self.mw().selected_screen not in ['process_dead_screen', 'connecting_screen', 'welcome_screen', ]:
                    self.mw().latest_screen = self.mw().selected_screen
            self.mw().state_identity_get = 0
            self.mw().state_network_connected = 0
            self.mw().select_screen('process_dead_screen')
            self.mw().close_active_screens(exclude_screens=['process_dead_screen', ])
            return
        if value == 1:
            self.on_state_success()
            return
        if value == 0:
            self.run()
            return
        raise Exception('unexpected process_health state: %r' % value)

    def on_state_identity_get(self, instance, value):
        if _Debug:
            print('Controller.on_state_identity_get', value)
        if self.mw().state_process_health != 1:
            return
        if value == -1:
            if self.mw().selected_screen:
                if self.mw().selected_screen not in ['process_dead_screen', 'connecting_screen', 'welcome_screen', 'startup_screen', ]:
                    self.mw().latest_screen = self.mw().selected_screen
            self.mw().state_network_connected = 0
            self.mw().select_screen('new_identity_screen')
            self.mw().close_screens(['process_dead_screen', 'connecting_screen', 'startup_screen', ])
            return
        if value == 1:
            self.on_state_success()
            return
        if value == 0:
            self.run()
            return
        raise Exception('unexpected identity_get state: %r' % value)

    def on_state_network_connected(self, instance, value):
        if _Debug:
            print('Controller.on_state_network_connected', value)
        if self.mw().state_process_health != 1:
            return
        if value == -1:
            if self.mw().selected_screen:
                if self.mw().selected_screen not in ['process_dead_screen', 'connecting_screen', 'welcome_screen', 'startup_screen', ]:
                    self.mw().latest_screen = self.mw().selected_screen
            if self.mw().selected_screen != 'welcome_screen':
                self.mw().select_screen('connecting_screen')
            self.mw().close_screens(['process_dead_screen', 'new_identity_screen', 'recover_identity_screen', 'startup_screen', ])
            return
        if value == 1:
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
        if self.mw().state_process_health == 1 and self.mw().state_identity_get == 1 and self.mw().state_network_connected == 1:
            if self.mw().latest_screen in ['process_dead_screen', 'connecting_screen', 'new_identity_screen', 'recover_identity_screen', 'startup_screen', ]:
                self.mw().latest_screen = 'welcome_screen'
            if self.mw().selected_screen != 'welcome_screen':
                self.mw().select_screen(self.mw().latest_screen or 'welcome_screen')
            self.mw().close_screens(['process_dead_screen', 'connecting_screen', 'new_identity_screen', 'recover_identity_screen', 'startup_screen', ])
            return
        if self.mw().state_process_health == 1 and self.mw().state_identity_get == 1 and self.mw().state_network_connected in [-1, 0, ]:
            if self.mw().selected_screen:
                if self.mw().selected_screen not in ['process_dead_screen', 'connecting_screen', 'welcome_screen', 'startup_screen', ]:
                    self.mw().latest_screen = self.mw().selected_screen
            if self.mw().selected_screen != 'welcome_screen':
                self.mw().select_screen('connecting_screen')
            self.mw().close_screens(['process_dead_screen', 'new_identity_screen', 'recover_identity_screen', 'startup_screen', ])
            return
        if self.mw().state_process_health == 1 and self.mw().state_identity_get == -1:
            if self.mw().selected_screen:
                if self.mw().selected_screen not in ['process_dead_screen', 'connecting_screen', 'welcome_screen', 'startup_screen', ]:
                    self.mw().latest_screen = self.mw().selected_screen
            self.mw().select_screen('new_identity_screen')
            self.mw().close_screens(['process_dead_screen', 'connecting_screen', 'recover_identity_screen', 'startup_screen', ])
            return
        if self.mw().selected_screen != 'welcome_screen':
            self.mw().select_screen('connecting_screen')
        self.mw().close_screens(['process_dead_screen', 'new_identity_screen', 'recover_identity_screen', 'startup_screen', ])
