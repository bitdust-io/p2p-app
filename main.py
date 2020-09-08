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

#------------------------------------------------------------------------------

kv = """
#:import NoTransition kivy.uix.screenmanager.NoTransition
"""

kv += labels.KVLabel
kv += buttons.KVButton
kv += buttons.KVNavButton
kv += navigation.KVScreenManagement
kv += screen_welcome.KVWelcomeScreen
kv += screen_main_menu.KVMainMenuScreen
kv += screen_offline.KVDisconnectedScreen
kv += screen_new_identity.KVNewIdentityScreen
kv += navigation.KVMainWindow

Builder.load_string(kv)

#------------------------------------------------------------------------------ 

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')  # disable multi-touch
Config.set('graphics', 'resizable', True)

#------------------------------------------------------------------------------

class BitDustApp(App):

    def build(self):
        return navigation.MainWindow()

#------------------------------------------------------------------------------

if __name__ == '__main__':
    BitDustApp().run()
