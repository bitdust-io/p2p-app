from kivy.metrics import dp
from kivy.properties import StringProperty, NumericProperty  # @UnresolvedImport

from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.list import TwoLineIconListItem

from lib import api_client

from components import screen

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

class NewShareItem(OneLineIconListItem):

    def on_pressed(self):
        if _Debug:
            print('NewShareItem.on_pressed', self)
        screen.select_screen('create_share_screen')


class ShareItem(TwoLineIconListItem):

    key_id = StringProperty()
    label = StringProperty()
    alias = StringProperty()
    share_state = StringProperty()
    automat_index = NumericProperty(None, allownone=True)
    automat_id = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.height = dp(48) if not self._height else self._height

    def get_secondary_text(self):
        sec_text = 'connecting...'
        sec_color = 'bbbf'
        if self.share_state in ['CONNECTED', ]:
            sec_text = 'connected'
            sec_color = 'adaf'
        elif self.share_state in ['DISCONNECTED', 'CLOSED', ]:
            sec_text = 'disconnected'
        elif self.share_state in [None, '', ]:
            sec_text = 'closed'
        if _Debug:
            print('ShareItem.get_secondary_text', self.key_id, self.share_state, sec_text)
        return '[size=10sp][color=%s]%s[/color][/size]' % (sec_color, sec_text, )

    def on_pressed(self):
        if _Debug:
            print('ShareItem.on_pressed', self)
        automat_index = self.automat_index or None
        automat_index = int(automat_index) if automat_index not in ['None', None, '', ] else None
        screen.select_screen(
            screen_id='shared_location_{}'.format(self.key_id),
            screen_type='shared_location_screen',
            key_id=self.key_id,
            label=self.label,
            automat_index=automat_index,
            automat_id=self.automat_id,
        )


class SharesScreen(screen.AppScreen):

    def get_title(self):
        return 'shared locations'

    # def get_icon(self):
    #     return 'account-box-multiple'

    def populate(self, *args, **kwargs):
        api_client.shares_list(cb=self.on_shares_list_result)

    def on_created(self):
        api_client.add_model_listener('shared_location', listener_cb=self.on_shared_location)

    def on_destroying(self):
        api_client.remove_model_listener('shared_location', listener_cb=self.on_shared_location)

    def on_enter(self, *args):
        self.ids.state_panel.attach(automat_id='service_shared_data')
        self.populate()

    def on_leave(self, *args):
        self.ids.state_panel.release()

    def on_shares_list_result(self, resp):
        if _Debug:
            print('SharesScreen.on_shares_list_result', resp)
        self.ids.shares_list_view.clear_widgets()
        self.ids.shares_list_view.add_widget(NewShareItem())
        if not isinstance(resp, dict):
            return
        result = api_client.response_result(resp)
        if not result:
            return
        for one_share in result:
            automat_index = one_share.get('index')
            automat_index = int(automat_index) if automat_index not in ['None', None, '', ] else None
            self.ids.shares_list_view.add_widget(ShareItem(
                key_id=one_share['key_id'],
                label=one_share['label'],
                alias=one_share['alias'],
                share_state=one_share.get('state') or '',
                automat_index=automat_index,
                automat_id=one_share.get('id') or '',
            ))

    def on_shared_location(self, payload):
        if _Debug:
            print('SharesScreen.on_shared_location', payload, self.ids.shares_list_view.children)
        item_found = None
        for w in self.ids.shares_list_view.children:
            if isinstance(w.instance_item, ShareItem):
                if w.instance_item.key_id == payload['data']['key_id']:
                    item_found = w
                    break
        if item_found:
            prev_state = item_found.instance_item.share_state
            if prev_state != payload['data']['state']:
                item_found.instance_item.share_state = payload['data']['state']
                item_found.instance_item.secondary_text = item_found.instance_item.get_secondary_text()
                if _Debug:
                    print('SharesScreen.on_shared_location %r updated : %r -> %r' % (
                        item_found.instance_item.key_id, prev_state, payload['data']['state'], ))
