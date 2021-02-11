from kivy.utils import platform

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

_LatestState = None
_LatestAndroidSDKVersion = None
_LatestAndroidBitDustActivity = None
_LatestAndroidRectClass = None
_LatestAndroidDisplayRealHeight = None
_LatestAndroidDisplayDefaultHeight = None
_LatestAndroidTopBarSize = None
_LatestAndroidBottomBarSize = None
_LatestAndroidKeyboardHeightSnapshot = 0

#------------------------------------------------------------------------------

def latest_state():
    global _LatestState
    if _LatestState:
        return _LatestState
    _LatestState = str('' + platform)
    return _LatestState

#------------------------------------------------------------------------------

def is_windows():
    return latest_state() == 'win'


def is_android():
    return latest_state() == 'android'


def is_ios():
    return latest_state() == 'ios'

#------------------------------------------------------------------------------

def android_sdk_version():
    global _LatestAndroidSDKVersion
    if not is_android():
        return None
    if _LatestAndroidSDKVersion is not None:
        return _LatestAndroidSDKVersion
    from jnius import autoclass  # @UnresolvedImport
    _LatestAndroidSDKVersion = autoclass('android.os.Build$VERSION').SDK_INT
    return _LatestAndroidSDKVersion

#------------------------------------------------------------------------------

def get_android_keyboard_height():
    global _LatestAndroidBitDustActivity
    global _LatestAndroidRectClass
    global _LatestAndroidDisplayRealHeight
    global _LatestAndroidDisplayDefaultHeight
    global _LatestAndroidTopBarSize
    global _LatestAndroidBottomBarSize
    global _LatestAndroidKeyboardHeightSnapshot
    if not is_android():
        return 0
    if _LatestAndroidBitDustActivity is None:
        from jnius import autoclass  # @UnresolvedImport
        _LatestAndroidBitDustActivity = autoclass('org.bitdust_io.bitdust1.BitDustActivity').mActivity
        _LatestAndroidRectClass = autoclass(u'android.graphics.Rect')
    if _LatestAndroidDisplayRealHeight is None:
        _LatestAndroidDisplayRealHeight = _LatestAndroidBitDustActivity.getDisplayRealHeight()
        if _Debug:
            print('system.get_android_keyboard_height         Display Real Height', _LatestAndroidDisplayRealHeight)
    if _LatestAndroidDisplayDefaultHeight is None:
        _LatestAndroidDisplayDefaultHeight = _LatestAndroidBitDustActivity.getWindowManager().getDefaultDisplay().getHeight()
        if _Debug:
            print('system.get_android_keyboard_height         Display Default Height', _LatestAndroidDisplayRealHeight)
    rctx = _LatestAndroidRectClass()
    _LatestAndroidBitDustActivity.getWindow().getDecorView().getWindowVisibleDisplayFrame(rctx)
    if _LatestAndroidTopBarSize is None:
        if _Debug:
            print('system.get_android_keyboard_height         Top Bar Size', rctx.top)
    # should overwrite because of portrait/landscape switching
    _LatestAndroidTopBarSize = rctx.top
    bottom_size_latest = _LatestAndroidDisplayRealHeight - _LatestAndroidDisplayDefaultHeight - _LatestAndroidTopBarSize
    if bottom_size_latest < 0:
        # if _Debug:
        #     print('system.get_android_keyboard_height         WARNING Bottom Bar Size  was going to be negative!', bottom_size_latest)
        bottom_size_latest = 0
    if _LatestAndroidBottomBarSize is None:
        if _Debug:
            print('system.get_android_keyboard_height         Bottom Bar Size', bottom_size_latest)
    _LatestAndroidBottomBarSize = bottom_size_latest
    visible_height = rctx.bottom - rctx.top
    keyboard_height = _LatestAndroidDisplayDefaultHeight - rctx.bottom + _LatestAndroidBottomBarSize
    if _LatestAndroidKeyboardHeightSnapshot != keyboard_height:
        old_keyboard_height = _LatestAndroidKeyboardHeightSnapshot
        _LatestAndroidKeyboardHeightSnapshot = keyboard_height
        if _Debug:
            print('system.get_android_keyboard_height updated latest snapshot %d->%d with real_H=%d default_H=%d visible_Top=%d visible_Bottom=%d visible_H=%d topBar_H=%d bottomBar_H=%d' % (
                old_keyboard_height, keyboard_height,
                _LatestAndroidDisplayRealHeight, _LatestAndroidDisplayDefaultHeight,
                rctx.top, rctx.bottom, visible_height,
                _LatestAndroidTopBarSize, _LatestAndroidBottomBarSize, ))
    return _LatestAndroidKeyboardHeightSnapshot


def set_android_system_ui_visibility():
    global _LatestAndroidBitDustActivity
    if not is_android():
        return
    from jnius import autoclass  # @UnresolvedImport
    if _LatestAndroidBitDustActivity is None:
        _LatestAndroidBitDustActivity = autoclass('org.bitdust_io.bitdust1.BitDustActivity').mActivity
    View = autoclass('android.view.View')
    decorView = _LatestAndroidBitDustActivity.getWindow().getDecorView()
    flags = View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY \
        | View.SYSTEM_UI_FLAG_FULLSCREEN \
        | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN \
        | View.SYSTEM_UI_FLAG_LAYOUT_STABLE \
        | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION \
        | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
    decorView.setSystemUiVisibility(flags)
    if _Debug:
        print('system.set_android_system_ui_visibility', decorView, flags)
