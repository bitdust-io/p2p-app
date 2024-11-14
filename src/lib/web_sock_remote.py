import time
import base64

try:
    import thread
except ImportError:
    import _thread as thread

import queue

#------------------------------------------------------------------------------

from kivy.clock import mainthread

#------------------------------------------------------------------------------

from lib import system
from lib import strng
from lib import jsn
from lib import rsa_key
from lib import cipher
from lib import hashes
from lib import web_socket

#------------------------------------------------------------------------------

_Debug = True
_DebugAPIResponses = _Debug

#------------------------------------------------------------------------------

_ClientInfoFilePath = None
_WebSocketApp = None
_WebSocketQueue = None
_WebSocketReady = False
_WebSocketClosed = True
_WebSocketStarted = False
_WebSocketConnecting = False
_LastCallID = 0
_PendingCalls = []
_CallbacksQueue = {}
_RegisteredCallbacks = {}
_ModelUpdateCallbacks = {}

#------------------------------------------------------------------------------

def start(callbacks={}, client_info_filepath=None):
    global _ClientInfoFilePath
    global _WebSocketStarted
    global _WebSocketConnecting
    global _WebSocketQueue
    global _RegisteredCallbacks
    if is_started():
        raise Exception('already started')
    if _Debug:
        print('web_sock_remote.start() client_info_filepath=%r' % client_info_filepath)
    _ClientInfoFilePath = client_info_filepath
    _RegisteredCallbacks = callbacks or {}
    _WebSocketConnecting = True
    _WebSocketStarted = True
    _WebSocketQueue = queue.Queue(maxsize=1000)
    thread.start_new_thread(websocket_thread, ())
    thread.start_new_thread(requests_thread, (_WebSocketQueue, ))


def stop():
    global _ClientInfoFilePath
    global _WebSocketStarted
    global _WebSocketQueue
    global _WebSocketConnecting
    global _WebSocketReady
    global _RegisteredCallbacks
    if not is_started():
        raise Exception('has not been started')
    if _Debug:
        print('web_sock_remote.stop()')
    _ClientInfoFilePath = None
    _RegisteredCallbacks = {}
    _WebSocketStarted = False
    _WebSocketConnecting = False
    _WebSocketReady = False
    while True:
        try:
            json_data, _ = ws_queue().get_nowait()
            print('cleaned unfinished call', json_data)
        except queue.Empty:
            break
    _WebSocketQueue.put_nowait((None, None, ))
    if ws():
        if _Debug:
            print('websocket already closed')
        ws().close()

#------------------------------------------------------------------------------

def ws():
    global _WebSocketApp
    return _WebSocketApp


def ws_queue():
    global _WebSocketQueue
    return _WebSocketQueue


def is_ready():
    global _WebSocketReady
    return _WebSocketReady


def is_closed():
    global _WebSocketClosed
    return _WebSocketClosed


def is_started():
    global _WebSocketStarted
    return _WebSocketStarted


def is_connecting():
    global _WebSocketConnecting
    return _WebSocketConnecting


def registered_callbacks():
    global _RegisteredCallbacks
    return _RegisteredCallbacks


def model_update_callbacks():
    global _ModelUpdateCallbacks
    return _ModelUpdateCallbacks

#------------------------------------------------------------------------------

@mainthread
def on_open(ws_inst):
    global _ClientInfoFilePath
    global _WebSocketReady
    global _WebSocketClosed
    global _WebSocketConnecting
    _WebSocketReady = True
    _WebSocketClosed = False
    _WebSocketConnecting = False
    cb = registered_callbacks().get('on_open')
    if cb:
        cb(ws_inst)
    client_info = jsn.loads(system.ReadTextFile(_ClientInfoFilePath) or '{}')
    if _Debug:
        print('websocket opened', time.time())
    auth_token = client_info.get('auth_token')
    if auth_token:
        on_connect(ws_inst)
        return
    restart_handshake()


@mainthread
def on_connect(ws_inst):
    global _PendingCalls
    if _Debug:
        print('websocket connected', time.time(), len(_PendingCalls))
    cb = registered_callbacks().get('on_connect')
    if cb:
        cb(ws_inst)
    while _PendingCalls:
        json_data, cb = _PendingCalls.pop(0)
        try:
            ws_queue().put_nowait((json_data, cb, ))
        except Exception as exc:
            if _Debug:
                print('websocket was not opened', exc)
            _PendingCalls.insert(0, (json_data, cb, ))
            on_error(ws_inst, exc)
            return


