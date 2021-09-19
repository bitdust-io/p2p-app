from kivy.clock import Clock

#------------------------------------------------------------------------------

from components import screen
# from components import snackbar

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
        self.ids.deploy_output_label.text = self.main_win().engine_log
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

    def on_engine_on_off(self, *args):
        if _Debug:
            print('EngineStatusScreen.on_engine_on_off', args)
        st = args[0]
        if st:
            self.app().start_engine()
            # snackbar.info(text='BitDust engine is starting')
        else:
            self.app().stop_engine()
            # snackbar.info(text='BitDust engine will be stopped')
