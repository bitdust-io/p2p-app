from kivy.clock import Clock

#------------------------------------------------------------------------------

from components.screen import AppScreen

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

class ProcessDeadScreen(AppScreen):

    verify_process_health_task = None

    def is_closable(self):
        return False

    def on_enter(self, *args):
        if _Debug:
            print('ProcessDeadScreen.on_enter')
        if not self.verify_process_health_task:
            self.verify_process_health_task = Clock.schedule_interval(self.control().verify_process_health, 3)

    def on_leave(self, *args):
        if _Debug:
            print('ProcessDeadScreen.on_leave')
        if self.verify_process_health_task:
            Clock.unschedule(self.verify_process_health_task)
            self.verify_process_health_task = None

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./screens/screen_process_dead.kv')
