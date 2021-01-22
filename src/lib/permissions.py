import threading

from jnius import autoclass, PythonJavaClass, java_method  # @UnresolvedImport


PERMISSION_GRANTED = 0
PERMISSION_DENIED = -1

ACTIVITY_CLASS_NAME = 'org.kivy.android.PythonActivity'
ACTIVITY_CLASS_NAMESPACE = 'org/kivy/android/PythonActivity'


class _onRequestPermissionsCallback(PythonJavaClass):
    """Callback class for registering a Python callback from
    onRequestPermissionsResult in PythonActivity.
    """
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
    """Internal class for requesting Android permissions.

    Permissions are requested through the method 'request_permissions' which
    accepts a list of permissions and an optional callback.

    Any callback will asynchronously receive arguments from
    onRequestPermissionsResult on PythonActivity after requestPermissions is
    called.

    The callback supplied must accept two arguments: 'permissions' and
    'grantResults' (as supplied to onPermissionsCallbackResult).

    Note that for SDK_INT < 23, run-time permissions are not required, and so
    the callback will be called immediately.

    The attribute '_java_callback' is initially None, but is set when the first
    permissions request is made. It is set to an instance of
    onRequestPermissionsCallback, which allows the Java callback to be
    propagated to the class method 'python_callback'. This is then, in turn,
    used to call an application callback if provided to request_permissions.

    The attribute '_callback_id' is incremented with each call to
    request_permissions which has a callback (the value '1' is used for any
    call which does not pass a callback). This is passed to requestCode in
    the Java call, and used to identify (via the _callbacks dictionary)
    the matching call.
    """
    _SDK_INT = None
    _java_callback = None
    _callbacks = {1: None}
    _callback_id = 1
    # Lock to prevent multiple calls to request_permissions being handled
    # simultaneously (as incrementing _callback_id is not atomic)
    _lock = threading.Lock()

    @classmethod
    def register_callback(cls):
        """Register Java callback for requestPermissions."""
        cls._java_callback = _onRequestPermissionsCallback(cls.python_callback)
        mActivity = autoclass(ACTIVITY_CLASS_NAME).mActivity
        mActivity.addPermissionsCallback(cls._java_callback)

    @classmethod
    def request_permissions(cls, permissions, callback=None):
        """Requests Android permissions from PythonActivity.
        If 'callback' is supplied, the request is made with a new requestCode
        and the callback is stored in the _callbacks dict. When a Java callback
        with the matching requestCode is received, callback will be called
        with arguments of 'permissions' and 'grant_results'.
        """
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
        """Calls the relevant callback with arguments of 'permissions'
        and 'grantResults'."""
        # Convert from Android codes to True/False
        grant_results = [x == PERMISSION_GRANTED for x in grantResults]
        if cls._callbacks.get(requestCode):
            cls._callbacks[requestCode](permissions, grant_results)


# Public API methods for requesting permissions

def request_permissions(permissions, callback=None):
    """Requests Android permissions.

    Args:
        permissions (str): A list of permissions to requests (str)
        callback (callable, optional): A function to call when the request
            is completed (callable)

    Returns:
        None

    Notes:

    Permission strings can be imported from the 'Permission' class in this
    module. For example:

    from android import Permission
        permissions_list = [Permission.CAMERA,
                            Permission.WRITE_EXTERNAL_STORAGE]

    See the p4a source file 'permissions.py' for a list of valid permission
    strings (pythonforandroid/recipes/android/src/android/permissions.py).

    Any callback supplied must accept two arguments:
       permissions (list of str): A list of permission strings
       grant_results (list of bool): A list of bools indicating whether the
           respective permission was granted.
    See Android documentation for onPermissionsCallbackResult for
    further information.

    Note that if the request is interupted the callback may contain an empty
    list of permissions, without permissions being granted; the App should
    check that each permission requested has been granted.

    Also note that when calling request_permission on SDK_INT < 23, the
    callback will be returned immediately as requesting permissions is not
    required.
    """
    _RequestPermissionsManager.request_permissions(permissions, callback)


def request_permission(permission, callback=None):
    request_permissions([permission], callback)


def check_permission(permission):
    """Checks if an app holds the passed permission.

    Args:
        - permission     An Android permission (str)

    Returns:
        bool: True if the app holds the permission given, False otherwise.
    """
    mActivity = autoclass(ACTIVITY_CLASS_NAME).mActivity
    result = bool(mActivity.checkCurrentPermission(
        permission + ""
    ))
    return result
