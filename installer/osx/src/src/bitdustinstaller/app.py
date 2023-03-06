import os
import time
import json
import threading
import queue
import subprocess

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER, LEFT
from toga_gtk.libs import gtk

_Debug = True

INP = {}

class bitdustinstaller(toga.App):

    def _create_impl(self):
        factory_app = self.factory.App
        factory_app.create_menus = lambda _: None
        return factory_app(interface=self)

    def startup(self):
        global INP
        self.cmd = INP.get('cmd')
        self.shell = INP.get('shell', False)
        self.running = 0
        self.completed = 0
        self.scrolled = 0
        self.error = None
        self.queue = queue.Queue()
        self.main_box = toga.Box(style=Pack(direction=COLUMN, flex=0))
        self.container = toga.ScrollContainer(content=self.main_box, horizontal=False, vertical=True)
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = self.container
        self.main_window.show()
        if self.cmd:
            self.thread = threading.Thread(target=self.workerThread1)
            self.running = 1
            self.thread.start()
        self._impl.loop.call_later(0.2, self.periodicCall)

    def periodicCall(self):
        a = None
        try:
            a = self.container._impl.native.get_vadjustment()
            cur_v = a.get_value()
            max_v = a.get_upper() - a.get_page_size()
        except:
            cur_v = 0
            max_v = 0
        if _Debug:
            print('periodicCall', time.time(), cur_v, max_v)
        while self.queue.qsize():
            try:
                msg = self.queue.get(0)
                if _Debug:
                    try:
                        print(msg.rstrip())
                    except:
                        pass
                self.main_box.add(toga.Label(msg.rstrip(), style=Pack(text_align=LEFT, flex=0)))
                # if _Debug:
                #     print(
                #         'periodicCall',
                #         time.time(),
                #         self.container._impl.native.get_vadjustment().get_value(),
                #         self.container._impl.native.get_vadjustment().get_upper()-
                #         self.container._impl.native.get_vadjustment().get_page_size(),
                #     )
                # print('v', v)
                # self.container._impl.native.get_vadjustment().value = v
            except queue.Empty:
                pass
        if not self.scrolled:
            if not self.running:
                if max_v > cur_v:
                    try:
                        a.configure(max_v, a.get_lower(), a.get_upper(), a.get_step_increment(), a.get_page_increment(), a.get_page_size())
                    except:
                        pass
                    self.scrolled = 1
        if not self.running:
            # self.exit()
            return
        # if self.completed:
        #     if not self.error:
        #         self.exit()
        #         return
        self._impl.loop.call_later(0.2, self.periodicCall)
        if self.completed:
            self.running = 0

    def workerThread1(self):
        process = subprocess.Popen(
            self.cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=self.shell,
            encoding='utf-8',
            errors='replace',
        )
        count = 0
        while True:
            if not self.running:
                break
            line = process.stdout.readline()
            if line == '' and process.poll() is not None:
                break
            if line:
                self.queue.put(line)
                count += 1
                if count % 100 == 1:
                    time.sleep(0.05)
        self.completed = 1


def main():
    global INP
    if os.environ.get('INP'):
        INP = json.loads(os.environ['INP'])
    return bitdustinstaller()
