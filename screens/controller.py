import time

from service import websock


class Controller(object):

    api_call_id = 0

    process_health_latest = None
    identity_get_latest = None
    network_connected_latest = None

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
        if not self.mw().state_process_health or not self.process_health_latest or (time.time() - self.process_health_latest > 30.0):
            self.verify_process_health()
            return None
        if not self.mw().state_identity_get or not self.identity_get_latest or (time.time() - self.identity_get_latest > 600.0):
            self.verify_identity_get()
            return None
        return True

    def verify_process_health(self, *args, **kwargs):
        self.api_call_id += 1
        websock.ws_call(
            json_data={"command": "api_call", "method": "process_health", "kwargs": {}, "call_id": self.api_call_id},
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
        self.api_call_id += 1
        websock.ws_call(
            json_data={"command": "api_call", "method": "identity_get", "kwargs": {}, "call_id": self.api_call_id},
            cb=self.on_identity_get_result,
        )

    def on_identity_get_result(self, resp):
        self.identity_get_latest = time.time()
        if not isinstance(resp, dict):
            self.mw().state_identity_get = -1
            return
        self.mw().state_identity_get = 1 if websock.is_ok(resp) else -1
        self.run()
