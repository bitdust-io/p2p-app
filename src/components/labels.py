import time

from kivy.properties import StringProperty, NumericProperty  # @UnresolvedImport
from kivy.uix.label import Label

from kivymd.uix.label import MDLabel
from kivymd.theming import ThemableBehavior

#------------------------------------------------------------------------------

from lib import api_client

from fonts import all_fonts

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

class CustomIcon(MDLabel):

    icon = StringProperty("ab-testing")
    icon_pack = StringProperty("IconMD")
    icon_width = NumericProperty("32dp")
    icon_height = NumericProperty("32dp")


class BaseLabel(MDLabel):
    pass


class MarkupLabel(BaseLabel):
    pass


class NormalLabel(MarkupLabel):
    pass


class SingleLineLabel(NormalLabel):
    pass


class HFlexMarkupLabel(ThemableBehavior, Label):
    label_height = NumericProperty('32dp')


class VFlexMarkupLabel(ThemableBehavior, Label):
    label_width = NumericProperty('100dp')


def format_chat_message(sender_name, sender_color, json_payload, message_id):
    return '[i][size=12sp][color={}]{}[/color]  [color=bbbf]{} #{}[/color][/size][/i]\n[font={}][size=14sp]{}[/size][/font]'.format(
        sender_color,
        sender_name,
        time.strftime('%d %B at %H:%M:%S', time.localtime(json_payload['time'])),
        message_id,
        all_fonts.font_path('JetBrainsMono-Medium.ttf'),
        json_payload['data']['message'].strip(),
    )


class ChatMessageLabel(NormalLabel):

    def __init__(self, **kwargs):
        self.conversation_id = kwargs.pop('conversation_id', None)
        self.message_id = kwargs.pop('message_id', None)
        self.message_time = kwargs.pop('message_time', None)
        super().__init__(**kwargs)


class StatusLabel(NormalLabel):

    def from_api_response(self, response):
        if api_client.is_ok(response):
            self.text = ''
            return
        errors = api_client.response_errors(response)
        if not isinstance(errors, list):
            errors = [errors, ]
        txt = ', '.join(errors)
        self.text = '[color=#f00]%s[/color]' % txt
