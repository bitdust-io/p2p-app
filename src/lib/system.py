import os
import subprocess
import time
import threading
from queue import Queue

#------------------------------------------------------------------------------

from kivy.utils import platform

#------------------------------------------------------------------------------

_Debug = False

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

def current_platform():
    global _LatestState
    if _LatestState:
        return _LatestState
    _LatestState = str('' + platform)
    if _Debug:
        print('system.current_platform', _LatestState)
    return _LatestState

#------------------------------------------------------------------------------

def is_linux():
    return current_platform() == 'linux'


def is_windows():
    return current_platform() == 'win'


def is_android():
    return current_platform() == 'android'


def is_ios():
    return current_platform() == 'ios'


def is_osx():
    return current_platform() == 'macosx'

#------------------------------------------------------------------------------

def get_app_data_path():
    """
    A portable method to get the default data folder location, usually it is: "~/.bitdust/"
    """
    if is_windows():
        # TODO: move somewhere on Win10 ...
        return os.path.join(os.path.expanduser('~'), '.bitdust')

    elif is_linux():
        # This should be okay : /home/veselin/.bitdust/
        return os.path.join(os.path.expanduser('~'), '.bitdust')

    elif is_android():
        try:
            from jnius import autoclass  # @UnresolvedImport
            Context = autoclass("android.content.Context")
            Environment = autoclass("android.os.Environment")
            documents_dir = Context.getExternalFilesDir(Environment.DIRECTORY_DOCUMENTS).getAbsolutePath()
        except Exception as e:
            if _Debug:
                print('get_app_data_path() failed', e)
            documents_dir = "/storage/emulated/0/Android/data/org.bitdust_io.bitdust1/files/Documents"
        if _Debug:
            print('get_app_data_path() documents_dir=%r' % documents_dir)
        return os.path.join(documents_dir, '.bitdust')

    elif is_osx():
        # This should be okay : /Users/veselin/.bitdust/
        return os.path.join(os.path.expanduser('~'), '.bitdust')

    # otherwise just default : ".bitdust/" in user root folder
    return os.path.join(os.path.expanduser('~'), '.bitdust')

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
    from android.config import ACTIVITY_CLASS_NAME  # @UnresolvedImport
    from jnius import autoclass  # @UnresolvedImport
    if _LatestAndroidBitDustActivity is None:
        _LatestAndroidBitDustActivity = autoclass(ACTIVITY_CLASS_NAME).mBitDustActivity
        _LatestAndroidRectClass = autoclass(u'android.graphics.Rect')
    if _LatestAndroidDisplayRealHeight is None:
        if android_sdk_version() >= 17:
            DisplayMetricsClass = autoclass(u'android.util.DisplayMetrics')
            metrics = DisplayMetricsClass()
            _LatestAndroidBitDustActivity.getWindowManager().getDefaultDisplay().getRealMetrics(metrics)
            _LatestAndroidDisplayRealHeight = metrics.heightPixels
        if _Debug:
            print('system.get_android_keyboard_height         Display Real Height', _LatestAndroidDisplayRealHeight)
    if _LatestAndroidDisplayRealHeight is None:
        return 0
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
        bottom_size_latest = 0
    if _LatestAndroidBottomBarSize is None:
        if _Debug:
            print('system.get_android_keyboard_height         Bottom Bar Size', bottom_size_latest)
    _LatestAndroidBottomBarSize = bottom_size_latest
    visible_height = rctx.bottom - rctx.top
    keyboard_height = _LatestAndroidDisplayDefaultHeight - rctx.bottom + _LatestAndroidBottomBarSize
    if _LatestAndroidDisplayDefaultHeight > 2000:
        if keyboard_height >= 32:
            keyboard_height -= 32
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
    from android.config import ACTIVITY_CLASS_NAME  # @UnresolvedImport
    if _LatestAndroidBitDustActivity is None:
        _LatestAndroidBitDustActivity = autoclass(ACTIVITY_CLASS_NAME).mBitDustActivity
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

#------------------------------------------------------------------------------

