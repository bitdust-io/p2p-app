from kivy.properties import BooleanProperty  # @UnresolvedImport
from kivy.properties import StringProperty  # @UnresolvedImport

from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager

#------------------------------------------------------------------------------

from components.webfont import fa_icon

#------------------------------------------------------------------------------

KVScreenManagement = """
<ScreenManagement>:
    transition: NoTransition()
    MainMenuScreen:
        id: main_menu_screen
        name: 'main_menu_screen'
"""

class ScreenManagement(ScreenManager):
    pass

#------------------------------------------------------------------------------

KVNavButton = f"""
<NavButton>:
    spacing: 0
    padding: 0
    cols: 2
    rows: 1
    size_hint: None, None
    width: self.minimum_width
    height: 26
    Button:
        width: self.texture_size[0] + 14
        height: 26
        size_hint: None, None
        corner_radius: 8
        markup: True
        background_color: 0,0,0,0
        color: 1,1,1,1
        disabled_color: .8,.8,.8,1
        background_disabled_normal: ''
        bg_normal: .1,.5,.8,1
        bg_pressed: .2,.6,.9,1
        bg_disabled: .3,.3,.3,1
        bg_normal_delta: .1
        bg_disabled_delta: .1
        canvas.before:
            Color:
                rgba: self.bg_normal if (self.state == 'normal' and not root.selected) else self.bg_pressed 
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [self.corner_radius+1, 0, 0, self.corner_radius+1, ]
            Color:
                rgba: (self.bg_normal[0]+self.bg_normal_delta,self.bg_normal[1]+self.bg_normal_delta,self.bg_normal[2]+self.bg_normal_delta,1) if (self.state == 'normal' and not root.selected) else (self.bg_pressed[0]+self.bg_normal_delta,self.bg_pressed[1]+self.bg_normal_delta,self.bg_pressed[2]+self.bg_normal_delta,1)
            RoundedRectangle:
                pos: self.pos[0]+2, self.pos[1]+2
                size: self.size[0]-2, self.size[1]-4
                radius: [self.corner_radius, 0, 0, self.corner_radius, ]
        font_size: 16
        text: root.nav_btn_text
        on_press: root.on_action_area_pressed()
    Button:
        width: 21
        height: 26
        size_hint: None, None
        corner_radius: 8
        markup: True
        background_color: 0,0,0,0
        color: .3,.7,1,1
        disabled_color: .8,.8,.8,1
        background_disabled_normal: ''
        bg_normal: .1,.5,.8,1
        bg_pressed: .2,.6,.9,1
        bg_disabled: .3,.3,.3,1
        bg_normal_delta: 0
        bg_disabled_delta: .1
        canvas.before:
            Color:
                rgba: self.bg_normal 
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [0, self.corner_radius+1, self.corner_radius+1, 0, ]
            Color:
                rgba: (self.bg_normal[0]+self.bg_normal_delta,self.bg_normal[1]+self.bg_normal_delta,self.bg_normal[2]+self.bg_normal_delta,1) if self.state == 'normal' else (self.bg_pressed[0]+self.bg_normal_delta,self.bg_pressed[1]+self.bg_normal_delta,self.bg_pressed[2]+self.bg_normal_delta,1)
            RoundedRectangle:
                pos: self.pos[0]+2, self.pos[1]+2
                size: self.size[0]-4, self.size[1]-4
                radius: [0, self.corner_radius, self.corner_radius, 0, ]
        font_size: 16
        text: '{fa_icon('times')}'
        on_release: root.on_close_area_pressed()
"""

class NavButton(GridLayout):

    selected = BooleanProperty(False)

    def __init__(self, **kwargs):
        self.screen = kwargs.pop('screen')
        self.nav_btn_text = kwargs.pop('text')
        super(NavButton, self).__init__(**kwargs)

    def get_main_window(self):
        return self.parent.parent.parent

    def get_screen_manager(self):
        return self.get_main_window().ids.screen_manager

    def on_action_area_pressed(self):
        self.get_main_window().select_screen(self.screen)

    def on_close_area_pressed(self):
        self.get_main_window().close_screen(self.screen)

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

    def init_screens(self, screens_dict):
        for screen_id, screen_class in screens_dict.items():
            self.screens_map[screen_id] = screen_class

    def open_screen(self, screen_id):
        if screen_id in self.active_screens:
            raise Exception('screen already active')
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
            raise Exception('screen is not active')
        scrn, btn = self.active_screens.pop(screen_id)
        self.ids.screen_manager.remove_widget(scrn)
        self.ids.nav_buttons_layout.remove_widget(btn)

    def select_screen(self, screen_id):
        if screen_id not in self.active_screens:
            raise Exception('screen is not active')
        if self.selected_screen:
            _, selected_btn = self.active_screens[self.selected_screen]
            selected_btn.selected = False
        _, another_btn = self.active_screens[screen_id]
        another_btn.selected = True
        self.ids.screen_manager.current = screen_id
        self.selected_screen = screen_id

#------------------------------------------------------------------------------

