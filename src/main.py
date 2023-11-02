#!/usr/bin/env python -u
# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------

import os
import sys
import platform
import threading
import locale
import traceback

#------------------------------------------------------------------------------ 

_Debug = True
_DebugProfilingEnabled = False
_DebugKivyOutputEnabled = True

#------------------------------------------------------------------------------

if _Debug and _DebugKivyOutputEnabled:
    # os.environ["KIVY_NO_CONSOLELOG"] = "0"
    pass
else:
    os.environ["KIVY_NO_CONSOLELOG"] = "1"

#------------------------------------------------------------------------------

if platform.system() == 'Windows':
    sys.stdout = open("stdout.txt", "w")
    sys.stderr = open("stderr.txt", "w")
    os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
    scriptdir, script = os.path.split(os.path.abspath(__file__))
    sys.path.insert(0, scriptdir)
    # here is the assumption for every Windows-based OS : we are running on Python 3.8 or higher
    os.add_dll_directory(scriptdir)  # @UndefinedVariable
else:
    locale.setlocale(locale.LC_CTYPE, 'en_US.UTF-8')

if platform.system() != 'Windows' and 'ANDROID_ARGUMENT' not in os.environ:
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())  # @UndefinedVariable
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())  # @UndefinedVariable

#------------------------------------------------------------------------------

from lib import system

#------------------------------------------------------------------------------

if _Debug:
    print('BitDustApp __file__', os.path.dirname(os.path.abspath(__file__)))
    print('BitDustApp __name__', __name__)
    print('BitDustApp sys.path', sys.path)
    print('BitDustApp os.getcwd()', os.path.abspath(os.getcwd()))
    print('BitDustApp os.listdir()', os.listdir(os.getcwd()))
    print('BitDustApp platform.uname()', platform.uname())

#------------------------------------------------------------------------------

from kivy.config import Config

Config.set('kivy', 'window_icon', 'bitdust.png')

if 'ANDROID_ARGUMENT' not in os.environ:
    Config.set('input', 'mouse', 'mouse,disable_multitouch')

if _Debug:
    Config.set('kivy', 'log_level', 'debug')

from kivy.lang import Builder
from kivy.clock import Clock, mainthread
from kivy.core.window import Window

if _Debug:
    print('BitDustApp Window=%r' % Window)
    print('BitDustApp Window.width=%r Window.height=%r' % (Window.width, Window.height, ))

from kivymd.app import MDApp

#------------------------------------------------------------------------------

from screens import controller

from components import styles
from components import snackbar

#------------------------------------------------------------------------------

if system.is_android():
    from jnius import autoclass, cast  # @UnresolvedImport
    import encodings.idna  # @UnusedImport

    from android import mActivity  # @UnresolvedImport
    from android.config import ACTIVITY_CLASS_NAME, ACTIVITY_CLASS_NAMESPACE  # @UnresolvedImport

    if _Debug:
        print('BitDustApp ACTIVITY_CLASS_NAME=%r' % ACTIVITY_CLASS_NAME)
        print('BitDustApp ACTIVITY_CLASS_NAMESPACE=%r' % ACTIVITY_CLASS_NAMESPACE)

    from android.storage import primary_external_storage_path, app_storage_path  # @UnresolvedImport

    if _Debug:
        print('BitDustApp primary_external_storage_path=%r' % primary_external_storage_path())
        print('BitDustApp app_storage_path=%r' % app_storage_path())

    # from lib.permissions import check_permission, request_permissions  # @UnresolvedImport

    PACKAGE_NAME = u'org.bitdust_io.bitdust1'
    SERVICE_NAME = u'{packagename}.Service{servicename}'.format(
        packagename=PACKAGE_NAME,
        servicename=u'Bitdustnode',
    )

#------------------------------------------------------------------------------

