import time

#------------------------------------------------------------------------------

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.properties import StringProperty  # @UnresolvedImport
from kivy.properties import NumericProperty  # @UnresolvedImport
from kivy.properties import ObjectProperty  # @UnresolvedImport
from kivy.properties import BooleanProperty  # @UnresolvedImport
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout

from kivymd.theming import ThemableBehavior

#------------------------------------------------------------------------------

from lib import system

from components import webfont
from components import all_components
from components import dialogs
from components import styles

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

_orig_request_keyboard = None
_orig_release_keyboard = None

#------------------------------------------------------------------------------

def patch_kivy_core_window():
    global _orig_request_keyboard
    global _orig_release_keyboard

    Window.clearcolor = (1, 1, 1, 1)
    Window.fullscreen = False

    if system.is_android():
        Window.keyboard_anim_args = {"d": 0.001, "t": "linear", }
        Window.softinput_mode = ''

    if _Debug:
        print('main_window.patch_kivy_core_window', Window)

#------------------------------------------------------------------------------

class CustomContentNavigationDrawer(BoxLayout):
    pass

#------------------------------------------------------------------------------

class MainWin(Screen, ThemableBehavior, styles.AppStyle):

    control = None
    screens_map = {}
    screens_loaded = set()
    active_screens = {}
    screen_closed_time = {}
    screens_stack = []

    engine_is_on = BooleanProperty(False)
    engine_log = StringProperty('')
    selected_screen = StringProperty('')
    dropdown_menu = ObjectProperty(None)

    state_node_local = ObjectProperty(None)
    state_device_authorized = BooleanProperty(False)
    state_process_health = NumericProperty(-1)
    state_identity_get = NumericProperty(-1)
    state_network_connected = NumericProperty(-1)
    state_entangled_dht = NumericProperty(-1)
    state_proxy_transport = NumericProperty(-1)
    state_my_data = NumericProperty(-1)
    state_message_history = NumericProperty(-1)
    state_rebuilding = BooleanProperty(False)

    def __init__(self, **kwargs):
        self.device_server_code_display_dialog = None
        self.device_client_code_input_dialog = None
        super().__init__(**kwargs)
        patch_kivy_core_window()
        Clock.schedule_once(self.on_init_done)

    def nav(self):
        return self.ids.nav_drawer

    def menu(self):
        return self.ids.nav_drawer_content

    def tbar(self):
        return self.ids.toolbar

    def footer(self):
        return self.ids.footer

    def footer_bar(self):
        return self.ids.footer_bar

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
        if self.state_node_local is False:
            if not self.state_device_authorized:
                return screen_id in ['device_connect_screen', 'about_screen', ]
        if self.state_process_health != 1:
            return screen_id in ['engine_status_screen', 'startup_screen', 'welcome_screen', 'about_screen', ]
        if self.state_identity_get != 1:
            return screen_id in ['engine_status_screen', 'startup_screen', 'welcome_screen', 'settings_screen',
                                 'my_id_screen', 'new_identity_screen', 'recover_identity_screen', 'about_screen', ]
        if self.state_network_connected != 1:
            return screen_id in ['engine_status_screen', 'startup_screen', 'welcome_screen',
                                 'connecting_screen', 'settings_screen',
                                 'my_id_screen', 'new_identity_screen', 'recover_identity_screen', 'about_screen', ]
        return True

    def update_menu_items(self):
        if not self.control:
            return
        if self.state_node_local is False:
            if self.state_device_authorized:
                if self.state_process_health != 1:
                    self.menu().ids.menu_item_status.disabled = True
                    self.menu().ids.menu_item_my_identity.disabled = True
                    self.menu().ids.menu_item_chat.disabled = True
                    self.menu().ids.menu_item_friends.disabled = True
                    self.menu().ids.menu_item_settings.disabled = True
                    self.menu().ids.menu_item_private_files.disabled = True
                    self.menu().ids.menu_item_shares.disabled = True
                    return
            else:
                self.menu().ids.menu_item_status.disabled = True
                self.menu().ids.menu_item_my_identity.disabled = True
                self.menu().ids.menu_item_chat.disabled = True
                self.menu().ids.menu_item_friends.disabled = True
                self.menu().ids.menu_item_settings.disabled = True
                self.menu().ids.menu_item_private_files.disabled = True
                self.menu().ids.menu_item_shares.disabled = True
                return
        self.menu().ids.menu_item_status.disabled = False
        if self.state_process_health != 1:
            self.menu().ids.menu_item_my_identity.disabled = True
            self.menu().ids.menu_item_chat.disabled = True
            self.menu().ids.menu_item_friends.disabled = True
            self.menu().ids.menu_item_settings.disabled = True
            self.menu().ids.menu_item_private_files.disabled = True
            self.menu().ids.menu_item_shares.disabled = True
            return
        if self.state_identity_get != 1:
            self.menu().ids.menu_item_my_identity.disabled = False
            self.menu().ids.menu_item_chat.disabled = True
            self.menu().ids.menu_item_friends.disabled = True
            self.menu().ids.menu_item_settings.disabled = False
            self.menu().ids.menu_item_private_files.disabled = True
            self.menu().ids.menu_item_shares.disabled = True
            return
        if self.state_network_connected != 1:
            self.menu().ids.menu_item_my_identity.disabled = False
            self.menu().ids.menu_item_friends.disabled = True
            self.menu().ids.menu_item_chat.disabled = True
            self.menu().ids.menu_item_settings.disabled = False
            self.menu().ids.menu_item_private_files.disabled = True
            self.menu().ids.menu_item_shares.disabled = True
            return
        self.menu().ids.menu_item_my_identity.disabled = False
        self.menu().ids.menu_item_chat.disabled = self.state_message_history != 1
        self.menu().ids.menu_item_friends.disabled = False
        self.menu().ids.menu_item_settings.disabled = False
        self.menu().ids.menu_item_private_files.disabled = self.state_my_data != 1
        self.menu().ids.menu_item_shares.disabled = self.state_my_data != 1

    #------------------------------------------------------------------------------

    def populate_toolbar_content(self, screen_inst=None):
        if not screen_inst:
            self.ids.toolbar.title = ''
            return
        title = screen_inst.get_title()
        if title and system.is_android():
            if len(title) > 20:
                title = title[:20] + '...'
        icn = screen_inst.get_icon()
        if icn:
            icn_pack = screen_inst.get_icon_pack()
            title = '[size=24sp]{}[/size] {}'.format(webfont.make_icon(icn, icon_pack=icn_pack), title)
        if title:
            self.ids.toolbar.title = title
        else:
            self.ids.toolbar.title = ''

    def populate_dropdown_menu(self, screen_inst=None):
        if _Debug:
            print('MainWin.populate_dropdown_menu', screen_inst)
        if not screen_inst:
            self.tbar().right_action_items = []
            return
        drop_down_menu = screen_inst.ids.get('drop_down_menu')
        if not drop_down_menu:
            self.tbar().right_action_items = []
            return
        self.tbar().right_action_items = [["dots-vertical", self.on_drop_down_menu_clicked, ], ]

    def populate_hot_button(self, screen_inst=None):
        if not screen_inst:
            self.footer_bar().set_bottom_action_button(None)
            return
        bottom_action_button_info = screen_inst.get_hot_button()
        if not bottom_action_button_info:
            self.footer_bar().set_bottom_action_button(None)
            return
        self.footer_bar().set_bottom_action_button(
            icon=bottom_action_button_info.get('icon'),
            color=self.color(bottom_action_button_info.get('color')),
        )

    def populate_bottom_toolbar_icon(self, icon_name, state):
        Clock.schedule_once(lambda *a: self.footer_bar().update_bottom_action_bar_item(icon_name, state))

    def populate_device_server_code_display_dialog(self, event_data):
        if _Debug:
            print('MainWin.populate_device_server_code_display_dialog', event_data)
        if self.device_server_code_display_dialog:
            self.device_server_code_display_dialog.dismiss()
            self.device_server_code_display_dialog = None
        server_code = event_data['server_code']
        self.device_server_code_display_dialog = dialogs.open_message_dialog(
            title='Authorization code',
            text='[color=#000]Enter the authorization code dispalyed bellow on your device running BitDust p2p-app:\n\n\n[size=24sp]%s[/size][/color]' % server_code,
            button_confirm='Continue',
            cb=self.on_device_server_code_display_dialog_closed,
        )

    def populate_device_client_code_input_dialog(self, event_data):
        if self.device_server_code_display_dialog:
            self.device_server_code_display_dialog.dismiss()
            self.device_server_code_display_dialog = None
        device_name = event_data['device_name']
        self.device_client_code_input_dialog = dialogs.open_number_input_dialog(
            title='Device code',
            text='Enter 6-digits authorization code generated on your device:',
            button_confirm='Confirm',
            button_cancel='Back',
            cb=lambda inp: self.on_device_client_code_entered(device_name, inp),
        )

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
            screen_kv_file = all_components.root_path(filename=screen_kv_file)
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
            print('MainWin.open_screen   is about to create a new instance of %r with id %r, kwargs=%r' % (screen_class, screen_id, kwargs, ))
        screen_inst = screen_class(name=screen_id, **kwargs)
        self.active_screens[screen_id] = (screen_inst, None, )
        manager.add_widget(screen_inst)
        screen_inst.close_drop_down_menu()
        screen_inst.on_created()
        screen_inst.on_opened()
        if _Debug:
            print('MainWin.open_screen   opened screen %r' % screen_id)

    def close_screen(self, screen_id):
        if screen_id not in self.active_screens:
            if _Debug:
                print('MainWin.close_screen   screen %r has not been opened' % screen_id)
            return
        screen_inst, _ = self.active_screens.pop(screen_id)
        screen_inst.on_destroying()
        self.screen_closed_time.pop(screen_id, None)
        if screen_inst not in self.ids.screen_manager.children:
            if _Debug:
                print('MainWin.close_screen   WARNING   screen instance %r was not found among screen manager children' % screen_inst)
        screen_inst.close_drop_down_menu()
        self.ids.screen_manager.remove_widget(screen_inst)
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

    def select_screen(self, screen_id, verify_state=False, screen_type=None, clear_stack=False, **kwargs):
        if screen_type is None:
            screen_type = screen_id
            if screen_type.startswith('private_chat_'):
                screen_type = 'private_chat_screen'
            elif screen_type.startswith('group_'):
                screen_type = 'group_chat_screen'
            elif screen_type.startswith('info_group_'):
                screen_type = 'group_info_screen'
            elif screen_type.startswith('private_file_'):
                screen_type = 'single_private_file_screen'
            elif screen_type.startswith('shared_location_'):
                screen_type = 'shared_location_screen'
        if verify_state:
            if not self.is_screen_selectable(screen_id):
                if _Debug:
                    print('MainWin.select_screen   selecting screen %r not possible at the moment' % screen_id)
                return None
        if _Debug:
            print('MainWin.select_screen  starting transition to %r' % screen_id)
        if screen_id not in self.active_screens:
            self.open_screen(screen_id, screen_type, **kwargs)
        else:
            self.active_screens[screen_id][0].init_kwargs(**kwargs)
        if self.selected_screen and self.selected_screen == screen_id:
            if _Debug:
                print('MainWin.select_screen   skip, selected screen is already %r' % screen_id)
            return self.active_screens[screen_id][0]
        self.populate_toolbar_content(self.active_screens[screen_id][0])
        self.populate_hot_button(self.active_screens[screen_id][0])
        self.populate_dropdown_menu(self.active_screens[screen_id][0])
        if self.selected_screen:
            if _Debug:
                print('MainWin.select_screen   is about to switch away screen manager from currently selected screen %r' % self.selected_screen)
            self.screen_closed_time[self.selected_screen] = time.time()
            if self.selected_screen in self.active_screens:
                self.active_screens[self.selected_screen][0].close_drop_down_menu()
                self.active_screens[self.selected_screen][0].on_closed()
        if self.selected_screen and self.selected_screen not in ['startup_screen', ]:
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
        # if self.selected_screen in ['engine_status_screen', 'connecting_screen', 'startup_screen', ]:
        #     self.screens_stack = []
        if self.screens_stack and not clear_stack:
            self.tbar().left_action_items = [["arrow-left", self.on_nav_back_button_clicked, ], ]
        else:
            self.tbar().left_action_items = [["menu", self.on_left_menu_button_clicked, ], ]
        if _Debug:
            print('MainWin.select_screen   is going to switch screen manager to %r' % screen_id)
        self.ids.screen_manager.current = screen_id
        self.active_screens[screen_id][0].close_drop_down_menu()
        self.active_screens[screen_id][0].on_opened()
        if clear_stack:
            self.screens_stack.clear()
            self.screens_stack.append('welcome_screen')
        return self.active_screens[screen_id][0]

    def screen_back(self):
        back_to_screen = None
        if self.screens_stack:
            back_to_screen = self.screens_stack[-1]
        if _Debug:
            print('MainWin.screen_back %r' % back_to_screen)
        if back_to_screen:
            self.select_screen(back_to_screen)
            return True
        self.tbar().left_action_items = [["menu", self.on_left_menu_button_clicked, ], ]
        return False

    #------------------------------------------------------------------------------

    def on_init_done(self, *args):
        if _Debug:
            print('MainWin.on_init_done', self.footer_bar().height, self.footer_bar().bottom_action_button.x, self.footer_bar().bottom_action_button.y, )
        if self.selected_screen:
            self.populate_hot_button(self.active_screens[self.selected_screen][0])
            self.populate_dropdown_menu(self.active_screens[self.selected_screen][0])

    def on_hot_button_clicked(self, *args):
        if _Debug:
            print('MainWin.on_hot_button_clicked', self.selected_screen)
        if self.selected_screen:
            self.active_screens[self.selected_screen][0].on_hot_button_clicked()

    def on_nav_back_button_clicked(self, *args):
        if _Debug:
            print('MainWin.on_nav_back_button_clicked', self.screens_stack)
        self.screen_back()

    def on_system_back_button_clicked(self, *args):
        if _Debug:
            print('MainWin.on_system_back_button_clicked', self.screens_stack, *args)
        if self.screen_back():
            return True
        if system.is_android():
            return False
        return True
