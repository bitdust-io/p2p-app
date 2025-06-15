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

#------------------------------------------------------------------------------

_USE_PYCRYPTODOME = True

if system.is_ios():
    _USE_PYCRYPTODOME = False

#------------------------------------------------------------------------------

from lib import strng
from lib import jsn
from lib import serialization
from lib import web_socket

#------------------------------------------------------------------------------

if _USE_PYCRYPTODOME:
    from lib import rsa_key
    from lib import cipher
    from lib import hashes
else:
    from lib import rsa_key_slow as rsa_key
    from lib import cipher_slow as cipher
    from lib import hashes_slow as hashes

#------------------------------------------------------------------------------

_Debug = False
_DebugAPIResponses = _Debug

#------------------------------------------------------------------------------

_ClientInfoFilePath = None
_WebSocketApp = None
_WebSocketQueue = None
_WebSocketReady = False
_WebSocketClosed = True
_WebSocketStarted = False
_WebSocketConnecting = False
_WebSocketConnectingAttempts = 0
_WebSocketAuthToken = None
_WebSocketSessionKey = None
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
    global _WebSocketAuthToken
    global _WebSocketSessionKey
    global _RegisteredCallbacks
    if is_started():
        raise Exception('already started')
    if _Debug:
        print('web_sock_remote.start client_info_filepath=%r' % client_info_filepath)
    _ClientInfoFilePath = client_info_filepath or 'client.json'
    _RegisteredCallbacks = callbacks or {}
    _WebSocketConnecting = True
    _WebSocketStarted = True
    _WebSocketAuthToken = None
    _WebSocketSessionKey = None
    _WebSocketQueue = queue.Queue(maxsize=1000)
    client_info = jsn.loads(system.ReadTextFile(_ClientInfoFilePath) or '{}')
    auth_token = client_info.get('auth_token')
    session_key_text = client_info.get('session_key')
    if auth_token and session_key_text:
        if _Debug:
            print('web_sock_remote.start was already AUTHORIZED')
        _WebSocketAuthToken = auth_token
        _WebSocketSessionKey = base64.b64decode(strng.to_bin(session_key_text))
    websocket_thread_id = thread.start_new_thread(websocket_thread, ())
    requests_thread_id = thread.start_new_thread(requests_thread, (_WebSocketQueue, ))
    if _Debug:
        print('    websocket_thread_id=%r requests_thread_id=%r' % (websocket_thread_id, requests_thread_id, ))


def stop():
    global _ClientInfoFilePath
    global _WebSocketStarted
    global _WebSocketQueue
    global _WebSocketConnecting
    global _WebSocketReady
    global _WebSocketAuthToken
    global _WebSocketSessionKey
    global _WebSocketApp
    global _RegisteredCallbacks
    if not is_started():
        raise Exception('has not been started')
    if _Debug:
        print('web_sock_remote.stop')
    _ClientInfoFilePath = None
    _RegisteredCallbacks = {}
    _WebSocketStarted = False
    _WebSocketConnecting = False
    _WebSocketReady = False
    _WebSocketAuthToken = None
    _WebSocketSessionKey = None
    while True:
        try:
            json_data, _ = ws_queue().get_nowait()
            if _Debug:
                print('web_sock_remote.stop cleaned unfinished call', json_data)
        except queue.Empty:
            break
    _WebSocketQueue.put_nowait((None, None, ))
    if _WebSocketApp:
        _WebSocketApp.close()
    else:
        if _Debug:
            print('web_sock_remote.stop websocket was already closed')
    _WebSocketApp = None

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
    global _WebSocketAuthToken
    global _WebSocketSessionKey
    _WebSocketReady = True
    _WebSocketClosed = False
    _WebSocketConnecting = False
    cb = registered_callbacks().get('on_open')
    if cb:
        cb(ws_inst)
    client_info = jsn.loads(system.ReadTextFile(_ClientInfoFilePath) or '{}')
    if _Debug:
        print('web_sock_remote.on_open websocket opened', time.time(), client_info)
    auth_token = client_info.get('auth_token')
    session_key_text = client_info.get('session_key')
    if auth_token and session_key_text:
        if _Debug:
            print('web_sock_remote.on_open was already AUTHORIZED', ws_inst)
        _WebSocketAuthToken = auth_token
        _WebSocketSessionKey = base64.b64decode(strng.to_bin(session_key_text))
        on_connect(ws_inst)
        return
    restart_handshake()


