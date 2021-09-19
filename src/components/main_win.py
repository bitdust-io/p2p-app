import os
import time

#------------------------------------------------------------------------------

from kivy.lang import Builder
from kivy.factory import Factory
# from kivy.clock import Clock
from kivy.properties import StringProperty  # @UnresolvedImport
from kivy.properties import NumericProperty  # @UnresolvedImport
from kivy.properties import ObjectProperty  # @UnresolvedImport
from kivy.properties import BooleanProperty  # @UnresolvedImport
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout

from kivymd.theming import ThemableBehavior
from kivymd.uix.menu import MDDropdownMenu

#------------------------------------------------------------------------------

from lib import system

from components import webfont

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

def patch_kivy_core_window():
    from kivy.core.window import Window

    def _get_android_kheight(self=Window):
        ret = system.get_android_keyboard_height()
        return ret

    def _get_size(self=Window):
        if _Debug:
            print('main_window._get_size', self)
        r = self._rotation
        w, h = self._size
        if self._density != 1:
            w, h = self._win._get_gl_size()
        if self.softinput_mode == 'resize':
            h -= system.get_android_keyboard_height()  # self.keyboard_height
        if r in (0, 180):
            return w, h
        return h, w

    def update_viewport(self=Window):
        from kivy.graphics.opengl import glViewport  # @UnresolvedImport
        from kivy.graphics.transformation import Matrix  # @UnresolvedImport
        from math import radians

        w, h = self.system_size
        if self._density != 1:
            w, h = self.size

        smode = self.softinput_mode
        target = self._system_keyboard.target
        targettop = max(0, target.to_window(0, target.y)[1]) if target else 0
        kheight = system.get_android_keyboard_height()

        w2, h2 = w / 2., h / 2.
        r = radians(self.rotation)

        x, y = 0, 0
        _h = h
        if smode == 'pan':
            y = kheight
        elif smode == 'below_target':
            y = 0 if kheight < targettop else (kheight - targettop)
        if smode == 'scale':
            _h -= kheight
        if smode == 'resize':
            y += kheight
        # prepare the viewport
        glViewport(x, y, w, _h)

        try:
            # do projection matrix
            projection_mat = Matrix()
            projection_mat.view_clip(0.0, w, 0.0, h, -1.0, 1.0, 0)
        except Exception as exc:
            if _Debug:
                print('main_window.update_viewport', exc)
            return
        self.render_context['projection_mat'] = projection_mat

        # do modelview matrix
        modelview_mat = Matrix().translate(w2, h2, 0)
        modelview_mat = modelview_mat.multiply(Matrix().rotate(r, 0, 0, 1))

        w, h = self.size
        w2, h2 = w / 2., h / 2.
        modelview_mat = modelview_mat.multiply(Matrix().translate(-w2, -h2, 0))
        self.render_context['modelview_mat'] = modelview_mat
        frag_modelview_mat = Matrix()
        frag_modelview_mat.set(flat=modelview_mat.get())
        self.render_context['frag_modelview_mat'] = frag_modelview_mat

        # redraw canvas
        self.canvas.ask_update()

        # and update childs
        self.update_childsize()

    Window.clearcolor = (1, 1, 1, 1)
    Window.fullscreen = False

    if system.is_android():
        Window.update_viewport = update_viewport
        Window._get_size = _get_size
        Window._get_android_kheight = _get_android_kheight
        Window.keyboard_anim_args = {"d": 0.1,"t": "linear", }
        softinput_mode = 'resize'
        Window.softinput_mode = softinput_mode
        # set_android_system_ui_visibility()

    if _Debug:
        print('main_window.patch_kivy_core_window', Window)

#------------------------------------------------------------------------------

class ContentNavigationDrawer(BoxLayout):
    pass

#------------------------------------------------------------------------------

