from kivy.properties import StringProperty  # @UnresolvedImport

#------------------------------------------------------------------------------

from components import screen
from components import list_view

from lib import api_client
from lib import websock

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

class SelectFriendRecord(list_view.SelectableHorizontalRecord):
    pass


class SelectFriendListView(list_view.SelectableRecycleView):

    def on_selection_applied(self, item, index, is_selected, prev_selected):
        if _Debug:
            print('SelectFriendListView.on_selection_applied', item.global_id, self.selected_item)
        if self.selected_item:
            global_id = self.selected_item.global_id
            if self.parent.parent.parent.parent.parent.result_callback:
                self.parent.parent.parent.parent.parent.result_callback(global_id)
        self.clear_selection()
        self.ids.selectable_layout.clear_selection()

#------------------------------------------------------------------------------

class SelectFriendScreen(screen.AppScreen):

    screen_header = StringProperty('Select user')

    def init_kwargs(self, **kw):
        self.result_callback = kw.pop('result_callback', None)
        self.screen_header = kw.pop('screen_header', 'Select user')
        return kw

    def get_title(self):
        return 'select user'

    def get_icon(self):
        return 'target-account'

    def populate(self, *args, **kwargs):
        api_client.friends_list(cb=self.on_friends_list_result)

    def clear_selected_item(self):
        self.ids.friends_list_view.clear_selection()
        self.ids.friends_list_view.ids.selectable_layout.clear_selection()

    def on_enter(self, *args):
        self.ids.action_button.close_stack()
        self.clear_selected_item()
        self.populate()

    def on_leave(self, *args):
        self.ids.action_button.close_stack()
        self.clear_selected_item()

    def on_friends_list_result(self, resp):
        if not isinstance(resp, dict):
            self.clear_selected_item()
            self.ids.friends_list_view.data = []
            return
        result = websock.response_result(resp)
        if not result:
            self.ids.friends_list_view.data = []
            return
        self.ids.friends_list_view.data = []
        for one_friend in result:
            one_friend['automat_index'] = str(one_friend.pop('index', ''))
            one_friend['automat_id'] = str(one_friend.pop('id', ''))
            self.ids.friends_list_view.data.append(one_friend)

    def on_action_button_clicked(self, btn):
        if _Debug:
            print('SelectFriendScreen.on_action_button_clicked', btn.icon)
        self.ids.action_button.close_stack()
        if btn.icon == 'account-search-outline':
            self.main_win().select_screen(
                screen_id='search_people_screen',
                return_screen_id='select_friend_screen',
            )
