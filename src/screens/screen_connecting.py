from kivy.clock import Clock

#------------------------------------------------------------------------------

from components import screen

#------------------------------------------------------------------------------

class ConnectingScreen(screen.AppScreen):

    verify_network_connected_task = None

    def get_icon(self):
        return 'lan-pending'

    def get_title(self):
        return 'connecting...'

    def is_closable(self):
        return False

    def on_enter(self, *args):
        self.ids.state_panel.attach(automat_id='p2p_connector')
        if not self.verify_network_connected_task:
            self.verify_network_connected_task = Clock.schedule_interval(self.control().verify_network_connected, 1)

    def on_leave(self, *args):
        self.ids.state_panel.release()
        if self.verify_network_connected_task:
            Clock.unschedule(self.verify_network_connected_task)
            self.verify_network_connected_task = None
