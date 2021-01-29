from kivy.properties import StringProperty  # @UnresolvedImport
from kivy.properties import NumericProperty  # @UnresolvedImport
from kivy.uix.floatlayout import FloatLayout
from kivymd.theming import ThemableBehavior

#------------------------------------------------------------------------------

from components.navigation import NavButtonActive, NavButtonClosable
from components.buttons import CustomIconButton

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

class MainNavButton(CustomIconButton):
    pass


class MainWindow(FloatLayout, ThemableBehavior):

    screens_map = {}
    control = None
    active_screens = {}
    selected_screen = StringProperty('')
    latest_screen = ''

    state_process_health = NumericProperty(0)
    state_identity_get = NumericProperty(0)
    state_network_connected = NumericProperty(0)

    def register_screens(self, screens_dict):
        for screen_type, screen_class in screens_dict.items():
            self.screens_map[screen_type] = screen_class

    def unregister_screens(self):
        self.screens_map.clear()

    def register_controller(self, cont): 
        self.control = cont

    def unregister_controller(self): 
        self.control = None

    #------------------------------------------------------------------------------

    def is_screen_active(self, screen_id):
        return screen_id in self.active_screens

    def get_active_screen(self, screen_id):
        return self.active_screens.get(screen_id, [None, ])[0]

    def open_screen(self, screen_id, screen_type, **kwargs):
        if screen_id in self.active_screens:
            if _Debug:
                print('MainWindow.open_screen   screen %r already opened' % screen_id)
            return
        screen_class = self.screens_map[screen_type]
        screen = screen_class(name=screen_id, **kwargs)
        screen.on_opened()
        self.ids.screen_manager.add_widget(screen)
        title = screen.get_title()
        icn = screen.get_icon()
        closable = screen.is_closable()
        if title:
            if closable:
                btn = NavButtonClosable(text=title, icon=icn, screen=screen_id)
            else:
                btn = NavButtonActive(text=title, icon=icn, screen=screen_id)
            self.ids.nav_buttons_layout.add_widget(btn)
        else:
            btn = None
        self.ids.screen_manager.current = screen_id
        self.active_screens[screen_id] = (screen, btn, )
        if _Debug:
            print('MainWindow.open_screen   opened screen %r with button %r' % (screen_id, bool(btn), ))

    def close_screen(self, screen_id):
        if screen_id not in self.active_screens:
            if _Debug:
                print('MainWindow.close_screen   screen %r has not been opened' % screen_id)
            return
        scrn, btn = self.active_screens.pop(screen_id)
        self.ids.screen_manager.remove_widget(scrn)
        if btn:
            self.ids.nav_buttons_layout.remove_widget(btn)
            del btn
        scrn.on_closed()
        del scrn
        if _Debug:
            print('MainWindow.close_screen  closed screen %r' % screen_id)

    def close_screens(self, screen_ids_list):
        for screen_id in screen_ids_list:
            self.close_screen(screen_id)

    def close_active_screens(self, exclude_screens=[]):
        screen_ids = list(self.active_screens.keys())
        for screen_id in screen_ids:
            if screen_id not in exclude_screens:
                self.close_screen(screen_id)

    def select_screen(self, screen_id, verify_state=False, screen_type=None, **kwargs):
        if screen_type is None:
            screen_type = screen_id
            if screen_type.startswith('private_chat_'):
                screen_type = 'private_chat_screen'
            if screen_type.startswith('group_'):
                screen_type = 'group_chat_screen'
        if verify_state:
            if self.state_process_health != 1 or self.state_identity_get != 1:
                if _Debug:
                    print('MainWindow.select_screen   selecting screen %r not possible, state verify failed' % screen_id)
                return False
        if _Debug:
            print('MainWindow.select_screen  %r' % screen_id)
        if screen_id not in self.active_screens:
            self.open_screen(screen_id, screen_type, **kwargs)
        else:
            self.active_screens[screen_id][0].init_kwargs(**kwargs)
        self.ids.main_nav_button.disabled = bool(screen_id in ['process_dead_screen', 'connecting_screen', 'startup_screen', ])
        if self.selected_screen:
            if self.selected_screen == screen_id:
                if _Debug:
                    print('MainWindow.select_screen   skip, selected screen is already %r' % screen_id)
                return True
            if self.selected_screen in self.active_screens:
                _, selected_btn = self.active_screens[self.selected_screen]
                if selected_btn:
                    selected_btn.selected = False
        _, another_btn = self.active_screens[screen_id]
        if another_btn:
            another_btn.selected = True
        self.ids.screen_manager.current = screen_id
        self.selected_screen = screen_id
        if self.selected_screen not in ['process_dead_screen', 'connecting_screen', 'welcome_screen', 'startup_screen', ]:
            self.latest_screen = self.selected_screen
        return True

    #------------------------------------------------------------------------------

    def on_state_process_health(self, instance, value):
        self.control.on_state_process_health(instance, value)

    def on_state_identity_get(self, instance, value):
        self.control.on_state_identity_get(instance, value)

    def on_state_network_connected(self, instance, value):
        self.control.on_state_network_connected(instance, value)

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./components/main_window.kv')
