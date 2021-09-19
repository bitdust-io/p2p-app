from kivy.clock import Clock

#------------------------------------------------------------------------------

from components import screen

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

class EngineStatusScreen(screen.AppScreen):

    verify_process_health_task = None

    # def get_icon(self):
    #     return 'heart-pulse'

    def get_title(self):
        return 'status'

    def is_closable(self):
        return False

    def on_enter(self, *args):
        if _Debug:
            print('EngineStatusScreen.on_enter')
        self.ids.state_panel.attach(automat_id='initializer')
        Clock.schedule_once(self.control().verify_process_health)
        if not self.verify_process_health_task:
            self.verify_process_health_task = Clock.schedule_interval(self.control().verify_process_health, 5)

    def on_leave(self, *args):
        if _Debug:
            print('EngineStatusScreen.on_leave')
        self.ids.state_panel.release()
        if self.verify_process_health_task:
            Clock.unschedule(self.verify_process_health_task)
            self.verify_process_health_task = None

    def on_engine_on_checkbox(self, *args):
        if _Debug:
            print('EngineStatusScreen.on_engine_on_checkbox', args)

    def on_start_engine_button_clicked(self, *args):
        if _Debug:
            print('EngineStatusScreen.on_start_engine_button_clicked', args)
