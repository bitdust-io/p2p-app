from kivy.uix.textinput import TextInput
from kivy.properties import NumericProperty  # @UnresolvedImport
# from kivy.input.providers.mouse import MouseMotionEvent

from kivymd.uix.textfield import MDTextFieldRect, MDTextFieldRound, MDTextField
from kivymd.theming import ThemableBehavior

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

class SingleLineTextInput(ThemableBehavior, TextInput):

    extra_padding = NumericProperty('0dp')

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
            return super().insert_text(substring, from_undo=from_undo)

    def on_touch_down(self, touch):
        # if not isinstance(touch, MouseMotionEvent):
        #     return False
        if _Debug:
            print('SingleLineTextInput.on_touch_down', touch)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        # if not isinstance(touch, MouseMotionEvent):
        #     return False
        if _Debug:
            print('SingleLineTextInput.on_touch_up', touch)
        return super().on_touch_up(touch)

    def on_touch_move(self, touch):
        # if not isinstance(touch, MouseMotionEvent):
        #     return False
        if _Debug:
            print('SingleLineTextInput.on_touch_move', touch)
        return super().on_touch_move(touch)

    def on_focus(self, instance, value):
        if _Debug:
            print('SingleLineTextInput.on_focus', instance, value)


class DynamicHeightTextInput(ThemableBehavior, TextInput):

    extra_padding = NumericProperty('0dp')

    def insert_text(self, substring, from_undo=False):
        result = super(DynamicHeightTextInput, self).insert_text(substring=substring, from_undo=from_undo)
        self.refresh_height()
        return result

    def do_backspace(self, from_undo=False, mode='bkspc'):
        result = super(DynamicHeightTextInput, self).do_backspace(from_undo=from_undo, mode=mode)
        self.refresh_height()
        return result

    def refresh_height(self):
        old_height = self.height
        self.height = self.line_height * min(self.max_lines, int(len(self.text.split('\n')))) + self.padding[1] + self.padding[3] + self.extra_padding
        if self.height != old_height:
            if _Debug:
                print('DynamicHeightTextInput.refresh_height updated  %d->%d   line_height=%d  padding=%r' % (
                    old_height, self.height, self.line_height, self.padding, ))

    def on_touch_down(self, touch):
        # if not isinstance(touch, MouseMotionEvent):
        #     return False
        if _Debug:
            print('DynamicHeightTextInput.on_touch_down', touch)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        # if not isinstance(touch, MouseMotionEvent):
        #     return False
        if _Debug:
            print('DynamicHeightTextInput.on_touch_up', touch)
        return super().on_touch_up(touch)

    def on_touch_move(self, touch):
        # if not isinstance(touch, MouseMotionEvent):
        #     return False
        if _Debug:
            print('DynamicHeightTextInput.on_touch_move', touch)
        return super().on_touch_move(touch)

    def on_focus(self, instance, value):
        if _Debug:
            print('SingleLineTextInput.on_focus', instance, value)


class CustomTextField(MDTextField):
    pass

#     def on_focus(self, instance, value):
#         if _Debug:
#             print('CustomTextField.on_focus', instance, value)
#         update_app_screen_soft_keyboard_area(value)


class RoundedTextInput(MDTextFieldRound):
    pass

#     def on_focus(self, instance, value):
#         if _Debug:
#             print('RoundedTextInput.on_focus', instance, value)
#         update_app_screen_soft_keyboard_area(value)


class MultiLineTextInput(MDTextFieldRect):

    extra_padding = NumericProperty('0dp')

#     def on_focus(self, instance, value):
#         if _Debug:
#             print('MultiLineTextInput.on_focus', instance, value)
#         update_app_screen_soft_keyboard_area(value)


#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./components/text_input.kv')
