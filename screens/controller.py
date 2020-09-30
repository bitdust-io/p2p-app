import time

#------------------------------------------------------------------------------

from service import websock
from service import api_client

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

def all_screens():
    from screens import screen_main_menu
    from screens import screen_welcome
    from screens import screen_process_dead
    from screens import screen_new_identity
    from screens import screen_recover_identity
    from screens import screen_connecting
    from screens import screen_my_id
    from screens import screen_search_people
    from screens import screen_friends
    from screens import screen_private_chat
    return {
        'process_dead_screen': screen_process_dead.ProcessDeadScreen,
        'main_menu_screen': screen_main_menu.MainMenuScreen,
        'connecting_screen': screen_connecting.ConnectingScreen,
        'welcome_screen': screen_welcome.WelcomeScreen,
        'new_identity_screen': screen_new_identity.NewIdentityScreen,
        'recover_identity_screen': screen_recover_identity.RecoverIdentityScreen,
        'my_id_screen': screen_my_id.MyIDScreen,
        'search_people_screen': screen_search_people.SearchPeopleScreen,
        'friends_screen': screen_friends.FriendsScreen,
        'private_chat_screen': screen_private_chat.PrivateChatScreen,
    }

#------------------------------------------------------------------------------

class Controller(object):

    process_health_latest = 0
    identity_get_latest = 0
    network_connected_latest = 0

    def __init__(self, app):
        self.app = app

    def mw(self):
        return self.app.main_window

    def start(self):
        websock.start()
        self.run()

    def stop(self):
        websock.stop()

    def run(self):
        if _Debug:
            print('control.run')
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

    #------------------------------------------------------------------------------

    def verify_process_health(self, *args, **kwargs):
        return api_client.process_health(cb=self.on_process_health_result)

    def on_process_health_result(self, resp):
        if _Debug:
            print('on_process_health_result %r' % resp)
        self.process_health_latest = time.time()
        if not isinstance(resp, dict):
            self.mw().state_process_health = -1
            return
        self.mw().state_process_health = 1 if websock.is_ok(resp) else -1
        self.run()

    def verify_identity_get(self, *args, **kwargs):
        return api_client.identity_get(cb=self.on_identity_get_result)

    def on_identity_get_result(self, resp):
        self.identity_get_latest = time.time()
        if not isinstance(resp, dict):
            self.mw().state_identity_get = -1
            return
        self.mw().state_identity_get = 1 if websock.is_ok(resp) else -1
        self.run()

    def verify_network_connected(self, *args, **kwargs):
        return api_client.network_connected(cb=self.on_network_connected_result)

    def on_network_connected_result(self, resp):
        self.network_connected_latest = time.time()
        if not isinstance(resp, dict):
            self.mw().state_network_connected = -1
            return
        self.mw().state_network_connected = 1 if websock.is_ok(resp) else -1
        self.run()
