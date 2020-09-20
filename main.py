from kivy.app import App

from kivy.config import Config

from kivy.lang import Builder

#------------------------------------------------------------------------------

from screens import controller

#------------------------------------------------------------------------------ 

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')  # disable multi-touch
Config.set('graphics', 'resizable', True)
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '740')

#------------------------------------------------------------------------------

Builder.load_string("""
#:import NoTransition kivy.uix.screenmanager.NoTransition
#:import Window kivy.core.window.Window
#:import fa_icon components.webfont.fa_icon
""")

#------------------------------------------------------------------------------

class BitDustApp(App):

    control = None
    main_window = None

    def build(self):
        from components import labels
        from components import buttons
        from components import text_input
        from components import navigation
        from components import main_window

        from screens import screen_main_menu
        from screens import screen_welcome
        from screens import screen_process_dead
        from screens import screen_new_identity
        from screens import screen_recover_identity
        from screens import screen_connecting
        from screens import screen_private_chat

        self.control = controller.Controller(self)
        self.main_window = main_window.MainWindow()
        self.main_window.register_screens({
            'process_dead': screen_process_dead.ProcessDeadScreen,
            'connecting_screen': screen_connecting.ConnectingScreen,
            'welcome_screen': screen_welcome.WelcomeScreen,
            'new_identity_screen': screen_new_identity.NewIdentityScreen,
            'recover_identity_screen': screen_recover_identity.RecoverIdentityScreen,
            'private_chat_alice': screen_private_chat.PrivateChatScreen,
        })
        return self.main_window

    def on_start(self):
        self.control.start()

    def on_stop(self):
        self.control.stop()

#------------------------------------------------------------------------------

if __name__ == '__main__':
    BitDustApp().run()