@mainthread
def on_connect(ws_inst):
    global _PendingCalls
    if _Debug:
        print('web_sock_remote.on_connect websocket connected', ws_inst, time.time(), len(_PendingCalls))
    cb = registered_callbacks().get('on_connect')
    if cb:
        cb(ws_inst)
    while _PendingCalls:
        json_data, cb = _PendingCalls.pop(0)
        if _Debug:
            print('on_connect pushing data', json_data)
        try:
            ws_queue().put_nowait((json_data, cb, ))
        except Exception as exc:
            if _Debug:
                print('web_sock_remote.on_connect websocket was not opened', exc)
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
        print('web_sock_remote.on_close websocket closed', ws_inst, time.time())
    cb = registered_callbacks().get('on_close')
    if cb:
        cb(ws_inst)


@mainthread
def on_error(ws_inst, error):
    if _Debug:
        print('web_sock_remote.on_error', ws_inst, error)
    cb = registered_callbacks().get('on_error')
    if cb:
        cb(ws_inst, error)


@mainthread
def on_fail(err, result_callback=None):
    if _Debug:
        print('web_sock_remote.on_fail', err)
    if result_callback:
        result_callback(err)

#------------------------------------------------------------------------------

@mainthread
def on_message(ws_inst, message):
    global _CallbacksQueue
    global _ClientInfoFilePath
    global _WebSocketAuthToken
    global _WebSocketSessionKey
    json_data = jsn.loads(message)
    cmd = json_data.get('cmd')
    if _Debug:
        print('web_sock_remote.on_message [%s] with %d bytes' % ((str(cmd)[:20]), len(message)))
    if cmd == 'server-public-key':
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
                print('web_sock_remote.on_message failed reading server_public_key', e)
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
            cb(ws_inst)
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
            linked_routers = client_info.get('routers') or []
            client_key_object = rsa_key.RSAKey()
            client_key_object.fromDict(client_info['key'])
            server_key_object = rsa_key.RSAKey()
            server_key_object.fromString(client_info['server_public_key'])
            received_salted_payload = strng.to_text(client_key_object.decrypt(orig_encrypted_payload))
            hashed_payload = hashes.sha1(strng.to_bin(received_salted_payload))
            received_client_code, auth_token, session_key_text, _ = received_salted_payload.split('#')  
        except Exception as e:
            if _Debug:
                print('web_sock_remote.on_message failed reading server_public_key', e)
            cb = registered_callbacks().get('on_handshake_failed')
            if cb:
                cb(ws_inst, e)
            return False
        if not server_key_object.verify(strng.to_bin(signature), hashed_payload):
            if _Debug:
                print('web_sock_remote.on_message authorization response signature verification failed')
            cb = registered_callbacks().get('on_handshake_failed')
            if cb:
                cb(ws_inst, Exception('signature verification failed'))
            return False
        if received_client_code != client_code:
            if _Debug:
                print('web_sock_remote.on_message client code is not matching')
            cb = registered_callbacks().get('on_handshake_failed')
            if cb:
                cb(ws_inst, Exception('client code is not matching'))
            return False
        client_info['auth_token'] = auth_token
        client_info['session_key'] = session_key_text
        client_info['routers'] = linked_routers
        client_info['state'] = 'authorized'
        system.WriteTextFile(_ClientInfoFilePath, jsn.dumps(client_info, indent=2))
        _WebSocketAuthToken = auth_token
        _WebSocketSessionKey = base64.b64decode(strng.to_bin(session_key_text))
        if _Debug:
            print('web_sock_remote.on_message AUTHORIZED', ws_inst)
        on_connect(ws_inst)        
        return True
    if cmd in ['response', 'push', 'publish-routers']:
        if 'iv' not in json_data or 'ct' not in json_data:
            if _Debug:
                print('web_sock_remote.on_message received not encrypted web socket message: %r' % json_data)
            return False
        try:
            decrypted_raw_data = cipher.decrypt_json(json_data, _WebSocketSessionKey, from_dict=True)
            decrypted_json_payload = serialization.BytesToDict(decrypted_raw_data, keys_to_text=True, values_to_text=True, encoding='utf-8')
        except Exception as exc:
            if _Debug:
                print('web_sock_remote.on_message failed receiving incoming message payload: %r' % exc)
            return False
        if cmd == 'response':
            if 'payload' not in decrypted_json_payload:
                if _Debug:
                    print('web_sock_remote.on_message no payload found in the response: %r' % decrypted_json_payload)
                return False
            if 'call_id' not in json_data:
                if _Debug:
                    print('        call_id not found in the response')
                return False
            call_id = json_data['call_id']
            if call_id not in _CallbacksQueue:
                if _Debug:
                    print('        call_id found in the response, but no callbacks registered')
                return False
            result_callback = _CallbacksQueue.pop(call_id)
            if _DebugAPIResponses:
                if decrypted_json_payload['payload'].get('response'):
                    print('WS API Response {} : {}'.format(call_id, decrypted_json_payload['payload']['response'], ))
            if result_callback:
                result_callback(decrypted_json_payload)
            return True
        if cmd == 'push':
            if 'payload' not in decrypted_json_payload:
                if _Debug:
                    print('web_sock_remote.on_message no payload found in the response: %r' % decrypted_json_payload)
                return False
            payload_type = decrypted_json_payload.get('type')
            if payload_type == 'event':
                return on_event(decrypted_json_payload)
            if payload_type == 'stream_message':
                return on_stream_message(decrypted_json_payload)
            if payload_type == 'model':
                return on_model_update(decrypted_json_payload)
        if cmd == 'publish-routers':
            if 'routers' not in decrypted_json_payload:
                if _Debug:
                    print('        routers list was not found in the response')
                return False
            try:
                client_info = jsn.loads(system.ReadTextFile(_ClientInfoFilePath) or '{}')
                client_info['routers'] = decrypted_json_payload['routers']
                client_info['authorized_routers'] = decrypted_json_payload.get('authorized_routers') or {}
                system.WriteTextFile(_ClientInfoFilePath, jsn.dumps(client_info, indent=2))
            except Exception as e:
                if _Debug:
                    print('web_sock_remote.on_message failed writing updated routers list', e)
                return False
            if _Debug:
                print('        routers list was updated: %r' % client_info['routers'])
            return True
    if cmd == 'server-disconnected':
        if _Debug:
            print('    routed web socket connection was DISCONNECTED from server side')
        cb = registered_callbacks().get('on_server_disconnected')
        if cb:
            cb(ws_inst)
        return False
    if _Debug:
        print('       message was not processed', json_data)
    return False

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

