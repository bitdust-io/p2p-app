from kivy.metrics import dp
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty  # @UnresolvedImport

from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
 
#------------------------------------------------------------------------------

from lib import api_client
from lib import websock

from components import labels
from components import layouts

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

class AutomatStatusPanel(MDCard):

    automat_index = None

#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)

#     def build(self):
#         self.label_name = labels.NormalLabel()
#         self.label_state = labels.NormalLabel()
#         self.label_status = labels.NormalLabel()
#         hl = layouts.HorizontalLayout()
#         self.add_widget(hl)
#         self.add_widget(self.label_status)
#         hl.add_widget(self.label_name)
#         hl.add_widget(self.label_state)

    def state_to_label(self):
        return 'something here'

    def init(self, automat_index):
        if _Debug:
            print('AutomatStatusPanel.init', automat_index)
        self.automat_index = automat_index
        if self.automat_index is not None:
            api_client.automat_events_start(index=int(self.automat_index), cb=self.on_automat_events_start_result)

    def shutdown(self):
        if _Debug:
            print('AutomatStatusPanel.shutdown', self.automat_index)
        if self.automat_index is not None:
            api_client.automat_events_stop(index=int(self.automat_index))

    def on_automat_events_start_result(self, resp):
        if _Debug:
            print('AutomatStatusPanel.on_automat_events_start_result', resp)
        if not websock.is_ok(resp):
            self.ids.label_name.text = ''
            self.ids.label_state.text = ''
            self.ids.label_status.text = websock.red_err(resp)
            return
        r = websock.result(resp)
        self.ids.label_name.text = '#{} {} {}'.format(self.automat_index, r['name'], r['id'])
        self.ids.label_state.text = r['state']
        self.ids.label_status.text = self.state_to_label()
