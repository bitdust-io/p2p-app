from kivy.uix.label import Label

#------------------------------------------------------------------------------

from components.layouts import HorizontalLayout
from components.screen import AppScreen
from components.webfont import fa_icon

from lib import api_client

#------------------------------------------------------------------------------

class SearchResult(HorizontalLayout):

    def __init__(self, **kwargs):
        label_text = kwargs.pop('label_text', '')
        super(SearchResult, self).__init__(**kwargs)
        self.ids.search_result_label.text = label_text

    def on_search_result_add_clicked(self):
        api_client.friend_add(
            global_user_id=self.ids.search_result_label.text,
            cb=self.on_friend_added,
        )

    def on_friend_added(self, resp):
        self.parent.parent.parent.parent.main_win().select_screen('friends_screen')


class NoUsersFound(Label):
    pass


class SearchPeopleScreen(AppScreen):

    search_started = False

    def get_icon(self):
        return 'account-search'

    def get_title(self):
        return "search people"

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
            cb=self.on_user_observe_results,
        )

    def on_enter(self):
        if self.search_started:
            return
        self.clean_view(clear_input_field=True)
        self.ids.search_button.disabled = False

    def on_search_input_focus_changed(self):
        if not self.ids.search_input.focus:
            self.start_search()

    def on_search_button_clicked(self):
        self.start_search()

    def on_user_observe_results(self, resp):
        self.search_started = False
        self.clean_view()
        self.ids.search_button.disabled = False
        if not isinstance(resp, dict):
            self.ids.search_results.add_widget(NoUsersFound(
                text=str(resp),
            ))
            return
        result = resp.get('payload', {}).get('response' , {}).get('result', [])
        if not result:
            self.ids.search_results.add_widget(NoUsersFound())
            return
        for r in result:
            self.ids.search_results.add_widget(SearchResult(
                label_text=str(r['global_id']),
            ))

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./screens/screen_search_people.kv')
