import time
import subprocess
import threading
import queue

from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.lang import Builder


_Debug = True


class AsynchronousFileReader(threading.Thread):

    def __init__(self, fd, queue_inst, finishing):
        assert isinstance(queue_inst, queue.Queue)
        assert callable(fd.readline)
        threading.Thread.__init__(self)
        self._fd = fd
        self._queue = queue_inst
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

    def __init__(self, cmd, stdout_callback=None, stderr_callback=None, finishing=None, daemon=False, shell=False, result_callback=None):
        self.cmd = cmd
        self.process = None
        self.stdout_callback = stdout_callback
        self.stderr_callback = stderr_callback
        self.finishing = finishing
        self.daemon = daemon
        self.shell = shell
        self.result_callback = result_callback

    def run(self, **kwargs):

        def target(**kwargs):
            self.process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=self.shell)
            stdout_queue = queue.Queue()
            stdout_reader = AsynchronousFileReader(self.process.stdout, stdout_queue, self.finishing)
            stdout_reader.start()
            stderr_queue = queue.Queue()
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
                time.sleep(.1)
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


class BitDustP2P_App(App):

    finishing = threading.Event()

    def build(self):
        return Builder.load_string("""

BoxLayout:
    id: container
    spacing: 1
    padding: 1
    orientation: 'vertical'

    ScrollView:
        id: scroll
        bar_width: '10dp'

        TextInput:
            id: content
            size_hint: 1, None
            height: max(self.minimum_height, scroll.height)

    Button:
        id: button_close
        text: "Close"
        pos_hint: {'right': 1}
        size_hint: None, None
        width: '70dp'
        height: '28dp'
        disabled: True
    """)

    def on_start(self):
        self.error = None
        BackgroundProcess(
            cmd=['/bin/sh', './installer/osx/deploy.sh', ],
            finishing=self.finishing,
            daemon=True,
            result_callback=self.on_result,
            stdout_callback=self.on_stdout,
            stderr_callback=self.on_stderr,
        ).run()

    def on_stop(self):
        self.finishing.set()

    @mainthread
    def on_stdout(self, line):
        self.root.ids.content.text += line.decode()
        self.root.ids.scroll.scroll_y = 0.0

    @mainthread
    def on_stderr(self, line):
        self.root.ids.content.text += 'ERR:' + line.decode()
        self.root.ids.scroll.scroll_y = 0.0

    @mainthread
    def on_result(self, ret_code):
        if _Debug:
            print('BitDustP2P_App.on_result', ret_code)
        if ret_code:
            self.root.ids.button_close.disabled = False
        else:
            self.stop()

BitDustP2P_App().run()
