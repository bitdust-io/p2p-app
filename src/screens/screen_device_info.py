from kivy.core.clipboard import Clipboard

#------------------------------------------------------------------------------

from lib import api_client
from lib import util

from components import screen
from components import snackbar

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

device_info_temlate_text = """

[size={text_size}]{name}

[color=#909090]authorized:[/color] {authorized}

[color=#909090]connection info:[/color] [size={large_text_size}][font=RobotoMono-Regular]{url}[/font][/size]   [u][color=#0000ff][ref=copy_url][copy to clipboard][/ref][/color][/u]

Scan the QR code above using the BitDust p2p-app on your mobile device and be ready to enter the 6-digit verification code to authorize your mobile device.

You can also manually enter the connection info specified above on your remote device.[/size]
"""


class DeviceInfoScreen(screen.AppScreen):

    def __init__(self, **kwargs):
        if _Debug:
            print('DeviceInfoScreen.__init__', kwargs)
        self.device_name = ''
        self.automat_index = None
        self.automat_id = None
        self.url = ''
        self.deleted = False
        super(DeviceInfoScreen, self).__init__(**kwargs)

    def init_kwargs(self, **kw):
        if _Debug:
            print('DeviceInfoScreen.init_kwargs', kw)
        if not self.device_name and kw.get('device_name'):
            self.device_name = kw.pop('device_name', '')
        if 'automat_index' in kw:
            self.automat_index = kw.pop('automat_index', None)
        if 'automat_id' in kw:
            self.automat_id = kw.pop('automat_id', None)
        return kw

    # def get_icon(self):
    #     return 'account-group'

    def get_title(self):
        l = self.device_name
        if len(l) > 20:
            l = l[:20] + '...'
        return l

    def get_statuses(self):
        return {
            None: 'device is not ready',
            'AT_STARTUP': 'device is not ready',
            'ROUTERS?': 'connecting with other nodes',
            'WEB_SOCKET?': 'establishing websocket connections',
            'CLIENT_PUB?': 'ready to start authorization process',
            'SERVER_CODE?': 'authorization is in progress',
            'CLIENT_CODE?': 'waiting confirmation from remote device',
            'READY': 'device is authorized',
            'CLOSED': 'device is currently disabled',
        }

    def on_enter(self, *args):
        self.ids.state_panel.attach(automat_id=self.automat_id, callback_automat_state_changed=self.on_automat_state_changed)
        self.populate()

    def on_leave(self, *args):
        self.ids.state_panel.release()

    def populate(self, **kwargs):
        if _Debug:
            print('DeviceInfoScreen.populate')
        if self.deleted:
            return
        api_client.device_info(
            name=self.device_name,
            cb=self.on_device_info_result,
        )

    def on_device_info_result(self, resp):
        if _Debug:
            print('DeviceInfoScreen.on_device_info_result', resp)
        self.url = ''
        if not api_client.is_ok(resp):
            snackbar.error(text=api_client.response_err(resp))
            return
        result = api_client.result(resp)
        connected_routers = result.get('instance', {}).get('connected_routers', []) or []
        self.url = connected_routers[0] if connected_routers else ''
        result.update(
            text_size='{}sp'.format(self.app().font_size_normal_absolute),
            small_text_size='{}sp'.format(self.app().font_size_small_absolute),
            large_text_size='{}sp'.format(self.app().font_size_large_absolute),
            name=result.get('name', ''),
            state=result.get('instance', {}).get('state', '') or 'CLOSED',
            url=util.pack_device_url(self.url),
            authorized='yes' if result.get('meta', {}).get('auth_token') else 'no',
        )
        if _Debug:
            print('DeviceInfoScreen.on_device_info_result result updated:', result)
        self.ids.device_info_details.text = device_info_temlate_text.format(**result)
        self.ids.qr_code_image.data = util.pack_device_url(self.url)

    def on_automat_state_changed(self, event_data):
        if _Debug:
            print('DeviceInfoScreen.on_automat_state_changed', event_data)
        self.populate()

    def on_device_info_details_ref_pressed(self, *args):
        if _Debug:
            print('DeviceInfoScreen.on_device_info_details_ref_pressed', args)
        if args[1] == 'copy_url':
            if self.url:
                Clipboard.copy(util.pack_device_url(self.url))

    def on_drop_down_menu_item_clicked(self, btn):
        if _Debug:
            print('DeviceInfoScreen.on_drop_down_menu_item_clicked', btn.icon)
        if btn.icon == 'qrcode-remove':
            api_client.device_remove(
                name=self.device_name,
                cb=self.on_device_remove_result,
            )

    def on_device_remove_result(self, resp):
        if _Debug:
            print('DeviceInfoScreen.on_device_remove_result', resp)
        self.deleted = True
        screen.select_screen('settings_screen')
        screen.close_screen(screen_id='device_info_{}'.format(self.device_name))
        screen.stack_clear()
        screen.stack_append('welcome_screen')
