from kivy.metrics import dp
from kivy.properties import StringProperty, NumericProperty  # @UnresolvedImport

from kivymd.uix.list import OneLineIconListItem, TwoLineIconListItem

from lib import api_client

from components import screen

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

class NewFriendItem(OneLineIconListItem):

    def on_pressed(self):
        if _Debug:
            print('NewFriendItem.on_pressed', self)
        screen.select_screen('search_people_screen')


class FriendItem(TwoLineIconListItem):

    global_id = StringProperty()
    username = StringProperty()
    idhost = StringProperty()
    alias = StringProperty()
    contact_state = StringProperty()
    automat_index = NumericProperty(None, allownone=True)
    automat_id = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.height = dp(48) if not self._height else self._height

    def get_secondary_text(self):
        sec_text = 'connecting...'
        sec_color = 'bbbf'
        if self.contact_state in ['CONNECTED', ]:
            sec_text = 'on-line'
            sec_color = 'adaf'
        elif self.contact_state in ['OFFLINE', ]:
            sec_text = 'offline'
        if _Debug:
            print('FriendItem.get_secondary_text', self.global_id, sec_text)
        return '[size=10sp][color=%s]%s[/color][/size]' % (sec_color, sec_text, )

    def on_pressed(self):
        if _Debug:
            print('FriendItem.on_pressed', self)
        automat_index = self.automat_index or None
        automat_index = int(automat_index) if automat_index not in ['None', None, '', ] else None
        screen.select_screen(
            screen_id='private_chat_{}'.format(self.global_id),
            screen_type='private_chat_screen',
            global_id=self.global_id,
            username=self.username,
            automat_index=automat_index,
        )


class FriendsScreen(screen.AppScreen):

    def get_title(self):
        return 'contacts'

    # def get_icon(self):
    #     return 'account-box-multiple'

    def get_statuses(self):
        return {
            None: 'network service is not started',
            'OFF': 'network service is switched off',
            'ON': 'list of contacts is synchronized',
            'NOT_INSTALLED': 'network services is not ready yet',
            'INFLUENCE': 'turning off dependent network services',
            'STARTING': 'network service is starting',
            'DEPENDS_OFF': 'related network services were not started yet',
            'STOPPING': 'network service is stopping',
            'CLOSED': 'network service is closed',
        }

    def populate(self, *args, **kwargs):
        api_client.friends_list(cb=self.on_friends_list_result)

    def on_created(self):
        api_client.add_model_listener('online_status', listener_cb=self.on_online_status)

    def on_destroying(self):
        api_client.remove_model_listener('online_status', listener_cb=self.on_online_status)

    def on_enter(self, *args):
        self.ids.state_panel.attach(automat_id='service_identity_propagate')
        self.populate()

    def on_leave(self, *args):
        self.ids.state_panel.release()

    def on_friends_list_result(self, resp):
        if _Debug:
            print('FriendsScreen.on_friends_list_result', resp)
        self.ids.friends_list_view.clear_widgets()
        self.ids.friends_list_view.add_widget(NewFriendItem())
        if not isinstance(resp, dict):
            return
        result = api_client.response_result(resp)
        if not result:
            return
        for one_friend in result:
            automat_index = one_friend.get('index')
            automat_index = int(automat_index) if automat_index not in ['None', None, '', ] else None
            self.ids.friends_list_view.add_widget(FriendItem(
                global_id=one_friend['global_id'],
                username=one_friend['username'],
                idhost=one_friend['idhost'],
                alias=one_friend['alias'],
                contact_state=one_friend['contact_state'],
                automat_index=automat_index,
                automat_id=one_friend.get('id') or '',
            ))

    def on_online_status(self, payload):
        if _Debug:
            print('FriendsScreen.on_online_status', payload)
        item_found = None
        for w in self.ids.friends_list_view.children:
            if isinstance(w, FriendItem):
                if w.global_id == payload['data']['global_id']:
                    item_found = w
                    break
        if item_found:
            prev_state = item_found.contact_state
            if prev_state != payload['data']['state']:
                item_found.contact_state = payload['data']['state']
                item_found.secondary_text = item_found.get_secondary_text()
                if _Debug:
                    print('FriendsScreen.on_online_status %r updated : %r -> %r' % (
                        item_found.global_id, prev_state, payload['data']['state'], ))
