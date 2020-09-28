from kivy.clock import Clock

#------------------------------------------------------------------------------

from components.screen import AppScreen

#------------------------------------------------------------------------------

class ConnectingScreen(AppScreen):

    verify_network_connected_task = None

    def is_closable(self):
        return False

    def on_enter(self, *args):
        self.verify_network_connected_task = Clock.schedule_interval(self.control().verify_network_connected, 1)

    def on_leave(self, *args):
        Clock.unschedule(self.verify_network_connected_task)
        self.verify_network_connected_task = None


from kivy.lang.builder import Builder 
Builder.load_file('./screens/screen_connecting.kv')
