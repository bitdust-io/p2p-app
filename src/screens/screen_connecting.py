from kivy.clock import Clock

#------------------------------------------------------------------------------

from lib import api_client

from components import screen
from components import styles
from components import buttons

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------


class NetworkServiceElement(buttons.CustomRaisedFlexButton):
    pass


class ConnectingScreen(screen.AppScreen):

    known_services = {}
    state_panel_attached = False

    # def get_icon(self):
    #     return 'lan-pending'

    def get_title(self):
        return 'network services'

    def get_statuses(self):
        return {
            None: 'peer-to-peer connection not yet established',
            'AT_STARTUP': 'starting the application',
            'NETWORK?': 'checking connection to the Internet',
            'INCOMMING?': 'waiting initial reply from other nodes',
            'CONNECTED': 'peer-to-peer network services are started',
            'DISCONNECTED': 'disconnected',
            'MY_IDENTITY': 'verifying my identity in the network',
            'PROPAGATE': 'propagating my identity to other nodes',
        }

    def is_closable(self):
        return False

    def populate(self, *args, **kwargs):
        if _Debug:
            print('ConnectingScreen.populate')
        if not self.state_panel_attached:
            self.state_panel_attached = self.ids.state_panel.attach(automat_id='p2p_connector')
        for snap_info in self.model('service').values():
            if snap_info:
                self.on_service(snap_info)

    def on_enter(self, *args):
        if not self.state_panel_attached:
            self.state_panel_attached = self.ids.state_panel.attach(automat_id='p2p_connector')
        api_client.add_model_listener('service', listener_cb=self.on_service)
        self.populate()

    def on_leave(self, *args):
        api_client.remove_model_listener('service', listener_cb=self.on_service)
        if self.state_panel_attached:
            self.ids.state_panel.release()
        self.state_panel_attached = False

    def on_service(self, payload):
        if _Debug:
            print('ConnectingScreen.on_services_list_result', len(self.known_services))
        services_by_state = {}
        services_by_name = {}
        svc = payload['data']
        st = svc.get('state')
        if st not in services_by_state:
            services_by_state[st] = {}
        services_by_state[st][svc['name']] = svc
        services_by_name[svc['name']] = svc
        if not self.known_services:
            for st in ['ON', 'STARTING', 'DEPENDS_OFF', 'INFLUENCE', 'STOPPING', 'OFF', ]:
                for svc_name in sorted(services_by_state.get(st, {}).keys()):
                    svc = services_by_state[st][svc_name]
                    if svc.get('enabled'):
                        clr = self.get_service_color(svc.get('state'))
                    else:
                        clr = styles.app.color_btn_disabled
                    lbl = self.get_service_label(svc)
                    service_label = NetworkServiceElement(text=lbl)
                    service_label.md_bg_color = clr
                    self.ids.services_list.add_widget(service_label)
                    self.known_services[svc['name']] = service_label
        else:
            for svc_name in services_by_name.keys():
                svc = services_by_name[svc_name]
                if svc.get('enabled'):
                    clr = self.get_service_color(svc.get('state'))
                else:
                    clr = styles.app.color_btn_disabled
                service_label = self.known_services.get(svc['name'])
                if not service_label:
                    lbl = self.get_service_label(svc)
                    service_label = NetworkServiceElement(text=lbl)
                    service_label.md_bg_color = clr
                    self.ids.services_list.add_widget(service_label)
                    self.known_services[svc['name']] = service_label
                else:
                    service_label.md_bg_color = clr
        services_by_name.clear()
        services_by_state.clear()

    def get_service_label(self, svc):
        txt = '[size=14sp][b]{}[/b][/size]'.format(svc['name'].replace('service_', ''))
        if svc['depends']:
            txt += '[size=10sp][color=#888888]\ndepend on:[/color]'
            for d in svc['depends']:
                txt += '\n[color=#555555] + {}[/color]'.format(d.replace('service_', ''))
            txt += '[/size]'
        return txt

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
