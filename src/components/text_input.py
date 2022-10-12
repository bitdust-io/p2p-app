from kivy.clock import Clock
from kivy.properties import ColorProperty, NumericProperty, StringProperty  # @UnresolvedImport
from kivy.uix.textinput import TextInput

from kivymd.theming import ThemableBehavior
from kivymd.uix.textfield import MDTextFieldRect, MDTextField
from kivymd.uix.label import MDIcon

from lib import system

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

def on_text_input_focus(instance, value):
    if not system.is_android():
        return
    update_main_app_wrapper()
    Clock.schedule_once(update_main_app_wrapper, 0.01)
    Clock.schedule_once(update_main_app_wrapper, 0.02)
    Clock.schedule_once(update_main_app_wrapper, 0.04)
    Clock.schedule_once(update_main_app_wrapper, 0.08)
    Clock.schedule_once(update_main_app_wrapper, 0.16)
    Clock.schedule_once(update_main_app_wrapper, 0.32)
    Clock.schedule_once(update_main_app_wrapper, 0.64)
    Clock.schedule_once(update_main_app_wrapper, 1.28)
    Clock.schedule_once(update_main_app_wrapper, 2.56)


def update_main_app_wrapper(*a):
    from components import screen
    change = system.get_android_keyboard_height()
    if change < 0:
        change = 0
    screen.my_app().wrapper.padding = [0, 0, 0, change, ]
    if _Debug:
        print('text_input.on_text_input_focus', change, screen.main_window().size, screen.my_app().wrapper.size)

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
        on_text_input_focus(instance, value)

#------------------------------------------------------------------------------

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
            print('DynamicHeightTextInput.on_focus', instance, value)
        on_text_input_focus(instance, value)

#------------------------------------------------------------------------------

class CustomTextField(MDTextField):

    def on_focus(self, instance, value):
        if _Debug:
            print('CustomTextField.on_focus', instance, value)
        r = super().on_focus(instance, value)
        on_text_input_focus(instance, value)
        return r



class CustomTextFieldRound(ThemableBehavior, TextInput):
    icon_left = StringProperty()
    icon_left_color = ColorProperty((0, 0, 0, 1))
    icon_right = StringProperty()
    icon_right_color = ColorProperty((0, 0, 0, 1))
    line_color = ColorProperty(None)
    normal_color = ColorProperty(None)
    color_active = ColorProperty(None)
    _color_active = ColorProperty(None)
    _icon_left_color_copy = ColorProperty(None)
    _icon_right_color_copy = ColorProperty(None)

    def __init__(self, **kwargs):
        self._lbl_icon_left = MDIcon(theme_text_color="Custom")
        self._lbl_icon_right = MDIcon(theme_text_color="Custom")
        super().__init__(**kwargs)
        self.cursor_color = self.theme_cls.primary_color
        self.icon_left_color = self.theme_cls.text_color
        self.icon_right_color = self.theme_cls.text_color
        if not self.normal_color:
            self.normal_color = self.theme_cls.primary_light
        if not self.line_color:
            self.line_color = self.theme_cls.primary_dark
        if not self.color_active:
            self._color_active = (0.5, 0.5, 0.5, 0.5)

    def on_focus(self, instance, value):
        if value:
            self.icon_left_color = self.theme_cls.primary_color
            self.icon_right_color = self.theme_cls.primary_color
        else:
            self.icon_left_color = (
                self._icon_left_color_copy or self.theme_cls.text_color
            )
            self.icon_right_color = (
                self._icon_right_color_copy or self.theme_cls.text_color
            )

    def on_icon_left(self, instance, value):
        self._lbl_icon_left.icon = value

    def on_icon_left_color(self, instance, value):
        self._lbl_icon_left.text_color = value
        if (
            not self._icon_left_color_copy
            and value != self.theme_cls.text_color
            and value != self.theme_cls.primary_color
        ):
            self._icon_left_color_copy = value

    def on_icon_right(self, instance, value):
        self._lbl_icon_right.icon = value

    def on_icon_right_color(self, instance, value):
        self._lbl_icon_right.text_color = value
        if (
            not self._icon_right_color_copy
            and value != self.theme_cls.text_color
            and value != self.theme_cls.primary_color
        ):
            self._icon_right_color_copy = value

    def on_color_active(self, instance, value):
        if value != [0, 0, 0, 0.5]:
            self._color_active = value
            self._color_active[-1] = 0.5
        else:
            self._color_active = value

#------------------------------------------------------------------------------

class RoundedTextInput(CustomTextFieldRound):

    def on_focus(self, instance, value):
        if _Debug:
            print('RoundedTextInput.on_focus', instance, value)
        on_text_input_focus(instance, value)

#------------------------------------------------------------------------------

class MultiLineTextInput(MDTextFieldRect):

    extra_padding = NumericProperty('0dp')

    def on_focus(self, instance, value):
        if _Debug:
            print('MultiLineTextInput.on_focus', instance, value)
        on_text_input_focus(instance, value)
