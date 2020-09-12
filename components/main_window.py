from kivy.properties import StringProperty  # @UnresolvedImport
from kivy.properties import NumericProperty  # @UnresolvedImport

from kivy.uix.floatlayout import FloatLayout

#------------------------------------------------------------------------------

from components.webfont import fa_icon
from components.navigation import NavButton

#------------------------------------------------------------------------------

KVMainWindow = f"""
<MainWindow>:
    color: 0, 0, 0, 1
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: 'vertical'
        size_hint: 1, 1
        StackLayout:
            id: nav_buttons_layout
            orientation: 'lr-tb'
            padding: 1
            spacing: 2
            size_hint: 1, None
            height: self.minimum_height
            RoundedButton:
                id: main_nav_button
                size_hint: None, None
                width: 26
                height: 26
                bg_normal: .4,.65,.4,1
                bg_pressed: .5,.75,.5,1
                corner_radius: 8
                font_size: 16
                text: '{fa_icon('plus')}'
                on_press: root.ids.screen_manager.current = 'main_menu_screen'
        ScreenManagement:
            id: screen_manager
            size_hint: 1, 1
"""

class MainWindow(FloatLayout):

    screens_map = {}
    active_screens = {}
    selected_screen = StringProperty('')
    latest_screen = ''

    state_process_health = NumericProperty(0)
    state_network_connected = NumericProperty(0)
    state_identity_get = NumericProperty(0)

    def register_screens(self, screens_dict):
        for screen_id, screen_class in screens_dict.items():
            self.screens_map[screen_id] = screen_class

    def open_screen(self, screen_id):
        if screen_id in self.active_screens:
            return
        screen_class = self.screens_map[screen_id]
        screen = screen_class(name=screen_id, id=screen_id)
        self.ids.screen_manager.add_widget(screen)
        btn = NavButton(
            text=screen.get_title(),
            screen=screen_id,
        )
        self.ids.nav_buttons_layout.add_widget(btn)
        self.ids.screen_manager.current = screen_id
        self.active_screens[screen_id] = (screen, btn, )

    def close_screen(self, screen_id):
        if screen_id not in self.active_screens:
            return
        scrn, btn = self.active_screens.pop(screen_id)
        self.ids.screen_manager.remove_widget(scrn)
        self.ids.nav_buttons_layout.remove_widget(btn)

    def select_screen(self, screen_id):
        if screen_id not in self.active_screens:
            self.open_screen(screen_id)
        if self.selected_screen:
            _, selected_btn = self.active_screens[self.selected_screen]
            selected_btn.selected = False
        _, another_btn = self.active_screens[screen_id]
        another_btn.selected = True
        self.ids.screen_manager.current = screen_id
        self.selected_screen = screen_id
        self.latest_screen = self.selected_screen

    def on_state_process_health(self, instance, value):
        print('on_state_process_health', value)
        if value == -1:
            self.latest_screen = self.selected_screen
            self.select_screen('process_dead')
        else:
            if self.latest_screen:
                self.select_screen(self.latest_screen)