class MainWin(Screen, ThemableBehavior):

    control = None
    screens_map = {}
    screens_loaded = set()
    active_screens = {}
    dropdown_menus = {}
    screen_closed_time = {}
    latest_screen = ''
    screens_stack = []

    # kivy properties
    engine_is_on = BooleanProperty(False)
    engine_log = StringProperty('')
    state_process_health = NumericProperty(0)
    state_identity_get = NumericProperty(0)
    state_network_connected = NumericProperty(0)
    selected_screen = StringProperty('')
    dropdown_menu = ObjectProperty(None)

    # menu_item_status = BooleanProperty(True)
    # menu_item_my_identity = BooleanProperty(False)
    # menu_item_chat = BooleanProperty(False)
    # menu_item_settings = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        patch_kivy_core_window()

    def nav(self):
        return self.ids.nav_drawer

    def menu(self):
        return self.ids.nav_drawer_content

    def tbar(self):
        return self.ids.toolbar

    def register_screens(self, screens_dict):
        for screen_type, screen_module_class in screens_dict.items():
            screen_kv_file, screen_module, screen_classname = screen_module_class
            Factory.register(screen_classname, module=screen_module)
            self.screens_map[screen_type] = (screen_classname, screen_kv_file, )
        if _Debug:
            print('MainWin.register_screens  done with %d registered items' % len(self.screens_map))

    def unregister_screens(self):
        self.screens_map.clear()
        if _Debug:
            print('MainWin.unregister_screens done')

    def register_controller(self, cont): 
        self.control = cont

    def unregister_controller(self): 
        self.control = None

    #------------------------------------------------------------------------------

    def is_screen_active(self, screen_id):
        return screen_id in self.active_screens

    def get_active_screen(self, screen_id):
        return self.active_screens.get(screen_id, [None, ])[0]

    def is_screen_selectable(self, screen_id):
        if not self.control:
            return False
        if self.state_process_health != 1:
            return screen_id in ['engine_status_screen', 'startup_screen', 'welcome_screen', ]
        if self.state_identity_get != 1:
            return screen_id in ['engine_status_screen', 'startup_screen', 'welcome_screen', 'settings_screen',
                                 'my_id_screen', 'new_identity_screen', 'recover_identity_screen', ]
        if self.state_network_connected != 1:
            return screen_id in ['engine_status_screen', 'startup_screen', 'welcome_screen',
                                 'connecting_screen', 'settings_screen',
                                 'my_id_screen', 'new_identity_screen', 'recover_identity_screen', ]
        return True

    def update_menu_items(self):
        if not self.control:
            return
        self.menu().ids.menu_item_status.disabled = False
        if self.state_process_health != 1:
            self.menu().ids.menu_item_my_identity.disabled = True
            self.menu().ids.menu_item_chat.disabled = True
            self.menu().ids.menu_item_settings.disabled = True
            return
        if self.state_identity_get != 1:
            self.menu().ids.menu_item_my_identity.disabled = False
            self.menu().ids.menu_item_chat.disabled = True
            self.menu().ids.menu_item_settings.disabled = False
            return
        if self.state_network_connected != 1:
            self.menu().ids.menu_item_my_identity.disabled = False
            self.menu().ids.menu_item_chat.disabled = True
            self.menu().ids.menu_item_settings.disabled = False
            return
        self.menu().ids.menu_item_my_identity.disabled = False
        self.menu().ids.menu_item_chat.disabled = False
        self.menu().ids.menu_item_settings.disabled = False

    #------------------------------------------------------------------------------

    def populate_toolbar_content(self, screen_inst=None):
        if not screen_inst:
            self.ids.toolbar.title = 'BitDust'
            return
        title = screen_inst.get_title()
        icn = screen_inst.get_icon()
        if icn:
            icn_pack = screen_inst.get_icon_pack()
            title = '[size=28sp]{}[/size]  {}'.format(webfont.make_icon(icn, icon_pack=icn_pack), title)
        if title:
            self.ids.toolbar.title = title
        else:
            self.ids.toolbar.title = 'BitDust'

    def populate_dropdown_menu(self, screen_id, new_items):
        if _Debug:
            print('MainWin.populate_dropdown_menu', new_items)
        # self.control.app.dropdown_menu.dismiss()
        # self.control.app.dropdown_menu.menu.ids.box.clear_widgets()
        itms = []
        for itm in new_items:
            itm.update({
                "height": "40dp",
                "top_pad": "10dp",
                "bot_pad": "10dp",
            })
            itms.append(itm)
        # self.control.app.dropdown_menu.items = itms
        # self.control.app.dropdown_menu.create_menu_items()
        self.dropdown_menus[screen_id] = MDDropdownMenu(
            caller=self.ids.dropdown_menu_placeholder,
            width_mult=3,
            items=itms,
            # selected_color=self.theme_cls.bg_darkest,
            opening_time=0,
            # radius=[0, ],
        )
        self.dropdown_menus[screen_id].bind(on_release=self.on_dropdown_menu_callback)

    #------------------------------------------------------------------------------

    def open_screen(self, screen_id, screen_type, **kwargs):
        manager = self.ids.screen_manager
        if manager.has_screen(screen_id):
            if _Debug:
                print('MainWin.open_screen   screen %r already registered in the screen manager' % screen_id)
            return
        if screen_id in self.active_screens:
            if _Debug:
                print('MainWin.open_screen   screen %r already opened' % screen_id)
            return
        screen_class_name, screen_kv_file = self.screens_map[screen_type]
        if screen_kv_file:
            if system.is_android():
                screen_kv_file = os.path.abspath(os.path.join(os.environ['ANDROID_ARGUMENT'], screen_kv_file))
            else:
                screen_kv_file = os.path.abspath(os.path.join('src', screen_kv_file))
            if screen_kv_file in self.screens_loaded:
                if _Debug:
                    print('MainWin.open_screen   KV file already loaded: %r' % screen_kv_file)
            else:
                if screen_kv_file in Builder.files:
                    if _Debug:
                        print('MainWin.open_screen   KV file already loaded, but not marked: %r' % screen_kv_file)
                else:
                    if _Debug:
                        print('MainWin.open_screen   is about to load KV file : %r' % screen_kv_file)
                    Builder.load_file(screen_kv_file)
                self.screens_loaded.add(screen_kv_file)
        screen_class = Factory.get(screen_class_name)
        if not screen_class:
            raise Exception('screen class %r was not registered' % screen_class_name)
        if _Debug:
            print('MainWin.open_screen   is about to create a new instance of %r with id %r' % (screen_class, screen_id, ))
        screen_inst = screen_class(name=screen_id, **kwargs)
        self.active_screens[screen_id] = (screen_inst, None, )
        # menu_items = screen_inst.get_dropdown_menu_items()
        # if menu_items:
        #     self.populate_dropdown_menu(screen_id, menu_items)
        manager.add_widget(screen_inst)
        screen_inst.on_opened()
        if _Debug:
            print('MainWin.open_screen   opened screen %r' % screen_id)

    def close_screen(self, screen_id):
        if screen_id not in self.active_screens:
            if _Debug:
                print('MainWin.close_screen   screen %r has not been opened' % screen_id)
            return
        screen_inst, btn = self.active_screens.pop(screen_id)
        self.screen_closed_time.pop(screen_id, None)
        if screen_inst not in self.ids.screen_manager.children:
            if _Debug:
                print('MainWin.close_screen   WARNING   screen instance %r was not found among screen manager children' % screen_inst)
        self.ids.screen_manager.remove_widget(screen_inst)
        # screen_inst.on_closed()
        del screen_inst
        if _Debug:
            print('MainWin.close_screen  closed screen %r' % screen_id)

    def close_screens(self, screen_ids_list):
        for screen_id in screen_ids_list:
            self.close_screen(screen_id)

    def close_active_screens(self, exclude_screens=[]):
        screen_ids = list(self.active_screens.keys())
        for screen_id in screen_ids:
            if screen_id not in exclude_screens:
                self.close_screen(screen_id)

    def cleanup_screens(self, *args):
        screen_ids = list(self.active_screens.keys())
        for screen_id in screen_ids:
            if screen_id == self.selected_screen:
                continue
            closed_time = self.screen_closed_time.get(screen_id)
            if closed_time:
                if time.time() - closed_time > 5.0:
                    if _Debug:
                        print('closing inactive screen %r : %d ~ %d' % (screen_id, time.time(), closed_time, ))
                    self.close_screen(screen_id)

    def select_screen(self, screen_id, verify_state=False, screen_type=None, **kwargs):
        if screen_type is None:
            screen_type = screen_id
            if screen_type.startswith('private_chat_'):
                screen_type = 'private_chat_screen'
            elif screen_type.startswith('group_'):
                screen_type = 'group_chat_screen'
            elif screen_type.startswith('info_group_'):
                screen_type = 'group_info_screen'
        if verify_state:
            if not self.is_screen_selectable(screen_id):
                if _Debug:
                    print('MainWin.select_screen   selecting screen %r not possible at the moment' % screen_id)
                return False
        if _Debug:
            print('MainWin.select_screen  starting transition to %r' % screen_id)
        if screen_id not in self.active_screens:
            self.open_screen(screen_id, screen_type, **kwargs)
        else:
            self.active_screens[screen_id][0].init_kwargs(**kwargs)
        if self.selected_screen and self.selected_screen == screen_id:
            if _Debug:
                print('MainWin.select_screen   skip, selected screen is already %r' % screen_id)
            return True
        self.populate_toolbar_content(self.active_screens[screen_id][0])
        if self.selected_screen:
            if _Debug:
                print('MainWin.select_screen   is about to switch away screen manger from currently selected screen %r' % self.selected_screen)
            self.screen_closed_time[self.selected_screen] = time.time()
            if self.selected_screen in self.active_screens:
                self.active_screens[self.selected_screen][0].on_closed()
        if self.selected_screen and self.selected_screen not in ['engine_status_screen', 'connecting_screen', 'startup_screen', ]:
            self.latest_screen = self.selected_screen
            if _Debug:
                print('MainWin.select_screen   current screens stack: %r' % self.screens_stack)
            if self.selected_screen not in self.screens_stack:
                if screen_id not in self.screens_stack:
                    self.screens_stack.append(self.selected_screen)
                else:
                    self.screens_stack.remove(screen_id)
            else:
                self.screens_stack.remove(self.selected_screen)
            if _Debug:
                print('MainWin.select_screen   new screens stack: %r' % self.screens_stack)
        self.selected_screen = screen_id
        if self.selected_screen in ['engine_status_screen', 'connecting_screen', 'startup_screen', ]:
            self.screens_stack = []
        if self.screens_stack:
            self.tbar().left_action_items = [["arrow-left", self.on_nav_back_button_clicked, ], ]
        else:
            self.tbar().left_action_items = [["menu", self.on_left_menu_button_clicked, ], ]
        if _Debug:
            print('MainWin.select_screen   is going to switch screen manager to %r' % screen_id)
        self.ids.screen_manager.current = screen_id
        self.active_screens[screen_id][0].on_opened()
        return True

    #------------------------------------------------------------------------------

    def on_nav_back_button_clicked(self, *args):
        if _Debug:
            print('MainWin.on_nav_back_button_clicked', self.screens_stack)
        back_to_screen = None
        if self.screens_stack:
            back_to_screen = self.screens_stack[-1]
        if back_to_screen:
            self.select_screen(back_to_screen)
        else:
            self.tbar().left_action_items = [["menu", self.on_left_menu_button_clicked, ], ]

    def on_left_menu_button_clicked(self, *args):
        if _Debug:
            print('MainWin.on_left_menu_button_clicked', self.selected_screen)
        if self.selected_screen:
            self.active_screens[self.selected_screen][0].on_nav_button_clicked()
        self.nav().set_state("open")

    def on_right_menu_button_clicked(self, *args):
        if _Debug:
            print('MainWin.on_right_menu_button_clicked', self.selected_screen, len(self.dropdown_menus))
        if self.selected_screen and self.selected_screen in self.dropdown_menus:
            self.dropdown_menus[self.selected_screen].open()

    def on_dropdown_menu_callback(self, instance_menu, instance_menu_item):
        if _Debug:
            print('MainWin.on_dropdown_menu_callback', self.selected_screen, instance_menu_item.text)
        instance_menu.dismiss()
        if self.selected_screen:
            self.active_screens[self.selected_screen][0].on_dropdown_menu_item_clicked(
                instance_menu, instance_menu_item
            )

    def on_state_process_health(self, instance, value):
        self.control.on_state_process_health(instance, value)

    def on_state_identity_get(self, instance, value):
        self.control.on_state_identity_get(instance, value)

    def on_state_network_connected(self, instance, value):
        self.control.on_state_network_connected(instance, value)

    # def on_height(self, instance, value):
    #     if _Debug:
    #         print ('MainWin.on_height', instance, value)

    # def on_size(self, instance, value):
    #     if _Debug:
    #         print ('MainWin.on_size', instance, value)