class BitDustApp(styles.AppStyle, MDApp):

    control = None
    main_window = None
    finishing = threading.Event()

    def apply_styles(self):
        from kivy.app import App
        from kivy.core.text import LabelBase
        from kivymd.font_definitions import theme_font_styles
        if _Debug:
            print('BitDustApp.apply_styles   App.get_running_app() : %r' % App.get_running_app())
            print('BitDustApp.apply_styles                    self : %r' % self)

        self.theme_cls.theme_style = 'Light'
        self.theme_cls.primary_palette = 'Blue'
        self.theme_cls.primary_hue = "400"
        self.theme_cls.accent_palette = 'Green'

        fonts_path = './src/fonts'
        if system.is_android():
            fonts_path = os.path.join(os.environ['ANDROID_ARGUMENT'], 'fonts')
        elif system.is_osx():
            fonts_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
        elif system.is_ios():
            fonts_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
        # https://materialdesignicons.com
        LabelBase.register(name="IconMD", fn_regular=os.path.join(fonts_path, "md.ttf"))
        theme_font_styles.append('IconMD')
        self.theme_cls.font_styles["IconMD"] = ["IconMD", 24, False, 0, ]
        # https://fontawesome.com
        LabelBase.register(name="IconFA", fn_regular=os.path.join(fonts_path, "fa-solid.ttf"))
        theme_font_styles.append('IconFA')
        self.theme_cls.font_styles["IconFA"] = ["IconFA", 24, False, 0, ]
        # https://icofont.com
        LabelBase.register(name="IconICO", fn_regular=os.path.join(fonts_path, "icofont.ttf"))
        theme_font_styles.append('IconICO')
        self.theme_cls.font_styles["IconICO"] = ["IconICO", 24, False, 0, ]

        if _Debug:
            print('BitDustApp.apply_styles', self.theme_cls)

    def build(self):
        if _Debug:
            print('BitDustApp.build')
            if system.is_android():
                print('BitDustApp.build   android_sdk_version() : %r' % system.android_sdk_version())
                print('BitDustApp.build   ACTIVITY_CLASS_NAME=%r' % ACTIVITY_CLASS_NAME)
                print('BitDustApp.build   ACTIVITY_CLASS_NAMESPACE=%r' % ACTIVITY_CLASS_NAMESPACE)
                print('BitDustApp.build   mActivity=%r' % mActivity)

        self.title = 'BitDust p2p-app'
        self.icon = './bitdust.png'
        self.granted = False

        self.apply_styles()
        self.init_components()

        self.control = controller.Controller(self)

        from components import main_win
        self.main_window = main_win.MainWin()
        self.root_widget = self.main_window

        self.main_window.register_controller(self.control)
        self.main_window.register_screens(controller.all_screens())
        self.main_window.bind(engine_log=self.on_engine_log)

        Window.bind(on_keyboard=self.on_key_input)

        from kivy.uix.anchorlayout import AnchorLayout
        self.wrapper = AnchorLayout()
        self.wrapper.padding = [0, 0, 0, 0, ]
        self.wrapper.add_widget(self.main_window)
        return self.wrapper

    def init_components(self):
        from components import all_components
        Builder.load_string(all_components.KV_IMPORT)
        if system.is_osx():
            all_components.KV_FILES_BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        for kv_file in all_components.KV_FILES:
            Builder.load_file(all_components.KV_FILES_BASE + '/' + kv_file)

    @mainthread
    def do_start(self, *args, **kwargs):
        if _Debug:
            print('BitDustApp.do_start', args, kwargs)
        self.dont_gc = None
        if not system.is_android():
            self.control.start()
            self.start_engine()
            return True
        self.granted = args[0]
        if not self.granted:
            mActivity.finishAndRemoveTask()
            return False
        try:
            self.control.start()
            self.start_engine()
        except:
            if _Debug:
                traceback.print_exc()
            mActivity.finishAndRemoveTask()
            return False
        return True

    def get_service_name(self):
        context =  mActivity.getApplicationContext()
        return str(context.getPackageName()) + '.Service' + 'Bitdustnode'

    def service_is_running(self):
        service_name = self.get_service_name()
        if _Debug:
            print('BitDustApp.service_is_running', service_name)
        try:
            context =  mActivity.getApplicationContext()
        except:
            if _Debug:
                traceback.print_exc()
        sys_service = mActivity.getSystemService(context.ACTIVITY_SERVICE)
        manager = cast('android.app.ActivityManager', sys_service)
        try:
            lst = manager.getRunningServices(100)
        except:
            if _Debug:
                traceback.print_exc()
        for service in lst:
            if service.service.getClassName() == service_name:
                if _Debug:
                    print('BitDustApp.service_is_running is True')
                return True
        if _Debug:
            print('BitDustApp.service_is_running is False')
        return False

    def start_service_if_not_running(self):
        if _Debug:
            print('BitDustApp.start_service_if_not_running', self.get_service_name())
        if self.service_is_running():
            return
        svc = autoclass(self.get_service_name())
        if _Debug:
            print('BitDustApp.start_service_if_not_running service', svc)
        svc.start(mActivity, 'bitdust.png', 'BitDust Service', 'Started', '')

    def start_engine(self, after_restart=False):
        if self.main_window.engine_is_on:
            if _Debug:
                print('BitDustApp.start_engine SKIP')
            return False
        if _Debug:
            print('BitDustApp.start_engine, after_restart=%r' % after_restart)
        self.main_window.engine_is_on = True
        self.main_window.state_process_health = 0
        if system.is_android():
            self.start_android_service()
        else:
            self.check_restart_bitdust_process()
        return True

    def restart_engine(self):
        if not self.main_window.engine_is_on:
            if _Debug:
                print('BitDustApp.restart_engine SKIP')
            return
        if _Debug:
            print('BitDustApp.restart_engine')
        self.main_window.state_process_health = 0
        if system.is_android():
            self.stop_android_service()
            Clock.schedule_once(lambda x: self.start_android_service(), .5)
        else:
            self.check_restart_bitdust_process(params=['restart', ])

    def redeploy_engine(self):
        if system.is_android():
            if _Debug:
                print('BitDustApp.redeploy_engine NOT IMPLEMENTED')
            return
        if _Debug:
            print('BitDustApp.redeploy_engine')
        self.stop_engine()
        self.check_restart_bitdust_process(params=['redeploy', ])

    def stop_engine(self):
        if not self.main_window.engine_is_on:
            if _Debug:
                print('BitDustApp.stop_engine SKIP')
            return
        if _Debug:
            print('BitDustApp.stop_engine')
        self.main_window.engine_is_on = False
        self.main_window.state_process_health = -1
        if system.is_android():
            self.stop_android_service()
        else:
            self.check_restart_bitdust_process(params=['stop', ])

    def start_android_service(self, shutdown=False):
        if not system.is_android():
            return False
        if _Debug:
            print('BitDustApp.start_android_service app data path is %r' % system.get_app_data_path())
        try:
            if self.main_window.is_screen_active('welcome_screen'):
                welcome_screen = self.main_window.get_active_screen('welcome_screen')
                if welcome_screen:
                    welcome_screen.populate(start_engine=True)
            self.main_window.engine_log = '\n'
            self.start_service_if_not_running()
        except:
            if _Debug:
                traceback.print_exc()
            return False
        return True

    def stop_android_service(self):
        if not system.is_android():
            return False
        if _Debug:
            print('BitDustApp.stop_service')
        self.main_window.engine_log = '\n'
        self.control.send_process_stop()
        if _Debug:
            print('BitDustApp.stop_service about to STOP')
        return True

    def check_restart_bitdust_process(self, params=[]):
        if not system.is_linux() and not system.is_osx() and not system.is_windows():
            if _Debug:
                print('BitDustApp.check_restart_bitdust_process NOT IMPLEMENTED')
            return None
        if _Debug:
            print('BitDustApp.check_restart_bitdust_process params=%r' % params)
        Clock.schedule_once(lambda *a: self.do_begin_deploy_process(params=params))

    def do_begin_deploy_process(self, params=[]):
        if _Debug:
            print('BitDustApp.do_begin_deploy_process params=%r finishing=%r' % (params, self.finishing.is_set(), ))
        if self.finishing.is_set():
            return
        if self.main_window.is_screen_active('welcome_screen'):
            welcome_screen = self.main_window.get_active_screen('welcome_screen')
            if welcome_screen:
                welcome_screen.populate(start_engine=True)
        self.main_window.engine_log = '\n'
        if not params and self.control.is_web_socket_ready():
            if _Debug:
                print('BitDustApp.do_begin_deploy_process SKIP because web socket already ready')
            return
        if system.is_linux():
            system.BackgroundProcess(
                cmd=['/bin/bash', './src/deploy/linux.sh', ] + params,
                stdout_callback=self.on_deploy_process_stdout,
                stderr_callback=self.on_deploy_process_stderr,
                finishing=self.finishing,
                daemon=True,
                result_callback=self.on_deploy_process_result,
            ).run()
        elif system.is_osx():
            system.BackgroundProcess(
                cmd=['/bin/bash', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'deploy', 'osx.sh'), ] + params,
                stdout_callback=self.on_deploy_process_stdout,
                stderr_callback=self.on_deploy_process_stderr,
                finishing=self.finishing,
                daemon=True,
                result_callback=self.on_deploy_process_result,
            ).run()
        elif system.is_windows():
            system.BackgroundProcess(
                cmd=['src\\deploy\\windows.bat', ] + params,
                stdout_callback=self.on_deploy_process_stdout,
                stderr_callback=self.on_deploy_process_stderr,
                finishing=self.finishing,
                daemon=True,
                shell=True,
                result_callback=self.on_deploy_process_result,
            ).run()

    @mainthread
    def on_deploy_process_stdout(self, line):
        if _Debug:
            print('DEPLOY OUT:', line.decode().rstrip())
        if line.decode().startswith('#####'):
            self.main_window.engine_log += line.decode()[6:]

    @mainthread
    def on_deploy_process_stderr(self, line):
        if _Debug:
            print('DEPLOY ERR:', line.decode().rstrip())

    @mainthread
    def on_deploy_process_result(self, retcode):
        if _Debug:
            print('BitDustApp.on_deploy_process_result', retcode)
        if retcode == 2:
            pth = os.path.join(os.path.expanduser('~'), '.bitdust', 'install.log')
            snackbar.error(text='installation failed, see %s file for details' % pth)

    def on_start(self):
        if _Debug:
            print('BitDustApp.on_start')
            if _DebugProfilingEnabled:
                import cProfile
                self.profile = cProfile.Profile()
                self.profile.enable()
        if not system.is_android():
            return self.do_start(True)
        if _Debug:
            print('BitDustApp.on_start about to verify android permissions')
        from lib.android_permissions import AndroidPermissions
        from android.permissions import Permission  # @UnresolvedImport
        permissions = []
        if system.android_sdk_version() >= 33:
            permissions = [
                Permission.POST_NOTIFICATIONS,
                Permission.READ_MEDIA_AUDIO,
                Permission.READ_MEDIA_IMAGES,
                Permission.READ_MEDIA_VIDEO,
            ]
        self.dont_gc = AndroidPermissions(
            callback=self.do_start,
            permissions=permissions,
        )
        return True

    def on_stop(self):
        if _Debug:
            print('BitDustApp.on_stop')
        self.finishing.set()
        self.control.stop()
        self.main_window.unregister_controller()
        self.main_window.unregister_screens()

    def on_pause(self):
        if _Debug:
            print('BitDustApp.on_pause')
            if _DebugProfilingEnabled:
                self.profile.disable()
                if system.is_android():
                    pass
                else:
                    self.profile.dump_stats('./debug.profile')
        return True

    def on_resume(self):
        if _Debug:
            print('BitDustApp.on_resume')
        self.control.verify_process_health()
        self.control.verify_identity_get()
        self.control.verify_network_connected()
        self.control.send_request_model_data('service')

