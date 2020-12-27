from components.screen import AppScreen
from components.list_view import SelectableRecycleView, SelectableHorizontalRecord

from lib import api_client
from lib import websock

#------------------------------------------------------------------------------

class SelectFriendRecord(SelectableHorizontalRecord):

    def __init__(self, **kwargs):
        super(SelectFriendRecord, self).__init__(**kwargs)
        self.visible_buttons = []


class SelectFriendListView(SelectableRecycleView):

    def on_selection_applied(self, item, index, is_selected, prev_selected):
        print('on_selection_applied', item.global_id)


class SelectFriendScreen(AppScreen):

    def init_kwargs(self, **kw):
        self.return_screen_id = kw.pop('return_screen_id', '')
        return kw

    def get_title(self):
        return 'contacts'

    def get_icon(self):
        return 'target-account'

    def populate(self, *args, **kwargs):
        api_client.friends_list(cb=self.on_friends_list_result)

    def on_pre_enter(self, *args):
        self.populate()

    def on_friends_list_result(self, resp):
        if not isinstance(resp, dict):
            self.ids.friends_list_view.data = []
            return
        result = websock.response_result(resp)
        if not result:
            self.ids.friends_list_view.data = []
            return
        self.ids.friends_list_view.data = []
        for one_friend in result:
            self.ids.friends_list_view.data.append(one_friend)

    def on_search_people_button_clicked(self, *args):
        self.main_win().select_screen(
            screen_id='search_people_screen',
            return_screen_id='select_friend_screen',
        )

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./screens/screen_select_friend.kv')
