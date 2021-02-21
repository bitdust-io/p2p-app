import threading

from jnius import autoclass, PythonJavaClass, java_method  # @UnresolvedImport

#------------------------------------------------------------------------------

PERMISSION_GRANTED = 0
PERMISSION_DENIED = -1

ACTIVITY_CLASS_NAME = 'org.kivy.android.PythonActivity'
ACTIVITY_CLASS_NAMESPACE = 'org/kivy/android/PythonActivity'
# ACTIVITY_CLASS_NAME = 'org.bitdust_io.bitdust1.BitDustActivity'
# ACTIVITY_CLASS_NAMESPACE = 'org/bitdust_io/bitdust1/BitDustActivity'

#------------------------------------------------------------------------------

class _onRequestPermissionsCallback(PythonJavaClass):

    __javainterfaces__ = [ACTIVITY_CLASS_NAMESPACE + '$PermissionsCallback']
    __javacontext__ = 'app'

    def __init__(self, func):
        self.func = func
        super().__init__()

    @java_method('(I[Ljava/lang/String;[I)V')
    def onRequestPermissionsResult(self, requestCode,
                                   permissions, grantResults):
        self.func(requestCode, permissions, grantResults)


class _RequestPermissionsManager:

    _SDK_INT = None
    _java_callback = None
    _callbacks = {1: None}
    _callback_id = 1
    # Lock to prevent multiple calls to request_permissions being handled
    # simultaneously (as incrementing _callback_id is not atomic)
    _lock = threading.Lock()

    @classmethod
    def register_callback(cls):
        cls._java_callback = _onRequestPermissionsCallback(cls.python_callback)
        mActivity = autoclass(ACTIVITY_CLASS_NAME).mActivity
        mActivity.addPermissionsCallback(cls._java_callback)

    @classmethod
    def request_permissions(cls, permissions, callback=None):
        if not cls._SDK_INT:
            # Get the Android build version and store it
            VERSION = autoclass('android.os.Build$VERSION')
            cls.SDK_INT = VERSION.SDK_INT
        if cls.SDK_INT < 23:
            # No run-time permissions needed, return immediately.
            if callback:
                callback(permissions, [True for x in permissions])
                return
        # Request permissions
        with cls._lock:
            if not cls._java_callback:
                cls.register_callback()
            mActivity = autoclass(ACTIVITY_CLASS_NAME).mActivity
            if not callback:
                mActivity.requestPermissions(permissions)
            else:
                cls._callback_id += 1
                mActivity.requestPermissionsWithRequestCode(
                    permissions, cls._callback_id)
                cls._callbacks[cls._callback_id] = callback

    @classmethod
    def python_callback(cls, requestCode, permissions, grantResults):
        grant_results = [x == PERMISSION_GRANTED for x in grantResults]
        if cls._callbacks.get(requestCode):
            cls._callbacks[requestCode](permissions, grant_results)


def request_permissions(permissions, callback=None):
    _RequestPermissionsManager.request_permissions(permissions, callback)


def request_permission(permission, callback=None):
    request_permissions([permission], callback)


def check_permission(permission):
    mActivity = autoclass(ACTIVITY_CLASS_NAME).mActivity
    result = bool(mActivity.checkCurrentPermission(
        permission + ""
    ))
    return result
