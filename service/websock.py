try:
    import thread
except ImportError:
    import _thread as thread
import queue
import websocket
import json

#------------------------------------------------------------------------------

from kivy.clock import mainthread

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

_WebSocketApp = None
_WebSocketQueue = None
_WebSocketReady = False
_WebSocketClosed = False
_LastCallID = 0
_PendingCalls = []
_CallbacksQueue = {}

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

#------------------------------------------------------------------------------

@mainthread
def on_open(ws_inst):
    global _WebSocketReady
    global _WebSocketClosed
    global _PendingCalls
    _WebSocketReady = True
    _WebSocketClosed = False
    if _Debug:
        print('websocket opened')
    for json_data, cb, in _PendingCalls:
        ws_queue().put_nowait((json_data, cb, ))
    _PendingCalls.clear()


@mainthread
def on_close(ws_inst):
    global _WebSocketReady
    global _WebSocketClosed
    _WebSocketReady = False
    _WebSocketClosed = True
    if _Debug:
        print('websocket closed')


def on_event(json_data):
    if _Debug:
        print('    WS EVENT:', json_data['payload']['event_id'])
    return True


@mainthread
def on_message(ws_inst, message):
    global _CallbacksQueue
    json_data = json.loads(message)
    if _Debug:
        print('        on_message', json_data)
    if 'payload' not in json_data:
        if _Debug:
            print('no payload found in the response')
        return False
    payload_type = json_data.get('type')
    if payload_type == 'event':
        return on_event(json_data)
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
        if _Debug:
            print('going to call %r' % result_callback)
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
    for json_data, cb, in _PendingCalls:
        if cb:
            cb(error)


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
        print('request thread finishing')


def websocket_thread():
    global _WebSocketApp
    websocket.enableTrace(False)
    _WebSocketApp = websocket.WebSocketApp(
        "ws://localhost:8280/",
        on_message = on_message,
        on_error = on_error,
        on_close = on_close,
        on_open = on_open,
    )
    ws().run_forever(ping_interval=10)
    if _Debug:
        print('websocket thread finishing')

#------------------------------------------------------------------------------

def start():
    global _WebSocketQueue
    _WebSocketQueue = queue.Queue(maxsize=100)
    thread.start_new_thread(websocket_thread, ())
    thread.start_new_thread(requests_thread, (_WebSocketQueue, ))


def stop():
    global _WebSocketQueue
    while True:
        try:
            json_data, _ = ws_queue().get_nowait()
            print('cleaned unfinished call', json_data)
        except queue.Empty:
            break
    _WebSocketQueue.put_nowait((None, None, ))
    ws().close()

#------------------------------------------------------------------------------

def ws_call(json_data, cb=None):
    global _PendingCalls
    if not is_ready():
        if not is_closed():
            if _Debug:
                print('websocket not started yet, remember pending request')
            _PendingCalls.append((json_data, cb, ))
        else:
            if _Debug:
                print('about to restart websocket thread')
            thread.start_new_thread(websocket_thread, ())
    else:
        ws_queue().put_nowait((json_data, cb, ))

#------------------------------------------------------------------------------

def is_ok(response):
    return response_status(response) == 'OK'


def response_errors(response):
    return response.get('payload', {}).get('response', {}).get('errors', [])


def response_status(response):
    return response.get('payload', {}).get('response', {}).get('status', '')
