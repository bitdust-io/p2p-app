from lib import api_client

from components import screen
from components import snackbar

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

class DeviceAddScreen(screen.AppScreen):

    # def get_icon(self):
    #     return 'chat-plus'

    def get_title(self):
        return 'add new device'

    def clean_view(self, clear_input_field=False):
        if clear_input_field:
            self.ids.device_name_input.text = ''
            self.ids.device_name_input.focus = True
            self.ids.routed_connection_switch_button.active = True
            self.ids.port_number_input.text = '8282'

    def on_enter(self):
        self.clean_view(clear_input_field=True)

    def on_add_device_button_clicked(self, *args):
        if _Debug:
            print('DeviceAddScreen.on_add_device_button_clicked', args, self.ids.device_name_input.text, self.ids.routed_connection_switch_button.active, int(self.ids.port_number_input.text))
        if not self.ids.device_name_input.text:
            self.ids.device_name_input.focus = True
            return
        api_client.device_add(
            name=self.ids.device_name_input.text.replace(' ', '_'),
            routed=self.ids.routed_connection_switch_button.active,
            activate=True,
            wait_listening=False,
            web_socket_port=int(self.ids.port_number_input.text),
            cb=self.on_device_add_result,
        )

    def on_device_add_result(self, resp):
        if _Debug:
            print('DeviceAddScreen.on_device_add_result', resp)
        if not api_client.is_ok(resp):
            snackbar.error(text=api_client.response_err(resp))
            return
        r = api_client.result(resp)
        screen.select_screen(
            screen_id='device_info_{}'.format(r['name']),
            screen_type='device_info_screen',
            device_name=r['name'],
            automat_index=r.get('instance', {}).get('index'),
            automat_id=r.get('instance', {}).get('id'),
        )
        screen.close_screen('device_add_screen')
        screen.stack_clear()
        screen.stack_append('welcome_screen')

    def on_routed_connection_switch_button_changed(self, *args):
        if _Debug:
            print('DeviceAddScreen.on_routed_connection_switch_button_changed', args)
        self.ids.port_number_input.disabled = args[0]
