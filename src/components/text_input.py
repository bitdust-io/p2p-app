from kivy.uix.textinput import TextInput

from kivymd.uix.textfield import MDTextFieldRect, MDTextFieldRound, MDTextField
from kivymd.theming import ThemableBehavior

#------------------------------------------------------------------------------

from lib.system import get_android_keyboard_height, is_android
#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

def update_app_screen_soft_keyboard_area(focus_on):
    if not is_android():
        return
    if _Debug:
        print('text_input.update_app_screen_soft_keyboard_area', focus_on, get_android_keyboard_height())

#------------------------------------------------------------------------------

class BasicTextInput(ThemableBehavior, TextInput):
    pass


class SingleLineTextInput(ThemableBehavior, TextInput):

    def insert_text(self, substring, from_undo=False):
        if _Debug:
            print('SingleLineTextInput.insert_text', self.text, substring)
        if self.input_filter != 'int':
            return super(SingleLineTextInput, self).insert_text(substring, from_undo=from_undo)
        min_value = self.parent.parent.option_value_min
        max_value = self.parent.parent.option_value_max
        t = self.text
        c = self.cursor[0]
        if c == len(t):
            new_text = self.text + substring
        else:
            new_text = t[:c] + substring + t[c:]
        if new_text != '':
            try:
                new_value = int(new_text)
            except:
                return
            if min_value is not None and min_value > new_value:
                return
            if max_value is not None and max_value < new_value:
                return
            return super(SingleLineTextInput, self).insert_text(substring, from_undo=from_undo)

    def on_focus(self, instance, value):
        if _Debug:
            print('SingleLineTextInput.on_focus', instance, value)
        update_app_screen_soft_keyboard_area(value)


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

    def on_focus(self, instance, value):
        if _Debug:
            print('DynamicHeightTextInput.on_focus', instance, value)
        update_app_screen_soft_keyboard_area(value)


class CustomTextField(MDTextField):

    def on_focus(self, instance, value):
        if _Debug:
            print('CustomTextField.on_focus', instance, value)
        update_app_screen_soft_keyboard_area(value)


class RoundedTextInput(MDTextFieldRound):

    def on_focus(self, instance, value):
        if _Debug:
            print('RoundedTextInput.on_focus', instance, value)
        update_app_screen_soft_keyboard_area(value)


class MultiLineTextInput(MDTextFieldRect):

    def on_focus(self, instance, value):
        if _Debug:
            print('MultiLineTextInput.on_focus', instance, value)
        update_app_screen_soft_keyboard_area(value)


#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./components/text_input.kv')
