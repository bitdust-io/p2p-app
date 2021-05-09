from kivy.clock import Clock

#------------------------------------------------------------------------------

from components import screen

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

class WelcomeScreen(screen.AppScreen):

    verify_network_connected_task = None

    def get_icon(self):
        return 'human-greeting'

    def get_title(self):
        return 'welcome'

    def on_enter(self, *args):
        if not self.verify_network_connected_task:
            self.verify_network_connected_task = Clock.schedule_interval(self.control().verify_network_connected, 10)

    def on_leave(self, *args):
        if self.verify_network_connected_task:
            Clock.unschedule(self.verify_network_connected_task)
            self.verify_network_connected_task = None

    def on_action_button_clicked(self, btn):
        if _Debug:
            print('WelcomeScreen.on_action_button_clicked', btn.icon)
        self.ids.action_button.close_stack()
        if btn.icon == '':
            self.main_win().select_screen('')
        elif btn.icon == '':
            pass

    def on_nav_button_clicked(self):
        self.ids.action_button.close_stack()
