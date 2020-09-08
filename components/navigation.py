from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager

#------------------------------------------------------------------------------

KVScreenManagement = """
<ScreenManagement>:
    transition: NoTransition()
    welcome_screen: welcome_screen
    main_menu_screen: main_menu_screen
    disconnected_screen: disconnected_screen
    new_identity_screen: new_identity_screen
    WelcomeScreen:
        id: welcome_screen
        name: 'welcome_screen'
    MainMenuScreen:
        id: main_menu_screen
        name: 'main_menu_screen'
    DisconnectedScreen:
        id: disconnected_screen
        name: 'disconnected_screen'
    NewIdentityScreen:
        id: new_identity_screen
        name: 'new_identity_screen'
    
"""

class ScreenManagement(ScreenManager):
    pass

#------------------------------------------------------------------------------

KVMainWindow = """
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
            canvas.before:
                Color:
                    rgba: .9, .9, 1, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
            id: nav_buttons_layout
            orientation: 'lr-tb'
            padding: 2
            spacing: 2
            size_hint: 1, None
            height: self.minimum_height
            NavButton:
                id: add_screen_btn: add_screen_btn
                screen: 'main_menu_screen'
                text: '+'
                bg_normal: .4,.65,.4,1
                bg_pressed: .5,.75,.5,1
                corner_radius: 8
            NavButton:
                id: new_identity_screen_btn: new_identity_screen_btn
                screen: 'new_identity_screen'
                text: 'new identity'
            NavButton:
                id: disconnected_screen_btn: disconnected_screen_btn
                screen: 'disconnected_screen'
                text: 'disconnected'
        ScreenManagement:
            id: screen_manager
            size_hint: 1, 1
"""

class MainWindow(FloatLayout):
    pass

#------------------------------------------------------------------------------

