import time

from service import websock


class Controller(object):

    process_health_latest = None
    network_connected_latest = None
    identity_get_latest = None

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
            return

    def verify_process_health(self, *args, **kwargs):
        websock.ws_call({"command": "api_call", "method": "process_health", "kwargs": {}, "call_id": 123}, self.on_process_health_result)

    def on_process_health_result(self, resp):
        print('on_process_health_result', resp)
        self.process_health_latest = time.time()
        if not isinstance(resp, dict):
            self.mw().state_process_health = -1
            return
        self.mw().state_process_health = 1 if resp.get('payload', {}).get('response', {}).get('status', '') == 'OK' else -1
