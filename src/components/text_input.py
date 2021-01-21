from kivy.uix.textinput import TextInput
from kivymd.uix.textfield import MDTextFieldRect, MDTextFieldRound
from kivymd.theming import ThemableBehavior

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

class BasicTextInput(ThemableBehavior, TextInput):
    pass


class SingleLineTextInput(BasicTextInput):
    pass


class RoundedTextInput(MDTextFieldRound):
    pass


class MultiLineTextInput(MDTextFieldRect):
    pass


class DynamicHeightTextInput(ThemableBehavior, TextInput):

    def insert_text(self, substring, from_undo=False):
        result = super(DynamicHeightTextInput, self).insert_text(substring=substring, from_undo=from_undo)
        self.refresh_height()
        return result

    def do_backspace(self, from_undo=False, mode='bkspc'):
        result = super(DynamicHeightTextInput, self).do_backspace(from_undo=from_undo, mode=mode)
        self.refresh_height()
        return result

    def refresh_height(self):
        self.height = self.line_height * min(self.max_lines, int(len(self.text.split('\n')))) + self.padding[1] + self.padding[3]

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./components/text_input.kv')