def generate_client_private_key():
    global _ClientInfoFilePath
    client_info = jsn.loads(system.ReadTextFile(_ClientInfoFilePath) or '{}')
    if _Debug:
        print('web_sock_remote.generate_client_private_key about to generate new RSA key for remote web socket connection')
    key_object = rsa_key.RSAKey()
    key_object.generate(2048)
    client_info['key'] = key_object.toDict(include_private=True)
    client_info['state'] = 'init'
    system.WriteTextFile(_ClientInfoFilePath, jsn.dumps(client_info, indent=2))


def load_server_auth_info(encrypted_auth_info, signature, server_public_key_text):
    global _ClientInfoFilePath
    client_info = jsn.loads(system.ReadTextFile(_ClientInfoFilePath) or '{}')
    client_code = client_info.get('client_code') or None
    client_key_object = rsa_key.RSAKey()
    client_key_object.fromDict(client_info['key'])
    orig_encrypted_payload = base64.b64decode(strng.to_bin(encrypted_auth_info))
    server_key_object = rsa_key.RSAKey()
    server_key_object.fromString(server_public_key_text)
    received_salted_payload = strng.to_text(client_key_object.decrypt(orig_encrypted_payload))
    hashed_payload = hashes.sha1(strng.to_bin(received_salted_payload))
    if not server_key_object.verify(strng.to_bin(signature), hashed_payload):
        if _Debug:
            print('web_sock_remote.load_server_auth_info authorization info signature verification failed')
        raise Exception('signature verification failed')
    received_client_code, auth_token, session_key_text, _ = received_salted_payload.split('#')
    if client_code and received_client_code != client_code:
        if _Debug:
            print('web_sock_remote.load_server_auth_info client code is not matching')
        raise Exception('client code is not matching')
    client_info['auth_token'] = auth_token
    client_info['session_key'] = session_key_text
    client_info['server_public_key'] = server_public_key_text
    client_info['state'] = 'authorized'
    system.WriteTextFile(_ClientInfoFilePath, jsn.dumps(client_info, indent=2))