def ReadTextFile(filename):
    """
    Read text file and return its content.
    """
    if not os.path.isfile(filename):
        return u''
    if not os.access(filename, os.R_OK):
        return u''
    try:
        infile = open(filename, 'rt', encoding="utf-8")
        data = infile.read()
        infile.close()
        return data
    except Exception as e:
        if _Debug:
            print('file %r read failed: %r' % (filename, e, ))
    return u''


def rmdir_recursive(dirpath, ignore_errors=False, pre_callback=None):
    """
    Remove a directory, and all its contents if it is not already empty.

    http://mail.python.org/pipermail/python-
    list/2000-December/060960.html If ``ignore_errors`` is True process
    will continue even if some errors happens. Method ``pre_callback``
    can be used to decide before remove the file.
    """
    counter = 0
    for name in os.listdir(dirpath):
        full_name = os.path.join(dirpath, name)
        # on Windows, if we don't have write permission we can't remove
        # the file/directory either, so turn that on
        if not os.access(full_name, os.W_OK):
            try:
                os.chmod(full_name, 0o600)
            except:
                continue
        if os.path.isdir(full_name):
            counter += rmdir_recursive(full_name, ignore_errors, pre_callback)
        else:
            if pre_callback:
                if not pre_callback(full_name):
                    continue
            if os.path.isfile(full_name):
                if not ignore_errors:
                    os.remove(full_name)
                    counter += 1
                else:
                    try:
                        os.remove(full_name)
                        counter += 1
                    except Exception as exc:
                        if _Debug:
                            print('rmdir_recursive', exc)
                        continue
    if pre_callback:
        if not pre_callback(dirpath):
            return counter
    if not ignore_errors:
        os.rmdir(dirpath)
    else:
        try:
            os.rmdir(dirpath)
        except Exception as exc:
            if _Debug:
                print('rmdir_recursive', exc)
    return counter

#------------------------------------------------------------------------------

class AsynchronousFileReader(threading.Thread):

    def __init__(self, fd, queue, finishing):
        assert isinstance(queue, Queue)
        assert callable(fd.readline)
        threading.Thread.__init__(self)
        self._fd = fd
        self._queue = queue
        self._finishing = finishing

    def run(self):
        for line in iter(self._fd.readline, ''):
            if self._finishing and self._finishing.is_set():
                break
            self._queue.put(line)
            if not line:
                break

    def eof(self):
        return not self.is_alive() and self._queue.empty()


class BackgroundProcess(object):

    def __init__(self, cmd, stdout_callback=None, stderr_callback=None, finishing=None, daemon=False):
        self.cmd = cmd
        self.process = None
        self.stdout_callback = stdout_callback
        self.stderr_callback = stderr_callback
        self.finishing = finishing
        self.daemon = daemon

    def run(self, **kwargs):

        def target(**kwargs):
            self.process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout_queue = Queue()
            stdout_reader = AsynchronousFileReader(self.process.stdout, stdout_queue, self.finishing)
            stdout_reader.start()
            stderr_queue = Queue()
            stderr_reader = AsynchronousFileReader(self.process.stderr, stderr_queue, self.finishing)
            stderr_reader.start()
            empty_line = False
            if _Debug:
                print('BackgroundProcess.run.target start')
            while not stdout_reader.eof() or not stderr_reader.eof():
                if self.finishing and self.finishing.is_set():
                    break
                while not stdout_queue.empty():
                    line = stdout_queue.get()
                    if not line:
                        empty_line = True
                        break
                    if self.stdout_callback:
                        self.stdout_callback(line)
                while not stderr_queue.empty():
                    line = stderr_queue.get()
                    if not line:
                        empty_line = True
                        break
                    if self.stderr_callback:
                        self.stderr_callback(line)
                if empty_line:
                    break
                time.sleep(.2)
            if _Debug:
                print('BackgroundProcess.run.target EOF reached')
            if self.finishing and self.finishing.is_set():
                if _Debug:
                    print('BackgroundProcess.run.target terminating the process because finishing flag is set')
                self.process.terminate()
            else:
                stdout_reader.join()
                stderr_reader.join()
                self.process.stdout.close()
                self.process.stderr.close()
            if _Debug:
                print('BackgroundProcess.run.target finished')

        thread = threading.Thread(target=target, kwargs=kwargs, daemon=self.daemon)
        thread.start()

