import threading

from jnius import autoclass, cast, PythonJavaClass, java_method  # @UnresolvedImport
from android import mActivity, api_version  # @UnresolvedImport
from android.config import ACTIVITY_CLASS_NAME, ACTIVITY_CLASS_NAMESPACE  # @UnresolvedImport

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

PERMISSION_GRANTED = 0
PERMISSION_DENIED = -1

#------------------------------------------------------------------------------

class _onRequestCustomPermissionsCallback(PythonJavaClass):

    __javainterfaces__ = [ACTIVITY_CLASS_NAMESPACE + '$CustomPermissionsCallback']
    __javacontext__ = 'app'

    def __init__(self, func):
        self.func = func
        super().__init__()

    @java_method('(I[Ljava/lang/String;[I)V')
    def onRequestCustomPermissionsResult(self, requestCode, permissions, grantResults):
        if _Debug:
            print('_RequestPermissionsManager.onRequestCustomPermissionsResult', requestCode, permissions, grantResults)
        self.func(requestCode, permissions, grantResults)


class _RequestPermissionsManager(object):

    _SDK_INT = None
    _java_callback = None
    _callbacks = {1: None}
    _callback_id = 1
    # Lock to prevent multiple calls to request_permissions being handled
    # simultaneously (as incrementing _callback_id is not atomic)
    _lock = threading.Lock()

    @classmethod
    def register_callback(cls):
        if _Debug:
            print('_RequestPermissionsManager.register_callback ACTIVITY_CLASS_NAME=%r' % ACTIVITY_CLASS_NAME)
        cls._java_callback = _onRequestCustomPermissionsCallback(cls.python_callback)
        mActivity = autoclass(ACTIVITY_CLASS_NAME).mActivity
        mActivity.addCustomPermissionsCallback(cls._java_callback)

    @classmethod
    def request_permissions(cls, permissions, callback=None):
        if not cls._SDK_INT:
            # Get the Android build version and store it
            VERSION = autoclass('android.os.Build$VERSION')
            cls._SDK_INT = VERSION.SDK_INT
            if _Debug:
                print('_RequestPermissionsManager.request_permissions SDK_INT=%r' % cls._SDK_INT)
        if cls._SDK_INT < 23:
            # No run-time permissions needed, return immediately.
            if callback:
                callback(permissions, [True for _ in permissions])
            return
        if _Debug:
            print('request_permissions permissions=%r ACTIVITY_CLASS_NAME=%r' % (permissions, ACTIVITY_CLASS_NAME, ))
        # Request permissions
        with cls._lock:
            if not cls._java_callback:
                cls.register_callback()
            mActivity = autoclass(ACTIVITY_CLASS_NAME).mActivity
            if not callback:
                mActivity.requestCustomPermissions(permissions)
            else:
                cls._callback_id += 1
                mActivity.requestCustomPermissionsWithRequestCode(permissions, cls._callback_id)
                cls._callbacks[cls._callback_id] = callback

    @classmethod
    def python_callback(cls, requestCode, permissions, grantResults):
        if _Debug:
            print('_RequestPermissionsManager.python_callback grantResults=%r' % grantResults)
        grant_results = [x == PERMISSION_GRANTED for x in grantResults]
        if cls._callbacks.get(requestCode):
            cls._callbacks[requestCode](permissions, grant_results)


def request_permissions(permissions, callback=None):
    _RequestPermissionsManager.request_permissions(permissions, callback)


def request_permission(permission, callback=None):
    request_permissions([permission], callback)


def check_permission(permission):
    mActivity = autoclass(ACTIVITY_CLASS_NAME).mActivity
    if _Debug:
        print('check_permission permission=%r ACTIVITY_CLASS_NAME=%r mActivity=%r' % (permission, ACTIVITY_CLASS_NAME, mActivity, ))
    result = bool(mActivity.checkCurrentCustomPermission(permission))
    return result

def permissions_external_storage(*args):
    if _Debug:
        print('permissions_external_storage', args, api_version)
    PythonActivity = autoclass("org.kivy.android.PythonActivity")
    Environment = autoclass("android.os.Environment")
    Intent = autoclass("android.content.Intent")
    Settings = autoclass("android.provider.Settings")
    Uri = autoclass("android.net.Uri")
    if api_version > 29:
        if Environment.isExternalStorageManager():
            # If you have access to the external storage, do whatever you need
            if _Debug:
                print('permissions_external_storage Environment.isExternalStorageManager() returns True')
        else:
            if _Debug:
                print('permissions_external_storage Environment.isExternalStorageManager() returns False')
            # If you don't have access, launch a new activity to show the user the system's dialog
            # to allow access to the external storage
            try:
                activity = mActivity.getApplicationContext()
                uri = Uri.parse("package:" + activity.getPackageName())
                intent = Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION, uri)
                currentActivity = cast("android.app.Activity", PythonActivity.mActivity)
                currentActivity.startActivityForResult(intent, 101)
            except Exception as exc:
                if _Debug:
                    print(exc)
                intent = Intent()
                intent.setAction(Settings.ACTION_MANAGE_ALL_FILES_ACCESS_PERMISSION)
                currentActivity = cast("android.app.Activity", PythonActivity.mActivity)
                currentActivity.startActivityForResult(intent, 101)
