import os
import subprocess
import time
import platformdirs
import threading
from queue import Queue

#------------------------------------------------------------------------------

from kivy.utils import platform  # @UnresolvedImport

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

from lib import strng

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


def is_mobile():
    return is_android() or is_ios()

#------------------------------------------------------------------------------

def get_app_data_path():
    """
    A portable method to get the default data folder location, usually it is: "~/.bitdust/"
    """
    if is_windows():
        return os.path.join(os.path.expanduser('~'), '.bitdust')

    elif is_linux():
        return os.path.join(os.path.expanduser('~'), '.bitdust')

    elif is_android():
        from android.storage import app_storage_path  # @UnresolvedImport
        return os.path.join(app_storage_path(), '.bitdust')

    elif is_osx():
        return os.path.join(os.path.expanduser('~'), '.bitdust')

    elif is_ios():
        return os.path.join(os.path.expanduser('~'), 'Documents', '.bitdust')

    return os.path.join(os.path.expanduser('~'), '.bitdust')


def get_downloads_dir():
    if is_android():
        from android.storage import app_storage_path  # @UnresolvedImport
        downloads_dir = os.path.join(app_storage_path(), 'downloads')
        if not os.path.exists(downloads_dir):
            os.makedirs(downloads_dir)
        return downloads_dir
    if is_ios():
        return os.path.join(os.path.expanduser('~'), 'Documents')
    return platformdirs.user_downloads_dir()


def get_documents_dir():
    if is_android():
        from android.storage import app_storage_path  # @UnresolvedImport
        documents_dir = os.path.join(app_storage_path(), 'documents')
        if not os.path.exists(documents_dir):
            os.makedirs(documents_dir)
        return documents_dir
    if is_ios():
        return os.path.join(os.path.expanduser('~'), 'Documents')
    return platformdirs.user_documents_dir()

#------------------------------------------------------------------------------

def android_sdk_version():
    global _LatestAndroidSDKVersion
    if not is_android():
        return None
    if _LatestAndroidSDKVersion is not None:
        return _LatestAndroidSDKVersion
    from android import api_version  # @UnresolvedImport
    _LatestAndroidSDKVersion = api_version
    return _LatestAndroidSDKVersion


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
        _LatestAndroidBitDustActivity = autoclass(ACTIVITY_CLASS_NAME).mActivity
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
    if _LatestAndroidDisplayDefaultHeight > 1800:
        if keyboard_height >= 41:
            if _Debug:
                print('system.get_android_keyboard_height keyboard_height=%d going to be decreased and _LatestAndroidDisplayDefaultHeight=%d' % (
                    keyboard_height, _LatestAndroidDisplayDefaultHeight, ))
            keyboard_height -= 41
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
        _LatestAndroidBitDustActivity = autoclass(ACTIVITY_CLASS_NAME).mActivity
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

def WriteTextFile(filepath, data):
    """
    A smart way to write data into text file. Return True if success.
    This should be atomic operation - data is written to another temporary file and than renamed.
    """
    temp_path = filepath + '.tmp'
    if os.path.exists(temp_path):
        if not os.access(temp_path, os.W_OK):
            return False
    if os.path.exists(filepath):
        if not os.access(filepath, os.W_OK):
            return False
        try:
            os.remove(filepath)
        except Exception as e:
            if _Debug:
                print('file %r write failed: %r' % (filepath, e, ))
            return False
    fout = open(temp_path, 'wt', encoding='utf-8')
    text_data = strng.to_text(data)
    fout.write(text_data)
    fout.flush()
    os.fsync(fout)
    fout.close()
    try:
        os.rename(temp_path, filepath)
    except Exception as e:
        if _Debug:
            print('file %r write failed: %r' % (filepath, e, ))
        return False
    return True


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

#------------------------------------------------------------------------------

def WriteBinaryFile(filename, data):
    """
    A smart way to write data to binary file. Return True if success.
    """
    try:
        f = open(filename, 'wb')
        f.write(data)
        f.flush()
        # from http://docs.python.org/library/os.html on os.fsync
        os.fsync(f.fileno())
        f.close()
    except Exception as e:
        if _Debug:
            print('file %r write failed: %r' % (filename, e, ))
        try:
            # make sure file gets closed
            f.close()
        except:
            pass
        return False
    return True


