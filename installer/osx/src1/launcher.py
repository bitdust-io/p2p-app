import sys
import subprocess
import tkinter
import time
import threading
import queue
import json

_Debug = True

class GUI:
    def __init__(self, root, queue, endCommand, title=None, button=None):
        self.queue = queue
        if title:
            root.title(title)
        F1 = tkinter.Frame(root)
        F1.pack(fill=tkinter.BOTH, expand=1)
        S = tkinter.Scrollbar(F1)
        T = tkinter.Text(F1, height=20, width=80)
        S.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        T.pack(side=tkinter.LEFT, fill=tkinter.Y)
        S.config(command=T.yview)
        T.config(yscrollcommand=S.set)
        self.text = T
        self.button = None
        if button:
            F2 = tkinter.Frame(root)
            F2.pack(fill=tkinter.BOTH, expand=0)
            self.button = tkinter.Button(F2, text=button, command=root.destroy, state="disabled")
            self.button.pack(side=tkinter.RIGHT)

    def processIncoming(self):
        while self.queue.qsize():
            try:
                msg = self.queue.get(0)
                if _Debug:
                    try:
                        print(msg.rstrip())
                    except:
                        pass
                self.text.insert(tkinter.END, msg)
                self.text.see(tkinter.END)
            except queue.Empty:
                pass

class ThreadedClient:

    def __init__(self, master, cmd, shell=False, title=None, button=None):
        self.cmd = cmd
        self.shell = shell
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW", self.endApplication)
        self.queue = queue.Queue()
        self.gui = GUI(master, self.queue, self.endApplication, title=title, button=button)
        self.running = 1
        self.completed = 0
        self.thread1 = threading.Thread(target=self.workerThread1)
        self.thread1.start()
        self.periodicCall()

    def periodicCall(self):
        self.gui.processIncoming()
        if not self.running:
            import sys
            sys.exit(1)
        if self.completed:
            if self.gui.button:
                self.gui.button['state'] = 'normal'
        self.master.after(100, self.periodicCall)

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

    def endApplication(self):
        self.running = 0

inp = json.loads(sys.argv[1])
_Debug = inp.get('debug', False)

root = tkinter.Tk()
client = ThreadedClient(
    master=root,
    cmd=inp['cmd'],
    shell=inp.get('shell', False),
    title=inp.get('title'),
    button=inp.get('button'),
)
root.mainloop()