#     def on_dropdown_menu_callback(self, instance_menu, instance_menu_item):
#         if _Debug:
#             print('BitDustApp.on_dropdown_menu_callback', instance_menu, instance_menu_item.text)
#         instance_menu.dismiss()
#         if self.main_window.selected_screen:
#             self.main_window.active_screens[self.main_window.selected_screen][0].on_dropdown_menu_item_clicked(
#                 instance_menu, instance_menu_item
#             )

    def on_key_input(self, window_obj, key_code, scancode, codepoint, modifier):
        if _Debug:
            print('BitDustApp.on_key_input', key_code, scancode, modifier)
        if key_code in [27, ]:
            ret = self.main_window.on_system_back_button_clicked()
            return ret
        if key_code in [13, ] and 'ctrl' in modifier and len(modifier) == 1:
            if self.main_window.selected_screen.count('private_chat_') or self.main_window.selected_screen.count('group_'):
                active_scr = self.main_window.get_active_screen(self.main_window.selected_screen)
                if active_scr:
                    active_scr.on_hot_button_clicked()
                    return True
        return False

    # def on_height(self, instance, value):
    #     if _Debug:
    #         print ('BitDustApp.on_height', instance, value, Window.keyboard_height)

    def on_engine_log(self, instance, value):
        if 'engine_status_screen' in self.main_window.active_screens:
            self.main_window.active_screens['engine_status_screen'][0].ids.deploy_output_label.text = value

#------------------------------------------------------------------------------

def main():
    if _Debug:
        print('BitDustApp.main   process is starting')
    BitDustApp().run()
    if _Debug:
        print('BitDustApp.main   process is finishing')

#------------------------------------------------------------------------------

if __name__ == '__main__':
    main()
    if _Debug:
        import threading
        for thread in threading.enumerate():
            print(thread.name, thread)