@mainthread
def on_close(ws_inst):
    global _WebSocketReady
    global _WebSocketClosed
    global _WebSocketConnecting
    _WebSocketReady = False
    _WebSocketClosed = True
    _WebSocketConnecting = False
    if _Debug:
        print('websocket closed', time.time())
    cb = registered_callbacks().get('on_close')
    if cb:
        cb(ws_inst)


@mainthread
def on_message(ws_inst, message):
    global _CallbacksQueue
    global _ClientInfoFilePath
    json_data = jsn.loads(message)
    if _Debug:
        print('web_sock_remote.on_message %d bytes: %r' % (len(message), json_data))
    cmd = json_data.get('cmd')
    if cmd == 'server_public_key':
        # SECURITY
        # TODO: think about verifying if that is a malicious request that is intended to interrupt already connected "good guy"
        # add more strict verification of the all input fields
        try:
            server_public_key = json_data['server_public_key']
            confirmation_code = json_data.get('confirm')
            signature = json_data.get('signature')
            server_key_object = rsa_key.RSAKey()
            server_key_object.fromString(server_public_key)
            hashed_confirmation = hashes.sha1(strng.to_bin(server_public_key+'-'+confirmation_code))
        except Exception as e:
            if _Debug:
                print('failed reading server_public_key', e)
            restart_handshake()
            return False
        if not server_key_object.verify(strng.to_bin(signature), hashed_confirmation):
            if _Debug:
                print('web_sock_remote.on_message server public key response signature verification failed')
            restart_handshake()
            return False
        client_info = jsn.loads(system.ReadTextFile(_ClientInfoFilePath) or '{}')
        client_info['server_public_key'] = server_public_key
        client_info['state'] = 'input_server_code'
        system.WriteTextFile(_ClientInfoFilePath, jsn.dumps(client_info, indent=2))
        cb = registered_callbacks().get('on_handshake_started')
        if cb:
            cb()
        # here, the app needs to ask from the user for an input (by hand) of the server digit code
        # must raise an event to the UI and show a text input field widget
        # or code needs to be entered in the terminal via stdin
        # after user entered the server digit code next WS message will be sent with "cmd": "server-code"
        return True
    if cmd == 'client-code':
        try:
            encrypted_payload = json_data['auth']
            signature = json_data['signature']
            orig_encrypted_payload = base64.b64decode(strng.to_bin(encrypted_payload))
            client_info = jsn.loads(system.ReadTextFile(_ClientInfoFilePath) or '{}')
            client_code = client_info['client_code']
            client_key_object = rsa_key.RSAKey()
            client_key_object.fromDict(client_info['key'])
            server_key_object = rsa_key.RSAKey()
            server_key_object.fromString(client_info['server_public_key'])
            received_salted_payload = strng.to_text(client_key_object.decrypt(orig_encrypted_payload))
            hashed_payload = hashes.sha1(strng.to_bin(received_salted_payload))
            json_payload = jsn.loads(received_salted_payload)
            received_client_code = json_payload['client_code']
            auth_token = json_payload['auth_token']
            session_key = json_payload['session_key']
        except Exception as e:
            if _Debug:
                print('failed reading server_public_key', e)
            restart_handshake()
            return False
        if not server_key_object.verify(strng.to_bin(signature), hashed_payload):
            if _Debug:
                print('web_sock_remote.on_message authorization response signature verification failed')
            restart_handshake()
            return False
        if received_client_code != client_code:
            if _Debug:
                print('web_sock_remote.on_message client code is not matching')
            restart_handshake()
            return False
        client_info['auth_token'] = auth_token
        client_info['session_key'] = session_key
        system.WriteTextFile(_ClientInfoFilePath, jsn.dumps(client_info, indent=2))
        if _Debug:
            print('AUTHORIZED!!!')
        return True
    if 'payload' not in json_data:
        if _Debug:
            print('web_sock_remote.on_message no payload found in the response')
        return False
    payload_type = json_data.get('type')
    if payload_type == 'event':
        return on_event(json_data)
    if payload_type == 'stream_message':
        return on_stream_message(json_data)
    if payload_type == 'model':
        return on_model_update(json_data)
    if payload_type == 'api_call':
        if 'call_id' not in json_data['payload']:
            if _Debug:
                print('        call_id not found in the response')
            return False
        call_id = json_data['payload']['call_id']
        if call_id not in _CallbacksQueue:
            if _Debug:
                print('        call_id found in the response, but no callbacks registered')
            return False
        result_callback = _CallbacksQueue.pop(call_id)
        if _DebugAPIResponses:
            if json_data['payload'].get('response'):
                print('WS API Response {} : {}'.format(call_id, json_data['payload']['response'], ))
        if result_callback:
            result_callback(json_data)
        return True
    if _Debug:
        print('        unexpected payload_type', json_data)
    raise Exception(payload_type)


