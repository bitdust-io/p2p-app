from kivy.app import App
from kivy.clock import Clock

#------------------------------------------------------------------------------

from components.screen import AppScreen

#------------------------------------------------------------------------------


class ProcessDeadScreen(AppScreen):

    verify_process_health_task = None

    def on_enter(self, *args):
        self.verify_process_health_task = Clock.schedule_interval(App.get_running_app().control.verify_process_health, 3)

    def on_leave(self, *args):
        Clock.unschedule(self.verify_process_health_task)
        self.verify_process_health_task = None


from kivy.lang.builder import Builder 
Builder.load_file('./screens/screen_process_dead.kv')