def ReadBinaryFile(filename, decode_encoding=None):
    """
    A smart way to read binary file. Return empty string in case of:

    - path not exist
    - process got no read access to the file
    - some read error happens
    - file is really empty
    """
    if not filename:
        return b''
    if not os.path.isfile(filename):
        return b''
    if not os.access(filename, os.R_OK):
        return b''
    try:
        infile = open(filename, mode='rb')
        data = infile.read()
        if decode_encoding is not None:
            data = data.decode(decode_encoding)
        infile.close()
        return data
    except Exception as e:
        if _Debug:
            print('file %r read failed: %r' % (filename, e, ))
    return b''

#------------------------------------------------------------------------------

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

    def __init__(self, cmd, stdout_callback=None, stderr_callback=None, finishing=None, daemon=False, shell=False, cwd=None, result_callback=None):
        self.cmd = cmd
        self.process = None
        self.stdout_callback = stdout_callback
        self.stderr_callback = stderr_callback
        self.finishing = finishing
        self.daemon = daemon
        self.shell = shell
        self.cwd = cwd
        self.result_callback = result_callback

    def run(self, **kwargs):

        def target(**kwargs):
            self.process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=self.shell, cwd=self.cwd)
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
                print('BackgroundProcess.run.target EOF reached finishing=%r' % self.finishing)
            if self.finishing and self.finishing.is_set():
                if _Debug:
                    print('BackgroundProcess.run.target terminating the process because finishing flag is set')
                self.process.terminate()
            else:
                stdout_reader.join()
                stderr_reader.join()
                self.process.stdout.close()
                self.process.stderr.close()
            rc = self.process.wait()
            if _Debug:
                print('BackgroundProcess.run.target finished rc=%r' % rc)
            if self.result_callback:
                self.result_callback(rc)

        thread = threading.Thread(target=target, kwargs=kwargs, daemon=self.daemon)
        thread.start()

#------------------------------------------------------------------------------

def float2str(float_value, mask='%6.8f', no_trailing_zeros=True):
    """
    Some smart method to do simple operation - convert float value into string.
    """
    try:
        f = float(float_value)
    except:
        return float_value
    s = mask % f
    if no_trailing_zeros:
        s = s.rstrip('0').rstrip('.')
    return s


def percent2string(percent, precis=3):
    """
    A tool to make a string (with % at the end) from given float, ``precis`` is
    precision to round the number.
    """
    s = float2str(round(percent, precis), mask=("%%3.%df" % (precis + 2)))
    return s + '%'


def get_nice_size(size_bytes):
    if strng.is_text(size_bytes):
        return size_bytes
    sz = float(size_bytes)
    for unit in ('B', 'KB', 'MB', 'GB', 'TB'):
        if sz < 1024.0:
            if sz < 100.0:
                return '%1.1f %s' % (sz, unit)
            return '%1.0f %s' % (sz, unit)
        sz /= 1024.0
    if sz < 100.0:
        return '%1.1f %s' % (sz, 'TB')
    return '%1.0f %s' % (sz, 'TB')


def make_nice_file_condition(file_info):
    versions = file_info.get('versions', 1)
    return '{}{}/{}'.format(
        '' if versions <= 1 else 'X{} '.format(versions),
        file_info.get('delivered', '0%'),
        file_info.get('reliable', '0%'),
    )

#------------------------------------------------------------------------------

def open_url(url):
    if _Debug:
        print('system.open_url', url)
    try:
        if is_ios():
            from pyobjus import autoclass, objc_str  # @UnresolvedImport
            from pyobjus.dylib_manager import load_framework  # @UnresolvedImport
            load_framework('/System/Library/Frameworks/UIKit.framework')
            UIApplication = autoclass("UIApplication")
            NSURL = autoclass("NSURL")
            NSDictionary = autoclass("NSDictionary")
            app = UIApplication.sharedApplication()
            ns_url = NSURL.URLWithString_(objc_str(url))
            options = NSDictionary.dictionary()  # Proper empty NSDictionary
            if ns_url and app:
                app.openURL_options_completionHandler_(ns_url, options, None)
            else:
                if _Debug:
                    print("system.open_url Invalid URL or UIApplication instance: %r" % url)
        else:
            import webbrowser
            webbrowser.open(url)
    except Exception as exc:
        if _Debug:
            print('system.open_url %r : %r' % (url, exc, ))
        return False
    return True


