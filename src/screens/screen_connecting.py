from kivy.metrics import dp, sp
from kivy.clock import Clock

#------------------------------------------------------------------------------

from components import screen
from components import styles
from components import buttons

from lib import api_client
from lib import websock

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

class ConnectingScreen(screen.AppScreen):

    verify_network_connected_task = None
    fetch_services_list_task = None
    known_services = {}

    def get_icon(self):
        return 'lan-pending'

    def get_title(self):
        return 'connecting...'

    def is_closable(self):
        return False

    def on_enter(self, *args):
        self.ids.state_panel.attach(automat_id='p2p_connector')
        Clock.schedule_once(self.schedule_nw_task)

    def on_leave(self, *args):
        self.ids.state_panel.release()
        self.unschedule_nw_task()

    def schedule_nw_task(self, *a, **kw):
        if not self.verify_network_connected_task:
            self.verify_network_connected_task = Clock.schedule_interval(self.control().verify_network_connected, 2)
        if not self.fetch_services_list_task:
            self.fetch_services_list_task = Clock.schedule_interval(self.populate, 0.33)

    def unschedule_nw_task(self, *a, **kw):
        self.known_services.clear()
        self.ids.services_list.clear_widgets()
        self.ids.progress_label.text = ''
        if self.fetch_services_list_task:
            Clock.unschedule(self.fetch_services_list_task)
            self.fetch_services_list_task = None
        if self.verify_network_connected_task:
            Clock.unschedule(self.verify_network_connected_task)
            self.verify_network_connected_task = None

    def populate(self, *args, **kwargs):
        if _Debug:
            print('ConnectingScreen.populate')
        api_client.services_list(cb=self.on_services_list_result)

    def get_service_color(self, st):
        clr = styles.app.color_btn_disabled
        if st == 'DEPENDS_OFF':
            clr = self.theme_cls.primary_light
        elif st in ['NOT_INSTALLED', 'OFF', ]:
            clr = styles.app.color_btn_disabled
        elif st in ['INFLUENCE', ]:
            clr = self.theme_cls.primary_light
        elif st in ['STARTING', 'STOPPING', ]:
            clr = styles.app.color_btn_pending_yellow_1
        else:
            clr = self.theme_cls.accent_light if st == 'ON' else self.theme_cls.primary_light
        return clr

    def switch_to_screen(self, next_screen):
        if _Debug:
            print('ConnectingScreen.switch_to_screen %r' % next_screen)
        self.known_services.clear()
        self.ids.services_list.clear_widgets()
        self.ids.progress_label.text = ''
        self.main_win().select_screen(next_screen)

    def on_services_list_result(self, resp):
        if _Debug:
            print('ConnectingScreen.on_services_list_result')
        self.known_services.clear()
        self.ids.services_list.clear_widgets()
        if not websock.is_ok(resp):
            return
        services_by_state = {}
        count_total = 0.0
        count_on = 0.0
        for svc in websock.response_result(resp):
            st = svc.get('state')
            if not svc.get('enabled'):
                continue
            if st not in services_by_state:
                services_by_state[st] = {}
            services_by_state[st][svc['name']] = svc
            count_total += 1.0
            if st == 'ON':
                count_on += 1.0
        self.ids.progress_label.text = '{} %'.format(int(100.0 * count_on / count_total))
        for st in ['ON', 'STARTING', 'DEPENDS_OFF', 'INFLUENCE', 'STOPPING', 'OFF', ]:
            for svc_name in sorted(services_by_state.get(st, {}).keys()):
                svc = services_by_state[st][svc_name]
                if svc.get('enabled'):
                    clr = self.get_service_color(svc.get('state'))
                else:
                    clr = styles.app.color_btn_disabled
                service_label = buttons.RoundedFlexWidthButton(text='')
                service_label.fixed_width = dp(11)
                service_label.fixed_height = dp(11)
                service_label.width = dp(11)
                service_label.height = dp(11)
                service_label.md_bg_color = clr
                self.ids.services_list.add_widget(service_label)
                self.known_services[svc['name']] = service_label

    def on_state_verify_success(self, next_screen):
        if _Debug:
            print('ConnectingScreen.on_state_verify_success, next_screen=%r' % next_screen)
        Clock.schedule_once(lambda *a: self.switch_to_screen(next_screen), 1)
