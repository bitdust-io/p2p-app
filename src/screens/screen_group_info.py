from lib import api_client

from components import screen
from components import snackbar

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

group_info_temlate_text = """
[size={text_size}][color=#909090]label:[/color]
{label}

[color=#909090]group ID:[/color]
{group_key_id}

[color=#909090]stream ID:[/color]
{active_queue_id}

[color=#909090]postman:[/color] {active_supplier_id}

[color=#909090]creator:[/color] {creator}

[color=#909090]participant:[/color] {participant_id}

[color=#909090]sequence head:[/color] {sequence_head}
[color=#909090]sequence tail:[/color] {sequence_tail}
[color=#909090]sequence count:[/color] {sequence_count}

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

    # def get_icon(self):
    #     return 'account-group'

    def get_title(self):
        l = self.label
        if len(l) > 20:
            l = l[:20] + '...'
        return l

    def get_statuses(self):
        return {
            None: 'group is currently inactive',
            'DHT_READ?': 'fetching list of active message brokers',
            'BROKERS?': 'connecting with message brokers',
            'QUEUE?': 'group is connected, reading recent messages',
            'IN_SYNC!': 'group is connected and synchronized',
            'DISCONNECTED': 'group is disconnected',
            'CLOSED': 'group is deactivated',
        }

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
        if not api_client.is_ok(resp):
            snackbar.error(text=api_client.response_err(resp))
            return
        result = api_client.response_result(resp)
        result.update(
            text_size='{}sp'.format(self.app().font_size_normal_absolute),
            small_text_size='{}sp'.format(self.app().font_size_small_absolute),
            label=result.get('label', ''),
            group_key_id=result.get('group_key_id', ''),
            active_supplier_id=result.get('active_supplier_id', ''),
            active_queue_id=result.get('active_queue_id', ''),
            creator=result.get('creator', ''),
            participant_id=result.get('participant_id', ''),
            state=result.get('state', ''),
            last_sequence_id=result.get('last_sequence_id', ''),
            sequence_head=result.get('sequence_head', '') or '',
            sequence_tail=result.get('sequence_tail', '') or '',
            sequence_count=result.get('sequence_count', '') or '',
        )
        self.ids.group_info_details.text = group_info_temlate_text.format(**result)

    def on_automat_state_changed(self, event_data):
        if _Debug:
            print('GroupInfoScreen.on_automat_state_changed', event_data)
        self.populate()