@mainthread
def on_error(ws_inst, error):
    if _Debug:
        print('on_error', error)
    cb = registered_callbacks().get('on_error')
    if cb:
        cb(ws_inst, error)


@mainthread
def on_fail(err, result_callback=None):
    if _Debug:
        print('on_fail', err)
    if result_callback:
        result_callback(err)

#------------------------------------------------------------------------------

def on_event(json_data):
    if _Debug:
        print('WS EVENT:', json_data['payload']['event_id'])
    cb = registered_callbacks().get('on_event')
    if cb:
        cb(json_data)
    return True


def on_stream_message(json_data):
    if _Debug:
        print('WS STREAM MSG:', json_data['payload']['payload']['message_id'])
    cb = registered_callbacks().get('on_stream_message')
    if cb:
        cb(json_data)
    return True


def on_model_update(json_data):
    if _Debug:
        print('WS MODEL:', json_data['payload']['name'], json_data['payload']['id'])
    cb = registered_callbacks().get('on_model_update')
    if cb:
        cb(json_data)
    model_cb_list = model_update_callbacks().get(json_data['payload']['name']) or []
    if model_cb_list:
        for model_cb in model_cb_list:
            if model_cb:
                model_cb(json_data['payload'])
    return True

#------------------------------------------------------------------------------

def restart_handshake():
    global _ClientInfoFilePath
    client_info = jsn.loads(system.ReadTextFile(_ClientInfoFilePath) or '{}')
    if _Debug:
        print('about to generate new RSA key')
    key_object = rsa_key.RSAKey()
    key_object.generate(4096)
    client_info['key'] = key_object.toDict(include_private=True)
    client_info['state'] = 'init'
    system.WriteTextFile(_ClientInfoFilePath, jsn.dumps(client_info, indent=2))
    json_data = {
        'cmd': 'client-public-key',
        'client_public_key': key_object.toPublicString(),
    }
    ws_queue().put_nowait((json_data, None, ))


def continue_handshake(server_code):
    global _ClientInfoFilePath
    client_info = jsn.loads(system.ReadTextFile(_ClientInfoFilePath) or '{}')
    salted_server_code = server_code + '-' + cipher.generate_secret_text(90)
    server_key_object = rsa_key.RSAKey()
    server_key_object.fromString(client_info['server_public_key'])
    encrypted_server_code = base64.b64encode(server_key_object.encrypt(strng.to_bin(salted_server_code)))
    hashed_server_code = hashes.sha1(strng.to_bin(salted_server_code))
    client_key_object = rsa_key.RSAKey()
    client_key_object.fromDict(client_info['key'])
    client_info['client_code'] = cipher.generate_digits(6, as_text=True)
    system.WriteTextFile(_ClientInfoFilePath, jsn.dumps(client_info, indent=2))
    # TODO: here must show the client_code digits in the app UI
    # user will have to enter the displayed client code on the server manually
    json_data = {
        'cmd': 'server-code',
        'server_code': strng.to_text(encrypted_server_code),
        'signature': strng.to_text(client_key_object.sign(hashed_server_code)),
    }
    ws_queue().put_nowait((json_data, None, ))
    if _Debug:
        print('continue_handshake client code: %r' % client_info['client_code'])

#------------------------------------------------------------------------------

def requests_thread(active_queue):
    global _LastCallID
    global _CallbacksQueue
    if _Debug:
        print('starting requests_thread()')
    while True:
        if not is_started():
            if _Debug:
                print('finishing requests_thread() because web socket is not started')
            break
        json_data, result_callback = active_queue.get()
        if json_data is None:
            if _Debug:
                print('going to stop requests thread')
            break
        if 'call_id' not in json_data:
            _LastCallID += 1
            json_data['call_id'] = _LastCallID
        else:
            _LastCallID = json_data['call_id']
        call_id = json_data['call_id']
        if call_id in _CallbacksQueue:
            on_fail(Exception('call_id was not unique'), result_callback)
            continue
        if not ws():
            on_fail(Exception('websocket is closed'), result_callback)
            continue
        _CallbacksQueue[call_id] = result_callback
        data = jsn.dumps(json_data)
        if _Debug:
            print('sending', data)
        ws().send(data)
    if _Debug:
        print('requests_thread() finished')


