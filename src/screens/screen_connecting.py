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
    known_services = {}

    def get_icon(self):
        return 'lan-pending'

    def get_title(self):
        return 'connecting...'

    def is_closable(self):
        return False

    def on_enter(self, *args):
        self.ids.state_panel.attach(automat_id='p2p_connector')
        if not self.verify_network_connected_task:
            self.verify_network_connected_task = Clock.schedule_interval(self.control().verify_network_connected, 1)
        self.populate()

    def on_leave(self, *args):
        self.ids.state_panel.release()
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

    def on_services_list_result(self, resp):
        if _Debug:
            print('ConnectingScreen.on_services_list_result')
        self.known_services.clear()
        self.ids.services_list.clear_widgets()
        if not websock.is_ok(resp):
            Clock.schedule_once(self.populate, 0.2)
            return
        for svc in websock.response_result(resp):
            if svc.get('enabled'):
                clr = self.get_service_color(svc.get('state'))
            else:
                clr = styles.app.color_btn_disabled
            service_label = buttons.RoundedFlexWidthButton(
                text=svc['name'].replace('service_', ''),
            )
            service_label.md_bg_color = clr
            self.ids.services_list.add_widget(service_label)
            self.known_services[svc['name']] = service_label

    def on_service_state_changed(self, event_data):
        if _Debug:
            print('ConnectingScreen.on_service_state_changed', len(self.known_services), event_data)
        service_name = event_data.get('id')
        if service_name in self.known_services:
            self.known_services[service_name].md_bg_color = self.get_service_color(event_data['newstate'])
