from jnius import PythonJavaClass, autoclass, java_method  # @UnresolvedImport
from android.config import ACTIVITY_CLASS_NAME, ACTIVITY_CLASS_NAMESPACE  # @UnresolvedImport

_activity = autoclass(ACTIVITY_CLASS_NAME).mBitDustActivity

_callbacks = {
    'on_new_intent': [],
    'on_activity_result': [],
}


class CustomNewIntentListener(PythonJavaClass):
    __javainterfaces__ = [ACTIVITY_CLASS_NAMESPACE + '$CustomNewIntentListener']
    __javacontext__ = 'app'

    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback

    @java_method('(Landroid/content/Intent;)V')
    def onNewIntent(self, intent):
        self.callback(intent)


class CustomActivityResultListener(PythonJavaClass):
    __javainterfaces__ = [ACTIVITY_CLASS_NAMESPACE + '$CustomActivityResultListener']
    __javacontext__ = 'app'

    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    @java_method('(IILandroid/content/Intent;)V')
    def onActivityResult(self, requestCode, resultCode, intent):
        self.callback(requestCode, resultCode, intent)


def bind(**kwargs):
    for event, callback in kwargs.items():
        if event not in _callbacks:
            raise Exception('Unknown {!r} event'.format(event))
        elif event == 'on_new_intent':
            listener = CustomNewIntentListener(callback)
            _activity.registerCustomNewIntentListener(listener)
            _callbacks[event].append(listener)
        elif event == 'on_activity_result':
            listener = CustomActivityResultListener(callback)
            _activity.registerCustomActivityResultListener(listener)
            _callbacks[event].append(listener)


def unbind(**kwargs):
    for event, callback in kwargs.items():
        if event not in _callbacks:
            raise Exception('Unknown {!r} event'.format(event))
        else:
            for listener in _callbacks[event][:]:
                if listener.callback == callback:
                    _callbacks[event].remove(listener)
                    if event == 'on_new_intent':
                        _activity.unregisterCustomNewIntentListener(listener)
                    elif event == 'on_activity_result':
                        _activity.unregisterCustomActivityResultListener(listener)
