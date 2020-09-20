import time

#------------------------------------------------------------------------------

from service import websock

#------------------------------------------------------------------------------

_Debug = True

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
        # BitDust process must be running already
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
        if _Debug:
            print('verify_process_health')
        websock.ws_call(
            json_data={"command": "api_call", "method": "process_health", "kwargs": {}, },
            cb=self.on_process_health_result,
        )

    def on_process_health_result(self, resp):
        self.process_health_latest = time.time()
        if not isinstance(resp, dict):
            self.mw().state_process_health = -1
            return
        self.mw().state_process_health = 1 if websock.is_ok(resp) else -1
        self.run()

    def verify_identity_get(self, *args, **kwargs):
        if _Debug:
            print('verify_identity_get')
        websock.ws_call(
            json_data={"command": "api_call", "method": "identity_get", "kwargs": {}, },
            cb=self.on_identity_get_result,
        )

    def on_identity_get_result(self, resp):
        self.identity_get_latest = time.time()
        if not isinstance(resp, dict):
            self.mw().state_identity_get = -1
            return
        self.mw().state_identity_get = 1 if websock.is_ok(resp) else -1
        self.run()

    def verify_network_connected(self, *args, **kwargs):
        if _Debug:
            print('verify_network_connected')
        websock.ws_call(
            json_data={"command": "api_call", "method": "network_connected", "kwargs": {"wait_timeout": 0, }, },
            cb=self.on_network_connected_result,
        )

    def on_network_connected_result(self, resp):
        self.network_connected_latest = time.time()
        if not isinstance(resp, dict):
            self.mw().state_network_connected = -1
            return
        self.mw().state_network_connected = 1 if websock.is_ok(resp) else -1
        self.run()
