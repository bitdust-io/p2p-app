import os
import sys
import time
import subprocess
import threading
import queue

from kivy.app import App
from kivy.metrics import dp
from kivy.config import Config
from kivy.core.window import Window
from kivy.clock import Clock, mainthread
from kivy.lang import Builder

_Debug = True

Config.set('graphics', 'resizable', False)

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
        Window.borderless = True
        root = Builder.load_string("""
BoxLayout:
    pos_hint: {'top': 1}
    spacing: '0dp'
    padding: '0dp'
    orientation: 'vertical'
    size_hint: 1, None
    height: '28dp'

    BoxLayout:
        spacing: '10dp'
        padding: '10dp', '0dp', '0dp', '0dp'
        orientation: 'horizontal'
        size_hint: 1, None
        height: '28dp'

        ProgressBar:
            id: progress
            max: 100
            value: 0
            size_hint_y: None
            height: '28dp'

        ToggleButton:
            id: button_expand
            text: '0%'
            size_hint: None, None
            width: '56dp'
            height: '28dp'
            on_state: app.on_button_expand_state()

    ScrollView:
        id: scroll
        bar_width: '12dp'
        size_hint: 1, None
        height: 0
        opacity: 0
        disabled: True

        TextInput:
            id: content
            size_hint: 1, None
            height: max(self.minimum_height, scroll.height)
            background_color: 0,0,0,1
            foreground_color: 1,1,1,1
            readonly: True

    Button:
        id: button_close
        text: "START"
        pos_hint: {'right': 1}
        size_hint: None, None
        width: '64dp'
        disabled: True
        height: 0
        opacity: 0
        on_release: app.on_button_close()
    """)
        Window.size = (Window.size[0] / dp(1), root.height / dp(1))
        return root

    def collapse(self):
        s = self.root.ids.scroll
        b = self.root.ids.button_close
        e = self.root.ids.button_expand
        self.root.height = dp(28)
        s.height = dp(0)
        s.opacity = 0
        s.disabled = True
        b.height = dp(0)
        b.opacity = 0
        b.disabled = True
        e.state = 'normal'
        Window.size = (Window.size[0] / dp(1), self.root.height / dp(1))

    def expand(self):
        s = self.root.ids.scroll
        b = self.root.ids.button_close
        e = self.root.ids.button_expand
        self.root.height = dp(28+28+300)
        s.height = dp(300)
        s.opacity = 1
        s.disabled = False
        b.height = dp(28)
        b.opacity = 1
        b.disabled = False
        e.state = 'down'
        Window.size = (Window.size[0] / dp(1), self.root.height / dp(1))

    def start_app(self):
        if _Debug:
            print('BitDustP2P_App.start_app sys.executable', sys.executable, os.getcwd())
        install_sh_full_path = os.path.join(os.getcwd(), 'install.sh')
        python_bin_full_path = sys.executable
        git_bin_full_path = os.path.join(os.getcwd(), 'git_scm', 'bin', 'git')
        subprocess.Popen(
            ['/bin/sh', install_sh_full_path, python_bin_full_path, git_bin_full_path, ],
            shell=False,
            close_fds=True,
            universal_newlines=False,
        )

    def on_start(self):
        if _Debug:
            print('BitDustP2P_App.on_start sys.executable', sys.executable, os.getcwd())
        install_sh_full_path = os.path.join(os.getcwd(), 'install.sh')
        python_bin_full_path = sys.executable
        git_bin_full_path = os.path.join(os.getcwd(), 'git_scm', 'bin', 'git')
        self.error = None
        BackgroundProcess(
            # python_bin_full_path + ' -m virtualenv venv',
            # '/bin/sh "%s" "%s" "%s"' % (install_sh_full_path, python_bin_full_path, git_bin_full_path),
            ['/bin/sh', install_sh_full_path, python_bin_full_path, git_bin_full_path, ],
            shell=True,
            finishing=self.finishing,
            daemon=False,
            result_callback=self.on_result,
            stdout_callback=self.on_stdout,
            stderr_callback=self.on_stderr,
        ).run()

    def on_stop(self):
        self.finishing.set()

    @mainthread
    def on_stdout(self, line):
        ln = line.decode()
        if _Debug:
            print('BitDustP2P_App.on_stdout ', ln)
        if ln.startswith('### '):
            self.root.ids.button_expand.text = ln.strip().replace('### ', '')
            self.root.ids.progress.value = int(ln.strip().replace('### ', '').replace('%', ''))
        else:
            self.root.ids.content.text += ln
            self.root.ids.scroll.scroll_y = 0.0

    @mainthread
    def on_stderr(self, line):
        ln = line.decode()
        if _Debug:
            print('BitDustP2P_App.on_stderr ', ln)
        if ln.startswith('### '):
            self.root.ids.button_expand.text = ln.strip().replace('### ', '')
            self.root.ids.progress.value = int(ln.strip().replace('### ', '').replace('%', ''))
        else:
            self.root.ids.content.text += ln
            self.root.ids.scroll.scroll_y = 0.0

    @mainthread
    def on_result(self, ret_code):
        if _Debug:
            print('BitDustP2P_App.on_result', ret_code)
        if not ret_code:
            if self.root.ids.button_expand.state != 'down':
                self.start_app()
                self.stop()
                return
        else:
            self.root.ids.button_close.text = 'EXIT'
            self.root.ids.button_close.disabled = False
            self.expand()

    def on_button_expand_state(self):
        if self.root.ids.button_expand.state == 'down':
            self.expand()
        else:
            self.collapse()
        Window.size = (Window.size[0] / dp(1), self.root.height / dp(1))

    def on_button_close(self):
        if self.root.ids.button_close.text != 'EXIT':
            self.start_app()
        self.stop()


BitDustP2P_App().run()
