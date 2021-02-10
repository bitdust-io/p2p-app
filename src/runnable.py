from jnius import PythonJavaClass, java_method, autoclass  # @UnresolvedImport

#------------------------------------------------------------------------------

PythonActivity = autoclass('org.bitdust_io.bitdust1.BitDustActivity')

#------------------------------------------------------------------------------

class Runnable(PythonJavaClass):

    __javainterfaces__ = ['java/lang/Runnable']
    __runnables__ = []

    def __init__(self, func):
        super(Runnable, self).__init__()
        self.func = func

    def __call__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        Runnable.__runnables__.append(self)
        activity = PythonActivity.mActivity
        activity.runOnUiThread(self)

    @java_method('()V')
    def run(self):
        try:
            self.func(*self.args, **self.kwargs)
        except:
            import traceback
            traceback.print_exc()
        Runnable.__runnables__.remove(self)


def run_on_ui_thread(f):
    def f2(*args, **kwargs):
        Runnable(f)(*args, **kwargs)
    return f2