def restart_handshake():
    global _ClientInfoFilePath
    generate_client_private_key()
    client_info = jsn.loads(system.ReadTextFile(_ClientInfoFilePath) or '{}')
    key_object = rsa_key.RSAKey()
    key_object.fromDict(client_info['key'])
    json_data = {
        'cmd': 'client-public-key',
        'client_public_key': key_object.toPublicString(),
    }
    if _Debug:
        print('web_sock_remote.restart_handshake pushing data', json_data)
    ws_queue().put_nowait((json_data, None, ))


def continue_handshake(server_code):
    global _ClientInfoFilePath
    client_info = jsn.loads(system.ReadTextFile(_ClientInfoFilePath) or '{}')
    salted_server_code = server_code + '-' + cipher.generate_secret_text(32)
    server_key_object = rsa_key.RSAKey()
    server_key_object.fromString(client_info['server_public_key'])
    encrypted_server_code = base64.b64encode(server_key_object.encrypt(strng.to_bin(salted_server_code)))
    hashed_server_code = hashes.sha1(strng.to_bin(salted_server_code))
    client_key_object = rsa_key.RSAKey()
    client_key_object.fromDict(client_info['key'])
    client_info['client_code'] = cipher.generate_digits(4, as_text=True)
    system.WriteTextFile(_ClientInfoFilePath, jsn.dumps(client_info, indent=2))
    # here must be shown the client_code digits in the BitDust Node UI
    # user will have to enter the displayed client code on the server manually if BitDust runs in headless mode
    json_data = {
        'cmd': 'server-code',
        'server_code': strng.to_text(encrypted_server_code),
        'signature': strng.to_text(client_key_object.sign(hashed_server_code)),
    }
    if _Debug:
        print('web_sock_remote.continue_handshake pushing data', json_data)
    ws_queue().put_nowait((json_data, None, ))
    if _Debug:
        print('web_sock_remote.continue_handshake client code: %r' % client_info['client_code'])
    return client_info['client_code']

#------------------------------------------------------------------------------

def requests_thread(active_queue):
    global _LastCallID
    global _CallbacksQueue
    if _Debug:
        print('web_sock_remote is starting requests_thread()')
    while True:
        if not is_started():
            if _Debug:
                print('web_sock_remote is finishing requests_thread() because web socket is not started')
            break
        json_data, result_callback = active_queue.get()
        if json_data is None:
            if _Debug:
                print('web_sock_remote is going to stop requests_thread()')
            break
        if 'call_id' not in json_data:
            _LastCallID += 1
            json_data['call_id'] = _LastCallID
        else:
            _LastCallID = json_data['call_id']
        call_id = json_data['call_id']
        if call_id in _CallbacksQueue:
            if _Debug:
                print('web_sock_remote ERROR call_id was not unique')
            on_fail(Exception('call_id was not unique'), result_callback)
            continue
        if not ws():
            if _Debug:
                print('web_sock_remote websocket is closed')
            on_fail(Exception('websocket is closed'), result_callback)
            continue
        _CallbacksQueue[call_id] = result_callback
        raw_data = serialization.DictToBytes(json_data, encoding='utf-8', to_text=True)
        if _Debug:
            print('    sending %d bytes' % len(raw_data))
        try:
            ws().send(raw_data)
        except Exception as exc:
            if _Debug:
                print('web_sock_remote errors sending data', exc)
    if _Debug:
        print('web_sock_remote.requests_thread() finished')