#         back_to_screen = None
#         if self.screens_stack:
#             back_to_screen = self.screens_stack[-1]
#         if back_to_screen:
#             self.select_screen(back_to_screen)
#             return True
#         self.tbar().left_action_items = [["menu", self.on_left_menu_button_clicked, ], ]
#         if system.is_android():
#             return False
#         return True

    def on_left_menu_button_clicked(self, *args):
        if _Debug:
            print('MainWin.on_left_menu_button_clicked', self.selected_screen)
        self.update_menu_items()
        if self.selected_screen:
            self.active_screens[self.selected_screen][0].on_nav_button_clicked()
        self.nav().set_state("open")

#     def on_right_menu_button_clicked(self, *args):
#         if _Debug:
#             print('MainWin.on_right_menu_button_clicked', self.selected_screen, len(self.dropdown_menus))
#         if self.selected_screen and self.selected_screen in self.dropdown_menus:
#             self.dropdown_menus[self.selected_screen].open()

    def on_drop_down_menu_clicked(self, *args):
        if _Debug:
            print('MainWin.on_drop_down_menu_clicked', args)
        if self.selected_screen:
            self.active_screens[self.selected_screen][0].open_drop_down_menu()

#     def on_dropdown_menu_callback(self, instance_menu, instance_menu_item):
#         if _Debug:
#             print('MainWin.on_dropdown_menu_callback', self.selected_screen, instance_menu_item.text)
#         instance_menu.dismiss()
#         if self.selected_screen:
#             self.active_screens[self.selected_screen][0].on_dropdown_menu_item_clicked(
#                 instance_menu, instance_menu_item
#             )

    def on_state_process_health(self, instance, value):
        if _Debug:
            print('MainWin.on_state_process_health', value)
        self.populate_bottom_toolbar_icon('micro-chip', value)
        self.control.on_state_process_health(instance, value)
        if self.is_screen_active('welcome_screen'):
            welcome_screen = self.get_active_screen('welcome_screen')
            if welcome_screen:
                welcome_screen.populate()
                # Clock.schedule_once(lambda dt: welcome_screen.populate(), 0.01)

    def on_state_identity_get(self, instance, value):
        if _Debug:
            print('MainWin.on_state_identity_get', value)
        self.populate_bottom_toolbar_icon('id-card', value)
        self.control.on_state_identity_get(instance, value)
        if self.is_screen_active('welcome_screen'):
            welcome_screen = self.get_active_screen('welcome_screen')
            if welcome_screen:
                welcome_screen.populate()
                # Clock.schedule_once(lambda dt: welcome_screen.populate(), 0.01)

    def on_state_network_connected(self, instance, value):
        if _Debug:
            print('MainWin.on_state_network_connected', value)
        self.populate_bottom_toolbar_icon('lan-connect', value)
        self.control.on_state_network_connected(instance, value)
        if self.is_screen_active('welcome_screen'):
            welcome_screen = self.get_active_screen('welcome_screen')
            if welcome_screen:
                welcome_screen.populate()
                # Clock.schedule_once(lambda dt: welcome_screen.populate(), 0.01)

    def on_state_entangled_dht(self, instance, value):
        if _Debug:
            print('MainWin.on_state_entangled_dht', value)
        self.populate_bottom_toolbar_icon('family-tree', value)
        self.control.on_state_entangled_dht(instance, value)

    def on_state_proxy_transport(self, instance, value):
        if _Debug:
            print('MainWin.on_state_proxy_transport', value)
        self.populate_bottom_toolbar_icon('transit-connection-variant', value)
        self.control.on_state_proxy_transport(instance, value)

    def on_state_my_data(self, instance, value):
        if _Debug:
            print('MainWin.on_state_my_data', value)
        not_blinking = value
        if self.state_rebuilding:
            not_blinking = 0
        self.populate_bottom_toolbar_icon('database', not_blinking)
        self.control.on_state_my_data(instance, value)

    def on_state_message_history(self, instance, value):
        if _Debug:
            print('MainWin.on_state_message_history', value)
        self.populate_bottom_toolbar_icon('comments', value)
        self.control.on_state_message_history(instance, value)

    def on_state_rebuilding(self, instance, value):
        if _Debug:
            print('MainWin.on_state_rebuilding', value)
        not_blinking = self.state_my_data
        if value:
            not_blinking = 0
        self.populate_bottom_toolbar_icon('database', not_blinking)

    def on_device_server_code_display_dialog_closed(self, *args, **kwargs):
        if _Debug:
            print('MainWin.on_device_client_code_entered', args, kwargs)
        self.device_server_code_display_dialog = None

    def on_device_client_code_entered(self, device_name, inp):
        if _Debug:
            print('MainWin.on_device_client_code_entered', device_name, inp)
        self.device_client_code_input_dialog = None
        self.control.on_device_client_code_entered(device_name, inp)
