from kivy.properties import StringProperty  # @UnresolvedImport
from kivy.properties import NumericProperty  # @UnresolvedImport

from kivy.uix.floatlayout import FloatLayout

#------------------------------------------------------------------------------

from components.navigation import NavButton

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

class MainWindow(FloatLayout):

    screens_map = {}
    control = None
    active_screens = {}
    selected_screen = StringProperty('')
    latest_screen = ''

    state_process_health = NumericProperty(0)
    state_identity_get = NumericProperty(0)
    state_network_connected = NumericProperty(0)

    def register_screens(self, screens_dict):
        for screen_id, screen_class in screens_dict.items():
            self.screens_map[screen_id] = screen_class

    def unregister_screens(self):
        self.screens_map.clear()

    def register_controller(self, cont): 
        self.control = cont

    def unregister_controller(self): 
        self.control = None

    def open_screen(self, screen_id):
        if screen_id in self.active_screens:
            if _Debug:
                print('screen %r already opened' % screen_id)
            return
        screen_class = self.screens_map[screen_id]
        screen = screen_class(name=screen_id, id=screen_id)
        self.ids.screen_manager.add_widget(screen)
        title = screen.get_title()
        if title:
            btn = NavButton(
                text=screen.get_title(),
                screen=screen_id,
            )
            self.ids.nav_buttons_layout.add_widget(btn)
        else:
            btn = None
        self.ids.screen_manager.current = screen_id
        self.active_screens[screen_id] = (screen, btn, )
        if _Debug:
            print('opened screen %r with button %r' % (screen_id, bool(btn), ))

    def close_screen(self, screen_id):
        if screen_id not in self.active_screens:
            if _Debug:
                print('screen %r has not been opened' % screen_id)
            return
        scrn, btn = self.active_screens.pop(screen_id)
        self.ids.screen_manager.remove_widget(scrn)
        self.ids.nav_buttons_layout.remove_widget(btn)
        if _Debug:
            print('closed screen %r' % screen_id)

    def select_screen(self, screen_id):
        if _Debug:
            print('selecting screen %r' % screen_id)
        if screen_id not in self.active_screens:
            self.open_screen(screen_id)
        self.ids.main_nav_button.disabled = bool(screen_id in ['process_dead_screen', 'connecting_screen', ])
        if self.selected_screen:
            if self.selected_screen == screen_id:
                if _Debug:
                    print('skip, selected screen is already %r' % screen_id)
                return
            if self.selected_screen in self.active_screens:
                _, selected_btn = self.active_screens[self.selected_screen]
                if selected_btn:
                    selected_btn.selected = False
        _, another_btn = self.active_screens[screen_id]
        if another_btn:
            another_btn.selected = True
        self.ids.screen_manager.current = screen_id
        self.selected_screen = screen_id
        if self.selected_screen not in ['process_dead_screen', 'connecting_screen', ]:
            self.latest_screen = self.selected_screen

    def on_state_process_health(self, instance, value):
        if _Debug:
            print('on_state_process_health', value)
        if value == -1:
            if self.selected_screen:
                if self.selected_screen not in ['process_dead_screen', 'connecting_screen', ]:
                    self.latest_screen = self.selected_screen
            self.select_screen('process_dead_screen')
            self.close_screen('connecting_screen')
            self.close_screen('new_identity_screen')
            self.close_screen('recover_identity_screen')
            return
        if value == 1:
            self.on_state_success()
            return
        if value == 0:
            self.control.run()
            return
        raise Exception('unexpected state: %r' % value)

    def on_state_identity_get(self, instance, value):
        if _Debug:
            print('on_state_identity_get', value)
        if value == -1:
            if self.selected_screen:
                if self.selected_screen not in ['process_dead_screen', 'connecting_screen', ]:
                    self.latest_screen = self.selected_screen
            self.select_screen('new_identity_screen')
            self.close_screen('process_dead_screen')
            self.close_screen('connecting_screen')
            return
        if value == 1:
            self.on_state_success()
            return
        if value == 0:
            self.control.run()
            return
        raise Exception('unexpected state: %r' % value)

    def on_state_network_connected(self, instance, value):
        if _Debug:
            print('on_state_network_connected', value)
        if value == -1:
            if self.selected_screen:
                if self.selected_screen not in ['process_dead_screen', 'connecting_screen', ]:
                    self.latest_screen = self.selected_screen
            self.select_screen('connecting_screen')
            self.close_screen('process_dead_screen')
            self.close_screen('new_identity_screen')
            self.close_screen('recover_identity_screen')
            return
        if value == 1:
            self.on_state_success()
            return
        if value == 0:
            self.control.run()
            return
        raise Exception('unexpected state: %r' % value)
    
    def on_state_success(self):
        if _Debug:
            print('on_state_success %r %r %r, latest_screen=%r' % (
                self.state_process_health, self.state_identity_get, self.state_network_connected, self.latest_screen, ))
        if self.state_process_health == 1 and self.state_identity_get == 1 and self.state_network_connected == 1:
            self.select_screen(self.latest_screen or 'main_menu_screen')
            self.close_screen('process_dead_screen')
            self.close_screen('connecting_screen')
            self.close_screen('new_identity_screen')
            self.close_screen('recover_identity_screen')
            return
        if self.state_process_health == 1 and self.state_identity_get == 1 and self.state_network_connected == -1:
            if self.selected_screen:
                if self.selected_screen not in ['process_dead_screen', 'connecting_screen', ]:
                    self.latest_screen = self.selected_screen
            self.select_screen('connecting_screen')
            self.close_screen('process_dead_screen')
            self.close_screen('new_identity_screen')
            self.close_screen('recover_identity_screen')
            return
        if self.state_process_health == 1 and self.state_identity_get == -1:
            if self.selected_screen:
                if self.selected_screen not in ['process_dead_screen', 'connecting_screen', ]:
                    self.latest_screen = self.selected_screen
            self.select_screen('new_identity_screen')
            self.close_screen('process_dead_screen')
            self.close_screen('connecting_screen')
            self.close_screen('recover_identity_screen')
            return
        self.select_screen('connecting_screen')
        self.close_screen('process_dead_screen')
        self.close_screen('new_identity_screen')
        self.close_screen('recover_identity_screen')
        # raise Exception('unexpected state reached: %r %r %r' % (
        #     self.state_process_health, self.state_identity_get, self.state_network_connected,
        # ))

    def on_main_menu_button_pressed(self, *args):
        if self.state_process_health == 1 and self.state_identity_get == 1:
            self.select_screen('main_menu_screen')

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./components/main_window.kv')
