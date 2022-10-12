from lib import api_client

from components import screen
from components import snackbar

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

shared_location_info_temlate_text = """
[size={text_size}][color=#909090]label:[/color] {label}

[color=#909090]key ID:[/color] {key_id}

[color=#909090]creator:[/color] {creator}

[color=#909090]state:[/color] {state}

[color=#909090]connected suppliers:[/color]
{suppliers}

[color=#909090]ECC map:[/color] {ecc_map}
[/size]
"""


class SharedLocationInfoScreen(screen.AppScreen):

    def __init__(self, **kwargs):
        self.key_id = ''
        self.label = ''
        self.automat_index = None
        self.automat_id = None
        super(SharedLocationInfoScreen, self).__init__(**kwargs)

    def init_kwargs(self, **kw):
        if not self.key_id and kw.get('key_id'):
            self.key_id = kw.pop('key_id', '')
        if not self.label and kw.get('label'):
            self.label = kw.pop('label', '')
        if 'automat_index' in kw:
            self.automat_index = kw.pop('automat_index', None)
        if 'automat_id' in kw:
            self.automat_id = kw.pop('automat_id', None)
        return kw

    # def get_icon(self):
    #     return 'account-group'

    def get_title(self):
        l = self.label
        if len(l) > 20:
            l = l[:20] + '...'
        return l

    def get_statuses(self):
        return {
            None: 'shared files are not available at the moment',
            'AT_STARTUP': 'shared files are not available at the moment',
            'DHT_LOOKUP': 'connecting to the distributed hash table',
            'SUPPLIERS?': 'connecting with remote suppliers',
            'DISCONNECTED': 'shared location is disconnected',
            'CONNECTED': 'shared location is synchronized',
            'CLOSED': 'shared location is not active',
        }

    def on_enter(self, *args):
        self.ids.state_panel.attach(automat_id=self.automat_id, callback_automat_state_changed=self.on_automat_state_changed)
        self.populate()

    def on_leave(self, *args):
        self.ids.state_panel.release()

    def populate(self, **kwargs):
        api_client.share_info(
            key_id=self.key_id,
            cb=self.on_shared_location_info_result,
        )

    def on_shared_location_info_result(self, resp):
        if not api_client.is_ok(resp):
            snackbar.error(text=api_client.response_err(resp))
            return
        result = api_client.result(resp)
        result.update(
            text_size='{}sp'.format(self.app().font_size_normal_absolute),
            small_text_size='{}sp'.format(self.app().font_size_small_absolute),
            suppliers=('\n'.join(result.get('suppliers', []))),
            key_id=result.get('key_id', ''),
            creator=result.get('creator', ''),
            state=result.get('state', '') or 'CLOSED',
            ecc_map=result.get('ecc_map', '') or 'unknown'
        )
        self.ids.shared_location_info_details.text = shared_location_info_temlate_text.format(**result)

    def on_automat_state_changed(self, event_data):
        if _Debug:
            print('SharedLocationInfoScreen.on_automat_state_changed', event_data)
        self.populate()
