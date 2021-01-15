from kivy.properties import StringProperty, NumericProperty  # @UnresolvedImport
from kivy.uix.label import Label
from kivymd.uix.label import MDLabel
from kivymd.theming import ThemableBehavior

from lib import websock
from components.webfont import md_icon, fa_icon, is_md_icon, is_fa_icon

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

class CustomIcon(ThemableBehavior, Label):

    icon = StringProperty("ab-testing")
    icon_width = NumericProperty("32dp")
    icon_height = NumericProperty("32dp")


class BaseLabel(MDLabel):
    pass


class MarkupLabel(BaseLabel):
    pass


class NormalLabel(MarkupLabel):
    pass


class HFlexMarkupLabel(ThemableBehavior, Label):
    label_height = NumericProperty('32dp')


class VFlexMarkupLabel(ThemableBehavior, Label):
    label_width = NumericProperty('100dp')


class ChatMessageLabel(NormalLabel):
    pass


class StatusLabel(NormalLabel):

    def from_api_response(self, response):
        if websock.is_ok(response):
            self.text = ''
            return
        errors = websock.response_errors(response)
        if not isinstance(errors, list):
            errors = [errors, ]
        txt = ', '.join(errors)
        self.text = '[color=#f00]%s[/color]' % txt

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./components/labels.kv')
