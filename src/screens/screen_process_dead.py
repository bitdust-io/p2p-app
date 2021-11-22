from kivy.clock import Clock

#------------------------------------------------------------------------------

from components import screen

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

class ProcessDeadScreen(screen.AppScreen):

    verify_process_health_task = None

    # def get_icon(self):
    #     return 'heart-pulse'

    def get_title(self):
        return 'starting'

    def is_closable(self):
        return False

    def on_enter(self, *args):
        if _Debug:
            print('screen_process_dead.on_enter')
        self.ids.state_panel.attach(automat_id='initializer')
        if not self.verify_process_health_task:
            self.verify_process_health_task = Clock.schedule_interval(self.control().verify_process_health, 3)

    def on_leave(self, *args):
        if _Debug:
            print('screen_process_dead.on_leave')
        self.ids.state_panel.release()
        if self.verify_process_health_task:
            Clock.unschedule(self.verify_process_health_task)
            self.verify_process_health_task = None

    def on_start_engine_button_clicked(self, *args):
        if _Debug:
            print('screen_process_dead.on_start_engine_button_clicked')
