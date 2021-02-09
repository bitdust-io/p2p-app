from components.buttons import TransparentIconButton
from components.screen import AppScreen
from components.list_view import SelectableRecycleView, SelectableHorizontalRecord

from lib import api_client
from lib import websock

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

class FriendActionButton(TransparentIconButton):
    pass


class FriendRecord(SelectableHorizontalRecord):

    def __init__(self, **kwargs):
        super(FriendRecord, self).__init__(**kwargs)
        self.visible_buttons = []

    def get_root(self):
        return self.parent.parent.parent.parent.parent.parent

    def show_buttons(self):
        if not self.visible_buttons:
            chat_button = FriendActionButton(
                icon='comment-multiple',
                on_release=self.on_chat_button_clicked,
            )
            self.visible_buttons.append(chat_button)
            self.add_widget(chat_button)
            delete_button = FriendActionButton(
                icon='trash-can',
                on_release=self.on_delete_button_clicked,
            )
            self.visible_buttons.append(delete_button)
            self.add_widget(delete_button)

    def hide_buttons(self):
        if self.visible_buttons:
            for w in self.visible_buttons:
                self.remove_widget(w)
            self.visible_buttons.clear()

    def on_chat_button_clicked(self, *args):
        self.get_root().main_win().select_screen(
            screen_id='private_chat_{}'.format(self.global_id),
            screen_type='private_chat_screen',
            global_id=self.global_id,
            username=self.username,
        )

    def on_delete_button_clicked(self, *args):
        self.get_root().main_win().close_screen(
            screen_id='private_chat_{}'.format(self.global_id),
        )
        self.parent.clear_selection()
        api_client.friend_remove(global_user_id=self.global_id, cb=self.on_friend_remove_result)

    def on_friend_remove_result(self, resp):
        self.get_root().ids.status_label.from_api_response(resp)
        self.get_root().populate()


class FriendsListView(SelectableRecycleView):

    def on_selection_applied(self, item, index, is_selected, prev_selected):
        if is_selected != prev_selected:
            if is_selected:
                item.show_buttons()
            else:
                item.hide_buttons()


class FriendsScreen(AppScreen):

    def get_title(self):
        return 'contacts'

    def get_icon(self):
        return 'account-box-multiple'

    def populate(self, *args, **kwargs):
        api_client.friends_list(cb=self.on_friends_list_result)

    def clear_selected_item(self):
        if self.ids.friends_list_view.selected_item:
            self.ids.friends_list_view.selected_item.hide_buttons()
            self.ids.friends_list_view.selected_item.selected = False
        self.ids.friends_list_view.clear_selection()

    def on_enter(self, *args):
        self.clear_selected_item()
        self.populate()

    def on_leave(self, *args):
        self.clear_selected_item()

    def on_friends_list_result(self, resp):
        self.ids.status_label.from_api_response(resp)
        if not websock.is_ok(resp):
            self.clear_selected_item()
            self.ids.friends_list_view.data = []
            return
        friends_list = websock.response_result(resp)
        for one_friend in friends_list:
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

    def on_search_people_button_clicked(self, *args):
        self.main_win().select_screen('search_people_screen')

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
                if old_state != prev_state:
                    if _Debug:
                        print('FriendsScreen.on_friend_state_changed WARNING prev_state was %r, but expected %r' % (prev_state, old_state, ))
                self.ids.friends_list_view.data[i]['contact_state'] = new_state
                if _Debug:
                    print('FriendsScreen.on_friend_state_changed %r updated : %r -> %r' % (idurl, prev_state, new_state, ))
                break
        if not item_found:
            self.populate()
        else:
            self.ids.friends_list_view.refresh_from_data()

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder
Builder.load_file('./screens/screen_friends.kv')
