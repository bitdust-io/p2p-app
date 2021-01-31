#!/usr/bin/env python -u
# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------

import os
import sys
import time

#------------------------------------------------------------------------------

import locale
locale.setlocale(locale.LC_CTYPE, 'en_US.UTF-8')

if 'ANDROID_ARGUMENT' not in os.environ:
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

#------------------------------------------------------------------------------ 

_Debug = True

#------------------------------------------------------------------------------

if _Debug:
    print('BitDustApp __file__', os.path.dirname(os.path.abspath(__file__)))
    print('BitDustApp os.getcwd', os.path.abspath(os.getcwd()))
    print('BitDustApp sys.path', sys.path)
    print('BitDustApp os.listdir', os.listdir(os.getcwd()))

#------------------------------------------------------------------------------

# current_src_folder = os.path.abspath(os.path.join(os.getcwd(), 'src'))
# if os.path.isdir(current_src_folder):
#     if current_src_folder not in sys.path:
#         sys.path.append(current_src_folder)
#         if _Debug:
#             print('added %r to Python sys.path' % current_src_folder)

#------------------------------------------------------------------------------

from kivy.lang import Builder
from kivy.config import Config

from lib.system import is_android

#------------------------------------------------------------------------------

Config.set('input', 'mouse', 'mouse,multitouch_on_demand,disable_on_activity,disable_multitouch')  # disable multi-touch
Config.set('graphics', 'resizable', True)
Config.set('graphics', 'fullscreen', False)

# if is_android():
#     pass 
    # Config.set('graphics', 'width', '360')
    # Config.set('graphics', 'height', '740')
# else:
    # Config.set('graphics', 'width', '600')
    # Config.set('graphics', 'height', '300')

#------------------------------------------------------------------------------

from kivy.core.text import LabelBase
from kivy.core.window import Window

from kivymd.app import MDApp
from kivymd.font_definitions import theme_font_styles

#------------------------------------------------------------------------------

from screens import controller

from components import styles

#------------------------------------------------------------------------------

if is_android(): 
    from jnius import autoclass  # @UnresolvedImport
    import encodings.idna

    from android.config import ACTIVITY_CLASS_NAME, ACTIVITY_CLASS_NAMESPACE  # @UnresolvedImport
    from android.storage import app_storage_path, primary_external_storage_path  # @UnresolvedImport

    from lib.permissions import check_permission, request_permissions  # @UnresolvedImport

#------------------------------------------------------------------------------

# os.environ['KIVY_METRICS_DENSITY'] = '1'
# os.environ['KIVY_METRICS_FONTSCALE'] = '1'

#------------------------------------------------------------------------------

Builder.load_string("""
#:import NoTransition kivy.uix.screenmanager.NoTransition
#:import fa_icon components.webfont.fa_icon
#:import md_icon components.webfont.md_icon
#:import icofont_icon components.webfont.icofont_icon
#:import make_icon components.webfont.make_icon
""")

#------------------------------------------------------------------------------

if is_android():
    PACKAGE_NAME = 'org.bitdust_io.bitdust1'
    SERVICE_NAME = '{packagename}.Service{servicename}'.format(
        packagename=PACKAGE_NAME,
        servicename='Bitdustnode'
    )    
    APP_STARTUP_PERMISSIONS = [
        'android.permission.INTERNET',
        'android.permission.READ_EXTERNAL_STORAGE',
        'android.permission.WRITE_EXTERNAL_STORAGE',
        'android.permission.FOREGROUND_SERVICE',
    ]
    PythonActivity = autoclass('org.bitdust_io.bitdust1.BitDustActivity')

#------------------------------------------------------------------------------

def check_app_permission(permission):
    if not is_android():
        return True
    ret = check_permission(permission)
    if _Debug:
        print('BitDustApp.check_app_permission', permission, ret)
    return ret


def request_app_permissions(permissions=[], callback=None):
    if not is_android():
        return True
    if not permissions:
        permissions = APP_STARTUP_PERMISSIONS
    if _Debug:
        print('BitDustApp.request_app_permissions', permissions, callback)
    request_permissions(permissions, callback)
    return True

#------------------------------------------------------------------------------

