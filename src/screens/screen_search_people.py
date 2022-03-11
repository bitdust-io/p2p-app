from lib import api_client

from components import layouts
from components import screen
from components import labels

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

class SearchPeopleResult(layouts.HorizontalLayout):

    def __init__(self, **kwargs):
        label_text = kwargs.pop('label_text', '')
        super(SearchPeopleResult, self).__init__(**kwargs)
        self.ids.search_result_label.text = label_text

    def on_search_result_add_clicked(self):
        api_client.friend_add(
            global_user_id=self.ids.search_result_label.text,
            cb=self.on_friend_added,
        )

    def on_friend_added(self, resp):
        screen.select_screen('friends_screen')
        screen.main_window().screens_stack.clear()


class NoUsersFound(labels.NormalLabel):
    pass


class SearchPeopleScreen(screen.AppScreen):

    search_started = False

    def init_kwargs(self, **kw):
        self.return_screen_id = kw.pop('return_screen_id', 'friends_screen')
        return kw

    def get_title(self):
        return "search people"

    def get_icon(self):
        return 'account-search'

    def clean_view(self, clear_input_field=False):
        if clear_input_field:
            self.ids.search_input.text = ''
        self.ids.search_results.clear_widgets()

    def start_search(self):
        if self.search_started:
            return
        nickname = self.ids.search_input.text.strip().lower()
        if not nickname:
            return
        self.clean_view()
        self.ids.search_button.disabled = True
        self.search_started = True
        api_client.user_observe(
            nickname=nickname,
            attempts=3,
            cb=self.on_user_observe_result,
        )

    def on_enter(self):
        if self.search_started:
            return
        self.clean_view(clear_input_field=True)
        self.ids.search_button.disabled = False

    def on_search_input_focus_changed(self):
        if _Debug:
            print('SearchPeopleScreen.on_search_input_focus_changed', self.ids.search_input.focus)
        if not self.ids.search_input.focus:
            self.start_search()

    def on_search_button_clicked(self):
        self.start_search()

    def on_user_observe_result(self, resp):
        self.search_started = False
        self.clean_view()
        self.ids.search_button.disabled = False
        if _Debug:
            print('SearchPeopleScreen.on_user_observe_result', resp)
        if not isinstance(resp, dict):
            self.ids.search_results.add_widget(NoUsersFound(
                text=str(resp),
            ))
            return
        result = resp.get('payload', {}).get('response' , {}).get('result', [])
        if not result:
            self.ids.search_results.add_widget(NoUsersFound(
                text='no users found'
            ))
            return
        for r in result:
            self.ids.search_results.add_widget(SearchPeopleResult(
                label_text=str(r['global_id']),
            ))
