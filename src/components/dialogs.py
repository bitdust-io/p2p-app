from kivy.metrics import dp, sp
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, NumericProperty  # @UnresolvedImport

from kivymd.uix.button import MDFillRoundFlatButton
from kivymd.uix.dialog import MDDialog

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

class YesNoPopup(GridLayout):
    label = StringProperty()

    def __init__(self,**kwargs):
        self.register_event_type('on_answer')
        super(YesNoPopup, self).__init__(**kwargs)

    def on_answer(self, *args):
        pass


def open_yes_no_dialog(title, text, cb=None):
    content = YesNoPopup(label=text)
    popup = Popup(
        title=title,
        title_align='center',
        content=content,
        size_hint=(None, None),
        size=(dp(480), dp(400)),
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


#------------------------------------------------------------------------------


class InputNumberContent(BoxLayout):
    text_content = StringProperty()
    max_text_length = NumericProperty()


def open_number_input_dialog(title, text, max_text_length=6, button_confirm='Confirm', button_cancel='Cancel', cb=None):
    popup = None
    content = InputNumberContent(
        text_content=text,
        max_text_length=max_text_length,
    )

    def on_confirm(*args, **kwargs):
        inp = content.ids.number_input.text
        if len(inp) == 6:
            popup.dismiss()
            if cb:
                cb(inp)

    def on_cancel(*args, **kwargs):
        popup.dismiss()
        if cb:
            cb(None)

    popup = MDDialog(
        title=title,
        type='custom',
        content_cls=content,
        buttons=[
            MDFillRoundFlatButton(
                font_size=sp(16),
                text=button_confirm,
                on_release=on_confirm,
                text_color=(1,1,1,1),
            ),
            MDFillRoundFlatButton(
                font_size=sp(16),
                text=button_cancel,
                on_release=on_cancel,
                text_color=(1,1,1,1),
            ),
        ],
        size_hint_x=None,
        width=dp(360),
        auto_dismiss=False,
    )
    popup.open()
    return popup

#------------------------------------------------------------------------------

def open_message_dialog(title, text, button_confirm='Confirm', cb=None):

    def on_confirm(*args, **kwargs):
        popup.dismiss()
        if cb:
            cb()

    popup = MDDialog(
        title=title,
        text=text,
        buttons=[
            MDFillRoundFlatButton(
                font_size=sp(16),
                text=button_confirm,
                on_release=on_confirm,
                text_color=(1,1,1,1),
            ),
        ],
        size_hint_x=None,
        width=dp(360),
        auto_dismiss=False,
    )
    popup.open()
    return popup
