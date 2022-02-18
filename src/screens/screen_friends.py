from kivy.properties import StringProperty, NumericProperty  # @UnresolvedImport

from kivymd.uix.list import OneLineIconListItem, IconLeftWidget

from lib import api_client

from components import screen

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

class CustomIconLeftWidget(IconLeftWidget):

    def set_size(self, interval):
        self.width = '36dp'
        self.height = '36dp'


class NewFriendItem(OneLineIconListItem):

    def on_pressed(self):
        if _Debug:
            print('NewFriendItem.on_pressed', self)
        screen.select_screen('search_people_screen')


class NewGroupItem(OneLineIconListItem):

    def on_pressed(self):
        if _Debug:
            print('NewGroupItem.on_pressed', self)
        screen.select_screen('create_group_screen')


class FriendItem(OneLineIconListItem):

    global_id = StringProperty()
    username = StringProperty()
    idhost = StringProperty()
    alias = StringProperty()
    contact_state = StringProperty()
    automat_index = NumericProperty()
    automat_id = StringProperty()

    def on_pressed(self):
        if _Debug:
            print('FriendItem.on_pressed', self)
        global_id = self.global_id
        username = self.username
        automat_index = self.automat_index or None
        automat_index = int(automat_index) if automat_index not in ['None', None, '', ] else None
        screen.select_screen(
            screen_id='private_chat_{}'.format(global_id),
            screen_type='private_chat_screen',
            global_id=global_id,
            username=username,
            automat_index=automat_index,
        )

#------------------------------------------------------------------------------

class FriendsScreen(screen.AppScreen):

    def get_title(self):
        return 'contacts'

    def get_icon(self):
        return 'account-box-multiple'

    def populate(self, *args, **kwargs):
        api_client.friends_list(cb=self.on_friends_list_result)

    def on_enter(self, *args):
        self.ids.state_panel.attach(automat_id='service_identity_propagate')
        self.populate()

    def on_leave(self, *args):
        self.ids.state_panel.release()

    def on_friend_state_changed(self, event_id, idurl, global_id, old_state, new_state):
        if _Debug:
            print('FriendsScreen.on_friend_state_changed', event_id, idurl, global_id)

    def on_friends_list_result(self, resp):
        if not isinstance(resp, dict):
            self.ids.friends_list_view.clear_widgets()
            return
        result = api_client.response_result(resp)
        if not result:
            self.ids.friends_list_view.clear_widgets()
            return
        self.ids.friends_list_view.clear_widgets()
        self.ids.friends_list_view.add_widget(NewGroupItem())
        self.ids.friends_list_view.add_widget(NewFriendItem())
        for one_friend in result:
            self.ids.friends_list_view.add_widget(FriendItem(
                global_id=one_friend['global_id'],
                username=one_friend['username'],
                idhost=one_friend['idhost'],
                alias=one_friend['alias'],
                contact_state=one_friend['contact_state'],
                automat_index=one_friend['index'],
                automat_id=one_friend['id'],
            ))

    # def on_drop_down_menu_item_clicked(self, btn):
    #     if _Debug:
    #         print('FriendsScreen.on_drop_down_menu_item_clicked', btn.icon)
    #     if btn.icon == 'account-plus':
    #         self.main_win().select_screen('search_people_screen')
