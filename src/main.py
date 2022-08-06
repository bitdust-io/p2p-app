#!/usr/bin/env python -u
# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------

import os
import sys
import threading

#------------------------------------------------------------------------------

import locale
locale.setlocale(locale.LC_CTYPE, 'en_US.UTF-8')

if 'ANDROID_ARGUMENT' not in os.environ:
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

#------------------------------------------------------------------------------ 

_Debug = True
_DebugProfilingEnabled = False

#------------------------------------------------------------------------------

if _Debug:
    print('BitDustApp __file__', os.path.dirname(os.path.abspath(__file__)))
    print('BitDustApp os.getcwd', os.path.abspath(os.getcwd()))
    print('BitDustApp sys.path', sys.path)
    print('BitDustApp os.listdir', os.listdir(os.getcwd()))

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

from kivymd.app import MDApp

#------------------------------------------------------------------------------

from lib import system

from screens import controller

from components import styles
from components import snackbar

#------------------------------------------------------------------------------

if system.is_android(): 
    from jnius import autoclass  # @UnresolvedImport
    import encodings.idna  # @UnusedImport

    from android.config import ACTIVITY_CLASS_NAME, ACTIVITY_CLASS_NAMESPACE  # @UnresolvedImport

    from android import activity  # @UnresolvedImport
    activity._activity = autoclass(ACTIVITY_CLASS_NAME).mBitDustActivity

    from android.storage import primary_external_storage_path, app_storage_path  # @UnresolvedImport

    from lib.permissions import check_permission, request_permissions  # @UnresolvedImport

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
                from android.activity import _activity  # @UnresolvedImport
                from android import mActivity  # @UnresolvedImport
                print('BitDustApp.build   _activity=%r' % _activity)
                print('BitDustApp.build   mActivity=%r' % mActivity)

        self.title = 'BitDust'
        self.icon = './bitdust.png'

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
        for kv_file in all_components.KV_FILES:
            Builder.load_file(kv_file)

    def do_start(self, *args, **kwargs):
        if _Debug:
            print('BitDustApp.do_start', args, kwargs)

        if system.is_android():
            if args:
                if len(args) >= 2:
                    if args[1] and isinstance(args[1], list):
                        if False in args[1]:
                            if _Debug:
                                print('BitDustApp.do_start   FAILED : some of the requested permissions was not granted', args)
                            return False
            if _Debug:
                print('BitDustApp.do_start   is okay to start now')
                print('    primary_external_storage_path is %r' % primary_external_storage_path())
                print('    app_storage_path is %r' % app_storage_path())

        self.control.start()
        self.start_engine()
        return True

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
            return None
        if _Debug:
            print('BitDustApp.start_android_service ACTIVITY_CLASS_NAME=%r SERVICE_NAME=%r shutdown=%r' % (
                ACTIVITY_CLASS_NAME, SERVICE_NAME, shutdown, ))
        if _Debug:
            print('BitDustApp.start_android_service app data path is %r' % system.get_app_data_path())
        if os.path.isdir('/storage/emulated/0/.bitdust'):
            try:
                os.rename('/storage/emulated/0/.bitdust', '/storage/emulated/0/Android/data/org.bitdust_io.bitdust1/files/Documents/.bitdust')
            except Exception as e:
                print('Failed to move data folder from legacy location:', e)
        if self.main_window.is_screen_active('welcome_screen'):
            welcome_screen = self.main_window.get_active_screen('welcome_screen')
            if welcome_screen:
                welcome_screen.populate(start_engine=True)
        self.main_window.engine_log = '\n'
        service = autoclass(SERVICE_NAME)
        if _Debug:
            print('BitDustApp.start_android_service service=%r' % service)
        activity = autoclass(ACTIVITY_CLASS_NAME).mBitDustActivity
        if _Debug:
            print('BitDustApp.start_android_service activity=%r' % activity)
        argument = ''
        if shutdown:
            argument = '{"stop_service": 1}'
        service.start(activity, argument)
        if shutdown:
            if _Debug:
                print('BitDustApp.start_android_service service expect to be STOPPED now')
        else:
            if _Debug:
                print('BitDustApp.start_android_service service STARTED : %r' % service)
        return service

    def stop_android_service(self):
        if not system.is_android():
            return None
        if _Debug:
            print('BitDustApp.stop_service')
        service = autoclass(SERVICE_NAME)
        activity = autoclass(ACTIVITY_CLASS_NAME).mBitDustActivity
        service.stop(activity)
        self.main_window.engine_log = '\n'
        if _Debug:
            print('BitDustApp.stop_service STOPPED')
        return service

    def check_restart_bitdust_process(self, params=[]):
        if not system.is_linux() and not system.is_osx():
            if _Debug:
                print('BitDustApp.check_restart_bitdust_process NOT IMPLEMENTED')
            return None
        if _Debug:
            print('BitDustApp.check_restart_bitdust_process')
        Clock.schedule_once(lambda *a: self.do_start_deploy_process(params=params))

    def do_start_deploy_process(self, params=[]):
        if _Debug:
            print('BitDustApp.do_start_deploy_process params=%r finishing=%r' % (params, self.finishing.is_set(), ))
        if self.finishing.is_set():
            return
        if self.main_window.is_screen_active('welcome_screen'):
            welcome_screen = self.main_window.get_active_screen('welcome_screen')
            if welcome_screen:
                welcome_screen.populate(start_engine=True)
        self.main_window.engine_log = '\n'
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
                cmd=['/bin/bash', './src/deploy/osx.sh', ] + params,
                stdout_callback=self.on_deploy_process_stdout,
                stderr_callback=self.on_deploy_process_stderr,
                finishing=self.finishing,
                daemon=True,
                result_callback=self.on_deploy_process_result,
            ).run()

    def do_android_check_app_permission(self, permission):
        if not system.is_android():
            return True
        ret = check_permission(permission)
        if _Debug:
            print('BitDustApp.do_android_check_app_permission', permission, ret)
        return ret

    def do_android_request_app_permissions(self, permissions, callback=None):
        if not system.is_android():
            return True
        if _Debug:
            print('BitDustApp.do_android_request_app_permissions', permissions, callback)
        request_permissions(permissions, callback)
        return True

    @mainthread
    def on_deploy_process_stdout(self, line):
        if _Debug:
            print('DEPLOY OUT:', line.decode().rstrip())
        if line.decode().startswith('#####'):
            # self.main_window.engine_log += '[%s] %s' % (time.strftime('%H:%M:%S'), line.decode()[6:])
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
            return self.do_start()
        required_permissions = [
            'android.permission.INTERNET',
            'android.permission.READ_EXTERNAL_STORAGE',
            'android.permission.WRITE_EXTERNAL_STORAGE',
        ]
        if system.android_sdk_version() >= 28:
            required_permissions.append('android.permission.FOREGROUND_SERVICE')
        if _Debug:
            print('BitDustApp.on_start required_permissions=%r' % required_permissions)
        missed_permissions = []
        for perm in required_permissions:
            if not self.do_android_check_app_permission(perm):
                missed_permissions.append(perm)
        if _Debug:
            print('BitDustApp.on_start missed_permissions=%r' % missed_permissions)
        if not missed_permissions:
            return self.do_start()
        self.do_android_request_app_permissions(permissions=missed_permissions, callback=self.do_start)
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
                    self.profile.dump_stats('/storage/emulated/0/Android/data/org.bitdust_io.bitdust1/files/Documents/.bitdust/logs/debug.profile')
                else:
                    self.profile.dump_stats('./debug.profile')
        return True

    def on_resume(self):
        if _Debug:
            print('BitDustApp.on_resume')

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
