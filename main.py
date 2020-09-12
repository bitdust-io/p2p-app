from kivy.app import App

from kivy.config import Config

from kivy.lang import Builder

#------------------------------------------------------------------------------

from components import buttons
from components import labels
from components import navigation
from components import main_window

from screens import screen_welcome
from screens import screen_main_menu
from screens import screen_process_dead
from screens import screen_offline
from screens import screen_new_identity
from screens import screen_private_chat
from screens import controller

#------------------------------------------------------------------------------ 

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')  # disable multi-touch
Config.set('graphics', 'resizable', True)

#------------------------------------------------------------------------------

kv = """
#:import NoTransition kivy.uix.screenmanager.NoTransition
#:import Window kivy.core.window.Window
""" + '\n'.join([
    labels.KVLabel,
    buttons.KVRoundedButton,
    screen_welcome.KVWelcomeScreen,
    screen_main_menu.KVMainMenuScreen,
    screen_process_dead.KVProcessDeadScreen,
    screen_offline.KVDisconnectedScreen,
    screen_new_identity.KVNewIdentityScreen,
    screen_private_chat.KVPrivateChatScreen,
    navigation.KVNavButton,
    navigation.KVScreenManagement,
    main_window.KVMainWindow,
])

Builder.load_string(kv)

#------------------------------------------------------------------------------

class BitDustApp(App):

    control = None
    main_window = None

    def build(self):
        self.control = controller.Controller(self)
        self.main_window = main_window.MainWindow()
        self.main_window.register_screens({
            'process_dead': screen_process_dead.ProcessDeadScreen,
            'welcome_screen': screen_welcome.WelcomeScreen,
            'disconnected_screen': screen_offline.DisconnectedScreen,
            'new_identity_screen': screen_new_identity.NewIdentityScreen,
            'private_chat_alice': screen_private_chat.PrivateChatScreen,
        })
        # main_window.open_screen('welcome_screen')
        # main_window.open_screen('new_identity_screen')
        # main_window.open_screen('private_chat_alice')
        # main_window.select_screen('private_chat_alice')
        return self.main_window

    def on_start(self):
        self.control.start()

    def on_stop(self):
        self.control.stop()

#------------------------------------------------------------------------------

if __name__ == '__main__':
    BitDustApp().run()
