from kivy.metrics import dp
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.properties import StringProperty  # @UnresolvedImport

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

class YesNoPopup(GridLayout):
    text = StringProperty()

    def __init__(self,**kwargs):
        self.register_event_type('on_answer')
        super(YesNoPopup,self).__init__(**kwargs)

    def on_answer(self, *args):
        pass


def open_yes_no_dialog(title, text, cb=None):
    content = YesNoPopup(text=text)
    popup = Popup(
        title=title,
        title_align='center',
        content=content,
        size_hint=(None, None),
        size=(dp(480),dp(400)),
        auto_dismiss=False,
    )

    def on_answer(instance, answer):
        if _Debug:
            print("dialogs.open_yes_no_dialog.on_answer:" , repr(answer))
        popup.dismiss()
        if cb:
            cb(answer)

    content.bind(on_answer=on_answer)
    popup.open()
    if _Debug:
        print('dialogs.open_yes_no_dialog', popup)
    return popup
