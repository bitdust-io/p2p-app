from kivy.clock import Clock

#------------------------------------------------------------------------------

from lib import api_client

from components import screen
from components import styles

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

class EngineStatusScreen(screen.AppScreen):

    # verify_process_health_task = None
    state_panel_attached = False

    # def get_icon(self):
    #     return 'heart-pulse'

    def get_title(self):
        return 'status'

    def is_closable(self):
        return False

    def populate(self):
        if _Debug:
            print('EngineStatusScreen.populate state_panel_attached=%r' % self.state_panel_attached)
        self.on_service(None)

    def on_enter(self, *args):
        if _Debug:
            print('EngineStatusScreen.on_enter')
        if self.main_win().engine_is_on:
            if not self.state_panel_attached:
                self.state_panel_attached = self.ids.state_panel.attach(automat_id='initializer')
        api_client.add_model_listener('service', listener_cb=self.on_service)
        # Clock.schedule_once(self.control().verify_process_health)
        # if not self.verify_process_health_task:
        #     self.verify_process_health_task = Clock.schedule_interval(self.control().verify_process_health, 5)
        self.populate()

    def on_leave(self, *args):
        if _Debug:
            print('EngineStatusScreen.on_leave')
        # if self.verify_process_health_task:
        #     Clock.unschedule(self.verify_process_health_task)
        #     self.verify_process_health_task = None
        api_client.remove_model_listener('service', listener_cb=self.on_service)
        if self.state_panel_attached:
            self.ids.state_panel.release()
        self.state_panel_attached = False

    def on_engine_on_off(self, *args):
        if _Debug:
            print('EngineStatusScreen.on_engine_on_off', args)
        st = args[0]
        if st:
            self.app().start_engine()
            self.state_panel_attached = self.ids.state_panel.attach(automat_id='initializer')
            self.populate()
        else:
            self.set_nw_progress(0)
            if self.state_panel_attached:
                self.ids.state_panel.release()
            self.state_panel_attached = False
            self.app().stop_engine()
            self.set_nw_progress(0)

    def on_network_connection_status_pressed(self, *args):
        if _Debug:
            print('EngineStatusScreen.on_network_connection_status_pressed', args)
        self.main_win().select_screen('connecting_screen')

    def on_service(self, payload):
        if _Debug:
            print('EngineStatusScreen.on_service')
        if not self.main_win().engine_is_on:
            self.set_nw_progress(0)
            return
        services_by_state = {}
        count_total = 0.0
        count_on = 0.0
        for snap_info in self.model('service').values():
            if snap_info:
                svc = snap_info['data']
                st = svc.get('state')
                if not svc.get('enabled'):
                    continue
                if st not in services_by_state:
                    services_by_state[st] = {}
                services_by_state[st][svc['name']] = svc
                count_total += 1.0
                if st == 'ON':
                    count_on += 1.0
        if count_total:
            self.set_nw_progress(int(100.0 * count_on / count_total))
        else:
            self.set_nw_progress(0)

    def set_nw_progress(self, v):
        self.ids.connection_progress.value = v
        if v == 100:
            self.ids.connection_progress.color = styles.app.color_success_green
        else:
            self.ids.connection_progress.color = self.theme_cls.primary_color
