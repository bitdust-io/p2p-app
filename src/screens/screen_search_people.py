from lib import api_client
from lib import util

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
        screen.stack_clear()
        screen.stack_append('welcome_screen')


class NoUsersFound(labels.NormalLabel):
    pass


class SearchPeopleScreen(screen.AppScreen):

    def init_kwargs(self, **kw):
        self.return_screen_id = kw.pop('return_screen_id', 'friends_screen')
        return kw

    def get_title(self):
        return "search people"

    def clean_view(self, clear_input_field=False):
        if clear_input_field:
            self.ids.search_input.text = ''
        self.ids.search_results.clear_widgets()

    def start_search(self, randomized=False):
        self.clean_view()
        self.ids.search_button.disabled = True
        self.ids.random_search_button.disabled = True
        if randomized:
            api_client.dht_user_random(
                count=3,
                cb=self.on_user_observe_result,
            )
        else:
            nickname = self.ids.search_input.text.strip().lower()
            if not nickname:
                self.clean_view(clear_input_field=True)
                self.ids.search_button.disabled = False
                self.ids.random_search_button.disabled = False
                return
            api_client.user_observe(
                nickname=nickname,
                attempts=3,
                cb=self.on_user_observe_result,
            )

    def on_enter(self):
        self.clean_view(clear_input_field=True)
        self.ids.search_button.disabled = False
        self.ids.random_search_button.disabled = False

    def on_search_input_key_enter_pressed(self, *args):
        if _Debug:
            print('SearchPeopleScreen.on_search_input_key_enter_pressed')
        self.start_search()

    def on_search_button_clicked(self):
        self.start_search()

    def on_random_button_clicked(self):
        self.start_search(randomized=True)

    def on_user_observe_result(self, resp):
        self.clean_view()
        self.ids.search_button.disabled = False
        self.ids.random_search_button.disabled = False
        if _Debug:
            print('SearchPeopleScreen.on_user_observe_result', resp)
        if not isinstance(resp, dict):
            self.ids.search_results.add_widget(NoUsersFound(text=str(resp)))
            return
        result = resp.get('payload', {}).get('response' , {}).get('result', [])
        if not result:
            self.ids.search_results.add_widget(NoUsersFound(text='no users found'))
            return
        for r in result:
            if isinstance(r, str):
                user_id = util.IDUrlToGlobalID(r)
            else:
                user_id = str(r['global_id'])
            self.ids.search_results.add_widget(SearchPeopleResult(label_text=user_id))
