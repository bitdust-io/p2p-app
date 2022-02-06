from lib import api_client

from components import screen
from components import list_view

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

class FriendRecord(list_view.SelectableHorizontalRecord):
    pass


class FriendsListView(list_view.SelectableRecycleView):

    def on_selection_applied(self, item, index, is_selected, prev_selected):
        if self.selected_item:
            global_id = self.selected_item.global_id
            username = self.selected_item.username
            automat_index = self.selected_item.automat_index or None
            automat_index = int(automat_index) if automat_index not in ['None', None, '', ] else None
            screen.main_window().select_screen(
                screen_id='private_chat_{}'.format(global_id),
                screen_type='private_chat_screen',
                global_id=global_id,
                username=username,
                automat_index=automat_index,
            )
        self.clear_selection()
        self.ids.selectable_layout.clear_selection()


class FriendsScreen(screen.AppScreen):

    def get_title(self):
        return 'contacts'

    def get_icon(self):
        return 'account-box-multiple'

    def populate(self, *args, **kwargs):
        api_client.friends_list(cb=self.on_friends_list_result)

    def clear_selected_item(self):
        self.ids.friends_list_view.clear_selection()
        self.ids.friends_list_view.ids.selectable_layout.clear_selection()

    def on_enter(self, *args):
        self.ids.state_panel.attach(automat_id='service_identity_propagate')
        self.clear_selected_item()
        self.populate()

    def on_leave(self, *args):
        self.ids.state_panel.release()
        self.clear_selected_item()

    def on_friends_list_result(self, resp):
        if not api_client.is_ok(resp):
            self.clear_selected_item()
            self.ids.friends_list_view.data = []
            return
        friends_list = api_client.response_result(resp)
        for one_friend in friends_list:
            one_friend['automat_index'] = str(one_friend.pop('index', ''))
            one_friend['automat_id'] = str(one_friend.pop('id', ''))
            item_found = False
            for i in range(len(self.ids.friends_list_view.data)):
                item = self.ids.friends_list_view.data[i]
                if item['idurl'] == one_friend['idurl']:
                    item_found = True
                    break
            if item_found:
                self.ids.friends_list_view.data[i] = one_friend
                continue
            self.ids.friends_list_view.data.append(one_friend)
        to_be_removed = []
        for item in self.ids.friends_list_view.data:
            item_found = False
            for one_friend in friends_list:
                if one_friend['idurl'] == item['idurl']:
                    item_found = True
                    break
            if item_found:
                continue
            to_be_removed.append(item)
        for item in to_be_removed:
            self.ids.friends_list_view.data.remove(item)
        self.ids.friends_list_view.refresh_from_data()

    def on_state_changed(self, event_data):
        if _Debug:
            print('FriendsScreen.on_state_changed', event_data)

    def on_friend_state_changed(self, event_id, idurl, global_id, old_state, new_state):
        if _Debug:
            print('FriendsScreen.on_friend_state_changed', event_id, idurl, global_id)
        item_found = False
        for i in range(len(self.ids.friends_list_view.data)):
            item = self.ids.friends_list_view.data[i]
            if item['idurl'] == idurl:
                item_found = True
                prev_state = self.ids.friends_list_view.data[i]['contact_state']
                self.ids.friends_list_view.data[i]['contact_state'] = new_state
                if _Debug:
                    print('FriendsScreen.on_friend_state_changed %r updated : %r -> %r' % (idurl, prev_state, new_state, ))
                break
        if not item_found:
            self.populate()
        else:
            self.ids.friends_list_view.refresh_from_data()

    def on_drop_down_menu_item_clicked(self, btn):
        if _Debug:
            print('FriendsScreen.on_drop_down_menu_item_clicked', btn.icon)
        if btn.icon == 'account-plus':
            self.main_win().select_screen('search_people_screen')
