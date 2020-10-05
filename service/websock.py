import time

try:
    import thread
except ImportError:
    import _thread as thread

import queue
import websocket
import json

#------------------------------------------------------------------------------

from kivy.clock import mainthread, Clock

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

_WebSocketApp = None
_WebSocketQueue = None
_WebSocketReady = False
_WebSocketClosed = False
_WebSocketStarted = False
_WebSocketConnecting = False
_LastCallID = 0
_PendingCalls = []
_CallbacksQueue = {}


#------------------------------------------------------------------------------

def start():
    global _WebSocketStarted
    global _WebSocketConnecting
    global _WebSocketQueue
    if is_started():
        raise Exception('already started')
    _WebSocketConnecting = True
    _WebSocketStarted = True
    _WebSocketQueue = queue.Queue(maxsize=100)
    thread.start_new_thread(websocket_thread, ())
    thread.start_new_thread(requests_thread, (_WebSocketQueue, ))


def stop():
    global _WebSocketStarted
    global _WebSocketQueue
    global _WebSocketConnecting
    if not is_started():
        raise Exception('has not been started')
    _WebSocketStarted = False
    _WebSocketConnecting = False
    while True:
        try:
            json_data, _ = ws_queue().get_nowait()
            print('cleaned unfinished call', json_data)
        except queue.Empty:
            break
    _WebSocketQueue.put_nowait((None, None, ))
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

#------------------------------------------------------------------------------

@mainthread
def on_open(ws_inst):
    global _WebSocketReady
    global _WebSocketClosed
    global _WebSocketConnecting
    global _PendingCalls
    _WebSocketReady = True
    _WebSocketClosed = False
    _WebSocketConnecting = False
    if _Debug:
        print('websocket opened')
    for json_data, cb, in _PendingCalls:
        ws_queue().put_nowait((json_data, cb, ))
    _PendingCalls.clear()


@mainthread
def on_close(ws_inst):
    global _WebSocketReady
    global _WebSocketClosed
    global _WebSocketConnecting
    _WebSocketReady = False
    _WebSocketClosed = True
    _WebSocketConnecting = False
    if _Debug:
        print('websocket closed')


def on_event(json_data):
    if _Debug:
        print('    WS EVENT:', json_data['payload']['event_id'])
    return True


def on_stream_message(json_data):
    if _Debug:
        print('    WS STREAM MSG:', json_data['payload']['payload']['message_id'])
    return True


@mainthread
def on_message(ws_inst, message):
    global _CallbacksQueue
    json_data = json.loads(message)
    if _Debug:
        print('        on_message %d bytes' % len(message))
    if 'payload' not in json_data:
        if _Debug:
            print('no payload found in the response')
        return False
    payload_type = json_data.get('type')
    if payload_type == 'event':
        return on_event(json_data)
    if payload_type == 'stream_message':
        return on_stream_message(json_data)
    if payload_type == 'api_call':
        if 'call_id' not in json_data['payload']:
            if _Debug:
                print('call_id not found in the response')
            return
        call_id = json_data['payload']['call_id']
        if call_id not in _CallbacksQueue:
            if _Debug:
                print('call_id found in the response, but no callbacks registered')
            return
        result_callback = _CallbacksQueue.pop(call_id)
        if result_callback:
            result_callback(json_data)
        return True
    if _Debug:
        print('        unexpected payload_type', json_data)
    raise Exception(payload_type)


@mainthread
def on_error(ws_inst, error):
    global _PendingCalls
    if _Debug:
        print('on_error', error)


@mainthread
def on_fail(err, result_callback=None):
    if _Debug:
        print('on_fail', err)
    if result_callback:
        result_callback(err)

#------------------------------------------------------------------------------

def requests_thread(active_queue):
    global _LastCallID
    global _CallbacksQueue
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
        _CallbacksQueue[call_id] = result_callback
        data = json.dumps(json_data)
        if _Debug:
            print('sending', data)
        ws().send(data)
    if _Debug:
        print('requests_thread() finished')


def websocket_thread():
    global _WebSocketApp
    global _WebSocketClosed
    websocket.enableTrace(False)
    _WebSocketApp = websocket.WebSocketApp(
        "ws://localhost:8280/",
        on_message = on_message,
        on_error = on_error,
        on_close = on_close,
        on_open = on_open,
    )
    if _Debug:
        print('websocket_thread() beginning')
    while is_started():
        if _Debug:
            print('websocket_thread() calling run_forever(ping_interval=10) %r' % time.asctime())
        _WebSocketClosed = False
        try:
            ret = ws().run_forever(ping_interval=10)
        except Exception as exc:
            if _Debug:
                print('websocket_thread(): %r' % exc)
            time.sleep(3)
        if _Debug:
            print('websocket_thread().run_forever() returned %r' % ret)
        if ret:
            time.sleep(3)
        else:
            break
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

def is_ok(response):
    if not isinstance(response, dict):
        return False
    return response_status(response) == 'OK'


def response_errors(response):
    if not isinstance(response, dict):
        return ['no response', ]
    return response.get('payload', {}).get('response', {}).get('errors', [])


def response_status(response):
    if not isinstance(response, dict):
        return ''
    return response.get('payload', {}).get('response', {}).get('status', '')


def response_result(response):
    if not isinstance(response, dict):
        return None
    return response.get('payload', {}).get('response', {}).get('result', [])