def websocket_thread():
    global _ClientInfoFilePath
    global _WebSocketApp
    global _WebSocketClosed
    web_socket.enableTrace(False)
    if _Debug:
        print('websocket_thread() beginning _ClientInfoFilePath=%r' % _ClientInfoFilePath)
    while is_started():
        if _Debug:
            print('websocket_thread() calling run_forever(ping_interval=10) %r' % time.asctime())
        _WebSocketClosed = False
        client_info = jsn.loads(system.ReadTextFile(_ClientInfoFilePath) or '{}')
        _WebSocketApp = web_socket.WebSocketApp(
            url=client_info['url'],
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open,
        )
        try:
            ret = ws().run_forever(ping_interval=10)
        except Exception as exc:
            ret = None
            _WebSocketApp = None
            if _Debug:
                print('websocket_thread(): %r' % exc)
            time.sleep(1)
        if _Debug:
            print('websocket_thread().run_forever() returned: %r  is_started: %r' % (ret, is_started(), ))
        if _WebSocketApp:
            del _WebSocketApp
            _WebSocketApp = None
        if not is_started():
            break
        time.sleep(1)
    _WebSocketApp = None
    if _Debug:
        print('websocket_thread() finished')

#------------------------------------------------------------------------------

def verify_state():
    global _WebSocketReady
    global _WebSocketConnecting
    if is_closed():
        _WebSocketReady = False
        if _Debug:
            print('WS CALL REFUSED, web socket already closed')
        if is_connecting():
            if _Debug:
                print('web socket closed but still connecting')
            return 'closed'
        return 'closed'
    if is_ready():
        return 'ready'
    if is_connecting():
        return 'connecting'
    if is_started():
        return 'connecting'
    return 'not-started'


def ws_call(json_data, cb=None):
    global _PendingCalls
    st = verify_state()
    if _Debug:
        print('ws_call', st)
    if st == 'ready':
        ws_queue().put_nowait((json_data, cb, ))
        return True
    if st == 'closed':
        if cb:
            cb(Exception('web socket is closed'))
        return False
    if st == 'connecting':
        if _Debug:
            print('web socket still connecting, remember pending request')
        _PendingCalls.append((json_data, cb, ))
        return True
    if st == 'not-started':
        if _Debug:
            print('web socket was not started')
        if cb:
            cb(Exception('web socket was not started'))
        return False
    raise Exception('unexpected state %r' % st)

#------------------------------------------------------------------------------

if __name__ == '__main__':
    from kivy.app import App

    class TestApp(App):

        def _on_websocket_open(self, ws_inst):
            print('TestApp._on_websocket_open', ws_inst)
    
        def _on_websocket_connect(self, ws_inst):
            print('TestApp._on_websocket_connect', ws_inst)
            ws_queue().put_nowait(({'first': 'message'}, None, ))

        def _on_websocket_handshake_started(self):
            print('TestApp._on_websocket_handshake_started')
            entered_server_code = input().strip()
            continue_handshake(entered_server_code)

        def _on_websocket_handshake_failed(self, ws_inst, err):
            print('TestApp._on_websocket_handshake_failed', ws_inst, err)
    
        def _on_websocket_error(self, ws_inst, error):
            print('TestApp._on_websocket_error', ws_inst, error)
    
        def _on_websocket_stream_message(self, json_data):
            print('TestApp._on_websocket_stream_message', json_data)
    
        def _on_websocket_event(self, json_data):
            print('TestApp._on_websocket_event', json_data)
    
        def _on_websocket_model_update(self, json_data):
            print('TestApp._on_websocket_model_update', json_data)

        def build(self):
            start(
                callbacks={
                    'on_open': self._on_websocket_open,
                    'on_handshake_failed': self._on_websocket_handshake_failed,
                    'on_connect': self._on_websocket_connect,
                    'on_error': self._on_websocket_error,
                    'on_stream_message': self._on_websocket_stream_message,
                    'on_event': self._on_websocket_event,
                    'on_model_update': self._on_websocket_model_update,
                    'on_handshake_started': self._on_websocket_handshake_started,
                },
                client_info_filepath='client.json',
            )
            return super().build()

    TestApp().run()
