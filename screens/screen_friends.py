from components.buttons import RoundedButton
from components.screen import AppScreen
from components.list_view import SelectableRecycleView, SelectableRecord
from components.webfont import fa_icon

from service import api_client

#------------------------------------------------------------------------------

class FriendActionButton(RoundedButton):

    pass



class FriendsScreen(AppScreen):

    def populate(self):
        api_client.friends_list(cb=self.on_friends_list_result)

    def on_pre_enter(self, *args):
        self.populate()

    def on_friends_list_result(self, resp):
        if not isinstance(resp, dict):
            self.ids.friends_list_view.data = []
            return
        result = resp.get('payload', {}).get('response' , {}).get('result', {})
        if not result:
            self.ids.friends_list_view.data = []
            return
        self.ids.friends_list_view.data = []
        for one_friend in result:
            self.ids.friends_list_view.data.append(one_friend)


class FriendRecord(SelectableRecord):

    visible_buttons = []

    def show_buttons(self):
        if not self.visible_buttons:
            chat_button = FriendActionButton(
                text=fa_icon('comments'),
                on_release=self.on_chat_button_clicked,
            )
            self.visible_buttons.append(chat_button)
            self.add_widget(chat_button)
            delete_button = FriendActionButton(
                text=fa_icon('trash'),
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
        print('on_chat_button_clicked')

    def on_delete_button_clicked(self, *args):
        print('on_delete_button_clicked')


class FriendsListView(SelectableRecycleView):

    def on_selection_applied(self, item, index, is_selected, prev_selected):
        print('on_selection_applied', item, index, is_selected, prev_selected)
        if is_selected:
            item.show_buttons()
        else:
            item.hide_buttons()

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./screens/screen_friends.kv')
