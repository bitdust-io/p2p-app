from kivy.properties import StringProperty, NumericProperty  # @UnresolvedImport
from kivymd.uix.list import OneLineIconListItem

#------------------------------------------------------------------------------

from lib import api_client

from components import screen

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

class SelectFriendItem(OneLineIconListItem):

    global_id = StringProperty()
    username = StringProperty()
    idhost = StringProperty()
    alias = StringProperty()
    contact_state = StringProperty()
    automat_index = NumericProperty(None, allownone=True)
    automat_id = StringProperty()

    def on_pressed(self):
        if _Debug:
            print('SelectFriendItem.on_pressed', self)
        if self.parent.parent.parent.parent.parent.parent.result_callback:
            self.parent.parent.parent.parent.parent.parent.result_callback(self.global_id)

#------------------------------------------------------------------------------

class SelectFriendScreen(screen.AppScreen):

    screen_header = StringProperty('Select user')

    def init_kwargs(self, **kw):
        self.result_callback = kw.pop('result_callback', None)
        self.screen_header = kw.pop('screen_header', '')
        return kw

    def get_title(self):
        return 'select contact'

    def get_icon(self):
        return 'target-account'

    def populate(self, *args, **kwargs):
        api_client.friends_list(cb=self.on_friends_list_result)

    def on_enter(self, *args):
        self.ids.state_panel.attach(automat_id='service_identity_propagate')
        self.populate()

    def on_leave(self, *args):
        self.ids.state_panel.release()

    def on_friends_list_result(self, resp):
        if not isinstance(resp, dict):
            self.ids.friends_list_view.clear_widgets()
            return
        result = api_client.response_result(resp)
        if not result:
            self.ids.friends_list_view.clear_widgets()
            return
        self.ids.friends_list_view.clear_widgets()
        for one_friend in result:
            self.ids.friends_list_view.add_widget(SelectFriendItem(
                global_id=one_friend['global_id'],
                username=one_friend['username'],
                idhost=one_friend['idhost'],
                alias=one_friend['alias'],
                contact_state=one_friend['contact_state'],
                automat_index=one_friend.get('index') or None,
                automat_id=one_friend.get('id') or '',
            ))
