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

_WebSocketApp = None
_WebSocketQueue = None
_WebSocketReady = False
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

#------------------------------------------------------------------------------

@mainthread
def on_message(ws_inst, message):
    global _CallbacksQueue
    json_data = json.loads(message)
    print(json_data)
    if 'call_id' not in json_data:
        return
    call_id = json_data['call_id']
    if call_id not in _CallbacksQueue:
        return
    result_callback = _CallbacksQueue.pop(call_id)
    print('going to call %r with %r' % (result_callback, json_data, ))
    result_callback(json_data)


@mainthread
def on_error(ws_inst, error):
    print(error)


@mainthread
def on_close(ws_inst):
    global _WebSocketReady
    _WebSocketReady = False
    print("ws closed")


@mainthread
def on_open(ws_inst):
    global _WebSocketReady
    global _PendingCalls
    _WebSocketReady = True
    print("ws started")
    for json_data, cb, in _PendingCalls:
        ws_queue().put_nowait((json_data, cb, ))
    _PendingCalls.clear()


@mainthread
def on_fail(err, result_callback=None):
    if result_callback:
        result_callback(err)

#------------------------------------------------------------------------------

def queue_thread(active_queue):
    global _LastCallID
    global _CallbacksQueue
    while True:
        json_data, result_callback = active_queue.get()
        if json_data is None:
            print('going to stop queue_thread')
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
        print('sending', data)
        ws().send(data)


def ws_thread():
    global _WebSocketApp
    websocket.enableTrace(False)
    _WebSocketApp = websocket.WebSocketApp(
        "ws://localhost:8280/",
        on_message = on_message,
        on_error = on_error,
        on_close = on_close,
        on_open = on_open,
    )
    ws().run_forever()

#------------------------------------------------------------------------------

def start():
    global _WebSocketQueue
    _WebSocketQueue = queue.Queue(maxsize=100)
    thread.start_new_thread(ws_thread, ())
    thread.start_new_thread(queue_thread, (_WebSocketQueue, ))


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
    print('ws_call', json_data)
    if not is_ready():
        _PendingCalls.append((json_data, cb, ))
    else:
        ws_queue().put_nowait((json_data, cb, ))
