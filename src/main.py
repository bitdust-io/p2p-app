import os

#------------------------------------------------------------------------------

from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import BooleanProperty  # @UnresolvedImport

#------------------------------------------------------------------------------

from lib.system import is_android

from screens import controller

#------------------------------------------------------------------------------

if is_android(): 
    from jnius import autoclass  # @UnresolvedImport
    from android.permissions import request_permissions, Permission  # @UnresolvedImport
    import encodings.idna

#------------------------------------------------------------------------------ 

_Debug = True

#------------------------------------------------------------------------------

# os.environ['KIVY_METRICS_DENSITY'] = '1'
# os.environ['KIVY_METRICS_FONTSCALE'] = '1'

#------------------------------------------------------------------------------

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')  # disable multi-touch
Config.set('graphics', 'resizable', True)
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '740')

#------------------------------------------------------------------------------

Builder.load_string("""
#:import NoTransition kivy.uix.screenmanager.NoTransition
#:import Window kivy.core.window.Window
#:import fa_icon components.webfont.fa_icon
""")

#------------------------------------------------------------------------------

if is_android():
    PACKAGE_NAME = 'org.bitdust_io.bitdust_p2p'
    SERVICE_NAME = '{packagename}.Service{servicename}'.format(
        packagename=PACKAGE_NAME,
        servicename='Bitdustnode'
    )
    APP_STARTUP_PERMISSIONS = [
        Permission.INTERNET,
        Permission.READ_EXTERNAL_STORAGE,
        Permission.WRITE_EXTERNAL_STORAGE,
        Permission.FOREGROUND_SERVICE,
    ]
    PythonActivity = autoclass('org.bitdust_io.bitdust_p2p.BitDustActivity')

#------------------------------------------------------------------------------

class BitDustApp(App):

    control = None
    main_window = None

    def build(self):
        if _Debug:
            print('BitDustApp.build')
        from components import styles
        from components import layouts
        from components import labels
        from components import buttons
        from components import text_input
        from components import list_view
        from components import navigation
        from components import main_window
        styles.init(self)
        self.control = controller.Controller(self)
        self.main_window = main_window.MainWindow()
        return self.main_window

    def on_start(self):
        if _Debug:
            print('BitDustApp.on_start')
        self.main_window.register_screens(controller.all_screens())
        self.main_window.register_controller(self.control)
        self.main_window.select_screen('process_dead_screen')
        self.control.start()
        if is_android():
            self.start_android_service()
        else:
            self.check_restart_bitdust_engine()

    def on_stop(self):
        if _Debug:
            print('BitDustApp.on_stop')
        self.control.stop()
        self.main_window.unregister_controller()
        self.main_window.unregister_screens()
        # TODO: check if we need to stop BitDust engine after App closes
        if is_android():
            pass
        else:
            pass

    def on_pause(self):
        if _Debug:
            print('BitDustApp.on_pause')
        return True

    def on_resume(self):
        if _Debug:
            print('BitDustApp.on_resume')

    def start_service(self, finishing=False):
        if _Debug:
            print('BitDustApp.start_service finishing=%r' % finishing)
        service = autoclass(SERVICE_NAME)
        mActivity = PythonActivity.mActivity
        argument = ''
        if finishing:
            argument = '{"stop_service": 1}'
        service.start(mActivity, argument)
        if _Debug:
            print('OK')
        if finishing:
            self.service = None
            if _Debug:
                print('service expect to be STOPPED now')
        else:
            self.service = service
            if _Debug:
                print('service STARTED : %r' % self.service)

    def stop_service(self):
        if _Debug:
            print('BitDustApp.stop_service %r' % self.service)
        service = autoclass(SERVICE_NAME)
        service.stop(PythonActivity.mActivity)
        self.start_service(finishing=True)
        if _Debug:
            print('BitDustApp.stop_service STOPPED')

    def request_app_permissions(self, list_permissions=[]):
        global APP_STARTUP_PERMISSIONS
        if _Debug:
            print('BitDustApp.request_app_permissions', list_permissions or APP_STARTUP_PERMISSIONS)
        ret = request_permissions(list_permissions or APP_STARTUP_PERMISSIONS)
        if _Debug:
            print('request_permissions result : %r' % ret)

#------------------------------------------------------------------------------

if __name__ == '__main__':
    BitDustApp().run()