def websocket_thread():
    global _ClientInfoFilePath
    global _WebSocketApp
    global _WebSocketClosed
    global _WebSocketConnectingAttempts
    web_socket.enableTrace(False)
    if _Debug:
        print('web_sock_remote.websocket_thread beginning _ClientInfoFilePath=%r attempts=%r' % (_ClientInfoFilePath, _WebSocketConnectingAttempts))
    client_info = jsn.loads(system.ReadTextFile(_ClientInfoFilePath) or '{}')
    routers = client_info['routers']
    max_attempts = len(routers)
    if _WebSocketConnectingAttempts > max_attempts:
        _WebSocketConnectingAttempts = 0
    while is_started():
        if _Debug:
            print('web_sock_remote.websocket_thread making %d attempt, calling run_forever() %r' % (_WebSocketConnectingAttempts, time.asctime()))
        _WebSocketClosed = False
        client_info = jsn.loads(system.ReadTextFile(_ClientInfoFilePath) or '{}')
        routers = client_info['routers']
        max_attempts = len(routers)
        if _WebSocketConnectingAttempts > max_attempts:
            on_error(None, Exception('connection attempts exceeded, failed connecting to web socket routers'))
            break
        url = routers[_WebSocketConnectingAttempts - 1]
        _WebSocketConnectingAttempts += 1
        if _Debug:
            print('web_sock_remote.websocket_thread is going to connect to %r, attempts=%r, max_attempts=%r' % (url, _WebSocketConnectingAttempts, max_attempts))
        _WebSocketApp = web_socket.WebSocketApp(
            url=url,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open,
        )
        try:
            ret = ws().run_forever(ping_interval=5*60, ping_timeout=15)
        except Exception as exc:
            ret = None
            _WebSocketApp = None
            if _Debug:
                print('web_sock_remote.websocket_thread: %r' % exc)
            time.sleep(5)
        if _Debug:
            print('web_sock_remote.websocket_thread run_forever() returned: %r  is_started: %r' % (ret, is_started(), ))
        if _WebSocketApp:
            del _WebSocketApp
            _WebSocketApp = None
        if not is_started():
            break
        time.sleep(5)
    _WebSocketApp = None
    if _Debug:
        print('web_sock_remote.websocket_thread finished')

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
                print('web_sock_remote.verify_state web socket closed but still connecting')
            return 'closed'
        return 'closed'
    if is_ready():
        return 'ready'
    if is_connecting():
        return 'connecting'
    if is_started():
        return 'connecting'
    return 'not-started'


def encrypt_api_payload(json_data):
    global _WebSocketAuthToken
    global _WebSocketSessionKey
    if not _WebSocketAuthToken:
        raise Exception('authorization token is not ready')
    if not _WebSocketSessionKey:
        raise Exception('session key is not ready')
    json_data['salt'] = cipher.generate_secret_text(10)
    raw_bytes = serialization.DictToBytes(json_data, encoding='utf-8')
    encrypted_json_data = cipher.encrypt_json(raw_bytes, _WebSocketSessionKey, to_dict=True)
    ret = {
        'cmd': 'api',
        'auth': _WebSocketAuthToken,
        'payload': encrypted_json_data,
    }
    if _Debug:
        print('web_sock_remote.encrypt_api_payload', len(raw_bytes))
    return ret


def ws_call(json_data, cb=None):
    global _PendingCalls
    global _ClientInfoFilePath
    st = verify_state()
    # if _Debug:
    #     print('ws_call', st)
    if st == 'ready':
        encrypted_json_data = encrypt_api_payload(json_data)
        ws_queue().put_nowait((encrypted_json_data, cb, ))
        return True
    if st == 'closed':
        if cb:
            cb(Exception('web socket is closed'))
        return False
    if st == 'connecting':
        encrypted_json_data = encrypt_api_payload(json_data)
        if _Debug:
            print('web_sock_remote.ws_call web socket still connecting, remember pending request', encrypted_json_data)
        _PendingCalls.append((encrypted_json_data, cb, ))
        return True
    if st == 'not-started':
        if _Debug:
            print('web_sock_remote.ws_call web socket was not started')
        if cb:
            cb(Exception('web socket was not started'))
        return False
    raise Exception('unexpected state %r' % st)
