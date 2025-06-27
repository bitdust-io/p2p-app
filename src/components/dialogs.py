from kivy.metrics import dp, sp
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, NumericProperty  # @UnresolvedImport

from kivymd.uix.button import MDFillRoundFlatButton, MDFlatButton
from kivymd.uix.dialog import MDDialog

#------------------------------------------------------------------------------

from components import spinner

#------------------------------------------------------------------------------

_Debug = False

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


class InputTextContent(BoxLayout):
    text_content = StringProperty()


class InputTextMultilineContent(BoxLayout):
    text_content = StringProperty()


def open_text_input_dialog(title, text, multiline=False, button_confirm='Confirm', button_cancel='Cancel', cb=None):
    popup = None
    if multiline:
        content = InputTextMultilineContent(text_content=text)
    else:
        content = InputTextContent(text_content=text)

    def on_confirm(*args, **kwargs):
        inp = content.ids.text_input.text
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
        pos_hint={'y': .15},
    )

    def on_open(*args, **kwargs):
        content.ids.text_input.focus = True

    popup.update_width = lambda *args: None
    popup.bind(on_open=on_open)
    popup.open()
    return popup

#------------------------------------------------------------------------------


class InputNumberContent(BoxLayout):
    text_content = StringProperty()
    max_text_length = NumericProperty()


def open_number_input_dialog(title, text, min_text_length=None, max_text_length=None, button_confirm='Confirm', button_cancel='Cancel', cb=None):
    popup = None
    content = InputNumberContent(
        text_content=text,
        max_text_length=max_text_length,
    )

    def on_confirm(*args, **kwargs):
        inp = content.ids.number_input.text
        if _Debug:
            print('dialogs.open_number_input_dialog.on_confirm', args, kwargs, cb, inp)
        if min_text_length is None:
            popup.dismiss()
            if cb:
                cb(inp)
        else:
            if len(inp) == min_text_length:
                popup.dismiss()
                if cb:
                    cb(inp)

    def on_cancel(*args, **kwargs):
        if _Debug:
            print('dialogs.open_number_input_dialog.on_cancel', args, kwargs, cb)
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
        pos_hint={'y': .15},
    )

    def on_open(*args, **kwargs):
        content.ids.number_input.focus = True

    popup.update_width = lambda *args: None
    popup.bind(on_open=on_open)
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
        pos_hint={'y': .15},
    )
    popup.update_width = lambda *args: None
    popup.open()
    return popup

#------------------------------------------------------------------------------

def open_spinner_dialog(title, label='', button_cancel=None, cb_cancel=None):
    popup = None
    spin = spinner.CircularProgressBar(
        size_hint=(None, None),
        size=(dp(125), dp(125)),
        pos_hint={'center_x': .5, 'center_y': .6},
        max=360,
    )
    spin.start(label=label)

    def on_cancel(*args, **kwargs):
        popup.dismiss()
        if cb_cancel:
            cb_cancel()

    def on_dismiss(*args, **kwargs):
        spin.stop()

    popup = MDDialog(
        title=title,
        type='custom',
        content_cls=spin,
        buttons=[
            MDFlatButton(
                font_size=sp(14),
                text=button_cancel,
                on_release=on_cancel,
            ),
        ] if button_cancel else [],
        size_hint_x=None,
        width=dp(170),
        auto_dismiss=False,
        on_dismiss=on_dismiss,
        pos_hint={'y': .15},
    )
    popup.update_width = lambda *args: None
    popup.open()
    return popup
