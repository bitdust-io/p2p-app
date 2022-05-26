from kivy.properties import StringProperty, NumericProperty  # @UnresolvedImport

from kivymd.uix.list import OneLineIconListItem

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


class ShareItem(OneLineIconListItem):

    key_id = StringProperty()
    label = StringProperty()
    alias = StringProperty()
    share_state = StringProperty()
    automat_index = NumericProperty(None, allownone=True)
    automat_id = StringProperty()

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
        )


class SharesScreen(screen.AppScreen):

    def get_title(self):
        return 'shared locations'

    # def get_icon(self):
    #     return 'account-box-multiple'

    def populate(self, *args, **kwargs):
        api_client.shares_list(cb=self.on_shares_list_result)

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