def open_path_in_os(filepath):
    """
    A portable way to open location or file on local disk with a default OS method.
    """
    if _Debug:
        print('system.open_path_in_os', filepath)
    try:
        if is_windows():
            if os.path.isfile(filepath):
                subprocess.Popen(['explorer', '/select,', '%s' % (filepath.replace('/', '\\'))])
                return True
            subprocess.Popen(['explorer', '%s' % (filepath.replace('/', '\\'))])
            return True

        elif is_linux():
            subprocess.Popen(['xdg-open', filepath])
            return True

        elif is_osx():
            subprocess.Popen(['open', '-R', filepath])
            return True

        elif is_android():
            from lib.sharesheet import ShareSheet
            ShareSheet().view_file(filepath)
            return True

        elif is_ios():
            from pyobjus import autoclass, objc_str  # @UnresolvedImport
            from pyobjus.dylib_manager import load_framework  # @UnresolvedImport
            load_framework('/System/Library/Frameworks/UIKit.framework')
            UIApplication = autoclass("UIApplication")
            NSURL = autoclass("NSURL")
            NSDictionary = autoclass("NSDictionary")
            app = UIApplication.sharedApplication()
            ns_url = NSURL.URLWithString_(objc_str('shareddocuments://'+filepath))
            options = NSDictionary.dictionary()  # Proper empty NSDictionary
            if ns_url and app:
                app.openURL_options_completionHandler_(ns_url, options, None)
            else:
                if _Debug:
                    print("system.open_path_in_os Invalid URL or UIApplication instance: %r" % filepath)

    except Exception as exc:
        if _Debug:
            print('system.open_path_in_os %r : %r' % (filepath, exc, ))
        return False
    try:
        import webbrowser
        webbrowser.open(filepath)
        return True
    except Exception as e:
        print('file %r failed to open with default OS method: %r' % (filepath, e, ))
    return False


def share_dialog(title: str, text: str) -> None:
    """Opens the native dialog 'Share with...'."""
    # if platform == "android":
    #     PythonActivity = autoclass("org.kivy.android.PythonActivity")
    #     Intent = autoclass("android.content.Intent")
    #     String = autoclass("java.lang.String")
    #
    #     intent = Intent()
    #     intent.setAction(Intent.ACTION_SEND)
    #     intent.putExtra(Intent.EXTRA_TEXT, String("{}".format(text)))
    #     intent.setType("text/plain")
    #     chooser = Intent.createChooser(intent, String(title))
    #     PythonActivity.mActivity.startActivity(chooser)
    # elif platform == "ios":
    #     load_framework("/System/Library/Frameworks/UIKit.framework")
    #
    #     UIApplication = autoclass("UIApplication")
    #     NSString = autoclass("NSString")
    #     UIActivityViewController = autoclass("UIActivityViewController")
    #
    #     share_str = NSString.stringWithUTF8String_(text)
    #     uiActivityViewController = UIActivityViewController.alloc().init()
    #     activityViewController = (
    #         uiActivityViewController.initWithActivityItems_applicationActivities_(
    #             [share_str], None
    #         )
    #     )
    #     UIcontroller = UIApplication.sharedApplication().keyWindow.rootViewController()
    #     UIcontroller.presentViewController_animated_completion_(
    #         activityViewController, True, None
    #     )


#------------------------------------------------------------------------------

class UnbufferedStream(object):

    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        try:
            self.stream.write(data)
        except:
            pass
        self.stream.flush()

    def writelines(self, datas):
        try:
            self.stream.writelines(datas)
        except:
            pass
        self.stream.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)
