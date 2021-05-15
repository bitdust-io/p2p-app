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
        self.ids.action_button.close_stack()
        self.ids.state_panel.attach(automat_id='initializer')
        if not self.verify_network_connected_task:
            self.verify_network_connected_task = Clock.schedule_interval(self.control().verify_network_connected, 10)

    def on_leave(self, *args):
        self.ids.action_button.close_stack()
        self.ids.state_panel.release()
        if self.verify_network_connected_task:
            Clock.unschedule(self.verify_network_connected_task)
            self.verify_network_connected_task = None

    def on_action_button_clicked(self, btn):
        if _Debug:
            print('WelcomeScreen.on_action_button_clicked', btn.icon)
        self.ids.action_button.close_stack()
        if btn.icon == 'chat-plus-outline':
            self.main_win().select_screen('create_group_screen')
        elif btn.icon == 'account-key-outline':
            self.main_win().select_screen('friends_screen')

    def on_nav_button_clicked(self):
        self.ids.action_button.close_stack()
