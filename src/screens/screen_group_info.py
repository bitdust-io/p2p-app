from components import screen
from components import snackbar

from lib import api_client
from lib import websock

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

group_info_temlate_text = """
[size={text_size}][color=#909090]label:[/color] {label}

[color=#909090]group ID:[/color] {group_key_id}

[color=#909090]active broker id:[/color] {active_broker_id}

[color=#909090]connected brokers:[/color]
{connected_brokers}

[color=#909090]creator:[/color] {creator}

[color=#909090]archive folder path:[/color] {archive_folder_path}

[color=#909090]sequence ID:[/color] {last_sequence_id}

[color=#909090]state:[/color] {state}
[/size]
"""


class GroupInfoScreen(screen.AppScreen):

    def __init__(self, **kwargs):
        self.global_id = ''
        self.label = ''
        self.automat_index = None
        self.automat_id = None
        super(GroupInfoScreen, self).__init__(**kwargs)

    def init_kwargs(self, **kw):
        if not self.global_id and kw.get('global_id'):
            self.global_id = kw.pop('global_id', '')
        if not self.label and kw.get('label'):
            self.label = kw.pop('label', '')
        if 'automat_index' in kw:
            self.automat_index = kw.pop('automat_index', None)
        if 'automat_id' in kw:
            self.automat_id = kw.pop('automat_id', None)
        return kw

    def get_icon(self):
        return 'account-group'

    def get_title(self):
        l = self.label
        if len(l) > 20:
            l = l[:20] + '...'
        return l

    def on_enter(self, *args):
        self.ids.state_panel.attach(automat_id=self.automat_id, callback_automat_state_changed=self.on_automat_state_changed)
        self.populate()

    def on_leave(self, *args):
        self.ids.state_panel.release()

    def populate(self, **kwargs):
        api_client.group_info(
            group_key_id=self.global_id,
            cb=self.on_group_info_result,
        )

    def on_group_info_result(self, resp):
        if not websock.is_ok(resp):
            snackbar.error(text=websock.response_err(resp))
            return
        result = websock.response_result(resp)
        result.update(
            text_size='{}sp'.format(self.app().font_size_normal_absolute),
            small_text_size='{}sp'.format(self.app().font_size_small_absolute),
            connected_brokers=('\n'.join(result.get('connected_brokers', {}).values())),
        )
        self.ids.group_info_details.text = group_info_temlate_text.format(**result)

    def on_automat_state_changed(self, event_data):
        if _Debug:
            print('GroupInfoScreen.on_automat_state_changed', event_data)
        self.populate()
