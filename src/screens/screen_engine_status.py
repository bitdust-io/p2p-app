from kivy.clock import Clock

#------------------------------------------------------------------------------

from lib import api_client

from components import screen
from components import styles

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

class EngineStatusScreen(screen.AppScreen):

    verify_process_health_task = None
    fetch_services_list_task = None
    state_panel_attached = False

    # def get_icon(self):
    #     return 'heart-pulse'

    def get_title(self):
        return 'status'

    def is_closable(self):
        return False

    def on_enter(self, *args):
        if _Debug:
            print('EngineStatusScreen.on_enter')
        Clock.schedule_once(self.control().verify_process_health)
        if not self.verify_process_health_task:
            self.verify_process_health_task = Clock.schedule_interval(self.control().verify_process_health, 5)
        if self.main_win().engine_is_on:
            Clock.schedule_once(self.schedule_nw_task)
            self.state_panel_attached = self.ids.state_panel.attach(automat_id='initializer')

    def on_leave(self, *args):
        if _Debug:
            print('EngineStatusScreen.on_leave')
        self.ids.state_panel.release()
        self.state_panel_attached = False
        self.unschedule_nw_task()
        if self.verify_process_health_task:
            Clock.unschedule(self.verify_process_health_task)
            self.verify_process_health_task = None

    def on_engine_on_off(self, *args):
        if _Debug:
            print('EngineStatusScreen.on_engine_on_off', args)
        st = args[0]
        if st:
            self.app().start_engine()
            Clock.schedule_once(self.schedule_nw_task, 0.5)
            self.state_panel_attached = self.ids.state_panel.attach(automat_id='initializer')
        else:
            self.set_nw_progress(0)
            self.ids.state_panel.release()
            self.state_panel_attached = False
            self.unschedule_nw_task()
            self.app().stop_engine()

    def on_network_connection_status_pressed(self, *args):
        if _Debug:
            print('EngineStatusScreen.on_network_connection_status_pressed', args)
        self.main_win().select_screen('connecting_screen')

    def on_services_list_result(self, resp):
        if _Debug:
            print('EngineStatusScreen.on_services_list_result')
        if not self.main_win().engine_is_on:
            self.set_nw_progress(0)
            return
        if not api_client.is_ok(resp):
            self.set_nw_progress(0)
            return
        services_by_state = {}
        count_total = 0.0
        count_on = 0.0
        for svc in api_client.response_result(resp):
            st = svc.get('state')
            if not svc.get('enabled'):
                continue
            if st not in services_by_state:
                services_by_state[st] = {}
            services_by_state[st][svc['name']] = svc
            count_total += 1.0
            if st == 'ON':
                count_on += 1.0
        self.set_nw_progress(int(100.0 * count_on / count_total))

    def set_nw_progress(self, v):
        self.ids.connection_progress.value = v
        if v == 100:
            self.ids.connection_progress.color = styles.app.color_success_green
        else:
            self.ids.connection_progress.color = self.theme_cls.primary_color

    def schedule_nw_task(self, *a, **kw):
        if _Debug:
            print('EngineStatusScreen.schedule_nw_task state_panel_attached=%r' % self.state_panel_attached)
        if not self.fetch_services_list_task:
            self.fetch_services_list_task = Clock.schedule_interval(self.populate_nw_services, 0.5)

    def unschedule_nw_task(self, *a, **kw):
        # self.set_nw_progress(0)
        if self.fetch_services_list_task:
            Clock.unschedule(self.fetch_services_list_task)
            self.fetch_services_list_task = None

    def populate_nw_services(self, *args, **kwargs):
        if _Debug:
            print('EngineStatusScreen.populate_nw_services state_panel_attached=%r' % self.state_panel_attached)
        if self.main_win().state_process_health == 1:
            api_client.services_list(cb=self.on_services_list_result)
            if not self.state_panel_attached:
                self.state_panel_attached = self.ids.state_panel.attach(automat_id='initializer')
