from kivy.app import App

from kivy.config import Config

from kivy.lang import Builder

#------------------------------------------------------------------------------

from components import buttons
from components import labels
from components import navigation

from screens import screen_welcome
from screens import screen_main_menu
from screens import screen_offline
from screens import screen_new_identity
from screens import screen_private_chat

from service import websock

#------------------------------------------------------------------------------ 

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')  # disable multi-touch
Config.set('graphics', 'resizable', True)

#------------------------------------------------------------------------------

kv = """
#:import NoTransition kivy.uix.screenmanager.NoTransition
#:import Window kivy.core.window.Window
"""

kv += labels.KVLabel
kv += buttons.KVRoundedButton
kv += screen_welcome.KVWelcomeScreen
kv += screen_main_menu.KVMainMenuScreen
kv += screen_offline.KVDisconnectedScreen
kv += screen_new_identity.KVNewIdentityScreen
kv += screen_private_chat.KVPrivateChatScreen
kv += navigation.KVNavButton
kv += navigation.KVScreenManagement
kv += navigation.KVMainWindow

Builder.load_string(kv)

#------------------------------------------------------------------------------

class BitDustApp(App):

    def build(self):
        main_window = navigation.MainWindow()
        main_window.init_screens({
            'welcome_screen': screen_welcome.WelcomeScreen,
            'disconnected_screen': screen_offline.DisconnectedScreen,
            'new_identity_screen': screen_new_identity.NewIdentityScreen,
            'private_chat_alice': screen_private_chat.PrivateChatScreen,
        })
        main_window.open_screen('welcome_screen')
        main_window.open_screen('new_identity_screen')
        main_window.open_screen('private_chat_alice')
        main_window.select_screen('private_chat_alice')
        return main_window

    def on_process_health(self, resp):
        print('on_process_health', resp)

    def on_start(self):
        websock.start()
        websock.ws_call({"command": "api_call", "method": "process_health", "kwargs": {}, }, self.on_process_health)

    def on_stop(self):
        websock.stop()

#------------------------------------------------------------------------------

if __name__ == '__main__':
    BitDustApp().run()