class BitDustApp(styles.AppStyle, MDApp):

    control = None
    main_window = None

    def build(self):
        if _Debug:
            print('BitDustApp.build')
            if is_android():
                print('BitDustApp.build   ACTIVITY_CLASS_NAME=%r' % ACTIVITY_CLASS_NAME)
                print('BitDustApp.build   ACTIVITY_CLASS_NAMESPACE=%r' % ACTIVITY_CLASS_NAMESPACE)

        self.theme_cls.theme_style = 'Light'
        self.theme_cls.primary_palette = 'Blue'
        self.theme_cls.primary_hue = "400"
        self.theme_cls.accent_palette = 'Green'

        fonts_path = './src/fonts'
        if is_android():
            fonts_path = os.path.join(os.environ['ANDROID_ARGUMENT'], 'fonts')

        LabelBase.register(name="IconMD", fn_regular=os.path.join(fonts_path, "md.ttf"))
        theme_font_styles.append('IconMD')
        self.theme_cls.font_styles["IconMD"] = ["IconMD", 22, False, 0.15, ]

        LabelBase.register(name="IconFA", fn_regular=os.path.join(fonts_path, "fa-solid.ttf"))
        theme_font_styles.append('IconFA')
        self.theme_cls.font_styles["IconFA"] = ["IconFA", 22, False, 0.15, ]

        LabelBase.register(name="IconICO", fn_regular=os.path.join(fonts_path, "icofont.ttf"))
        theme_font_styles.append('IconICO')
        self.theme_cls.font_styles["IconICO"] = ["IconICO", 22, False, 0.15, ]

        from components import layouts
        from components import labels
        from components import buttons
        from components import text_input
        from components import list_view
        from components import navigation
        from components import main_window

        self.control = controller.Controller(self)
        self.main_window = main_window.MainWindow()
        self.main_window.register_screens(controller.all_screens())
        self.main_window.register_controller(self.control)
        self.main_window.select_screen(screen_id='startup_screen', verify_state=False)
        # Window.bind(on_keyboard=self.on_key_input)
        return self.main_window

    def do_start(self, *args, **kwargs):
        if _Debug:
            print('BitDustApp.do_start', args, kwargs)

        if is_android():
            if args:
                if len(args) >= 2:
                    if args[1] and isinstance(args[1], list):
                        if False in args[1]:
                            if _Debug:
                                print('BitDustApp.do_start   FAILED : some of the requested permissions was not granted', args)
                            return False
            if _Debug:
                print('BitDustApp.do_start   is okay to start now, storage path is %r' % primary_external_storage_path())

        self.control.start()

        if is_android():
            self.start_android_service()
        else:
            self.check_restart_bitdust_engine()
        return True

    def start_android_service(self, finishing=False):
        if not is_android():
            return None
        if _Debug:
            print('BitDustApp.start_android_service finishing=%r' % finishing)
        service = autoclass(SERVICE_NAME)
        mActivity = PythonActivity.mActivity
        argument = ''
        if finishing:
            argument = '{"stop_service": 1}'
        service.start(mActivity, argument)
        if finishing:
            self.service = None
            if _Debug:
                print('BitDustApp.start_android_service service expect to be STOPPED now')
        else:
            self.service = service
            if _Debug:
                print('BitDustApp.start_android_service service STARTED : %r' % self.service)
        return self.service

    def stop_android_service(self):
        if not is_android():
            return None
        if _Debug:
            print('BitDustApp.stop_service %r' % self.service)
        service = autoclass(SERVICE_NAME)
        service.stop(PythonActivity.mActivity)
        self.start_android_service(finishing=True)
        if _Debug:
            print('BitDustApp.stop_service STOPPED')
        return self.service

    def check_restart_bitdust_engine(self):
        if is_android():
            return None
        # TODO: to be implemented ...

    def on_start(self):
        if not is_android():
            if _Debug:
                print('BitDustApp.on_start')
            return self.do_start()

        global APP_STARTUP_PERMISSIONS
        if _Debug:
            print('BitDustApp.on_start APP_STARTUP_PERMISSIONS=%r' % APP_STARTUP_PERMISSIONS)

        missed_permissions = []
        for perm in APP_STARTUP_PERMISSIONS:
            if not check_app_permission(perm):
                missed_permissions.append(perm)
        if _Debug:
            print('BitDustApp.on_start missed_permissions=%r' % missed_permissions)

        if not missed_permissions:
            return self.do_start() 

        request_app_permissions(permissions=missed_permissions, callback=self.do_start)
        return True

    def on_stop(self):
        if _Debug:
            print('BitDustApp.on_stop')
        self.control.stop()
        self.main_window.unregister_controller()
        self.main_window.unregister_screens()
        # TODO: check if we need to stop BitDust engine after App closes

    def on_pause(self):
        if _Debug:
            print('BitDustApp.on_pause')
        return True

    def on_resume(self):
        if _Debug:
            print('BitDustApp.on_resume')

    def on_key_input(self, window_obj, key_code, scancode, codepoint, modifier):
        if _Debug:
            print('BitDustApp.on_key_input', key_code, scancode, modifier)
        if is_android():
            if key_code == 27:
                return True
            else:
                return False
        return False

    def on_height(self, instance, value):
        # instance.y += Window.keyboard_height
        if _Debug:
            print ('BitDustApp.on_height', instance, value, Window.keyboard_height)

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
