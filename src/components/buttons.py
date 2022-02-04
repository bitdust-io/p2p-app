from kivy.metrics import dp
from kivy.clock import Clock
from kivy.properties import (
    BooleanProperty,  # @UnresolvedImport
    StringProperty,  # @UnresolvedImport
    NumericProperty,  # @UnresolvedImport
    BoundedNumericProperty,  # @UnresolvedImport
    ColorProperty,  # @UnresolvedImport
    ListProperty,  # @UnresolvedImport
    DictProperty,  # @UnresolvedImport
    ObjectProperty,  # @UnresolvedImport
)
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.switch import Switch
from kivy.animation import Animation

from kivymd.theming import ThemableBehavior
from kivymd.uix.button import (
    BaseButton,
    BaseElevationButton,
    BasePressedButton,
    MDFloatingActionButton,
    MDFlatButton,
    MDFloatingActionButtonSpeedDial,
    MDFloatingLabel,
    MDFloatingBottomButton,
    MDFloatingRootButton,
    MDFillRoundFlatButton,
)
from kivymd.uix.behaviors import CircularRippleBehavior, RectangularRippleBehavior
from kivymd.uix.behaviors.elevation import RectangularElevationBehavior
from kivymd.uix.behaviors.backgroundcolor_behavior import SpecificBackgroundColorBehavior

#------------------------------------------------------------------------------

from components import styles
from components import layouts
from components import labels

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

class CustomRectangularButton(RectangularRippleBehavior, BaseButton):

    width = BoundedNumericProperty(
        10, min=10, max=None, errorhandler=lambda x: 10
    )
    text = StringProperty("")
    increment_width = NumericProperty("0dp")
    button_label = BooleanProperty(True)
    can_capitalize = BooleanProperty(True)
    _radius = NumericProperty("2dp")
    _height = NumericProperty(36)
    text_halign = StringProperty('center')


class CustomRectangularFlexButton(RectangularRippleBehavior, BaseButton):

    width = BoundedNumericProperty(
        10, min=10, max=None, errorhandler=lambda x: 10
    )
    text = StringProperty("")
    increment_width = NumericProperty("0dp")
    increment_height = NumericProperty("0dp")
    button_label = BooleanProperty(True)
    can_capitalize = BooleanProperty(True)
    _radius = NumericProperty("2dp")
    text_halign = StringProperty('center')


class CustomRoundButton(CircularRippleBehavior, BaseButton):

    increment_diameter = NumericProperty(12)
    ripple_scale = 10
    _radius = 0
    fixed_width = NumericProperty(None, allownone=True)
    fixed_height = NumericProperty(None, allownone=True)
    icon_padding = NumericProperty("12dp")


class CustomRectangularIconButton(RectangularRippleBehavior, BaseButton):

    increment_width = NumericProperty("0dp")
    _radius = NumericProperty("2dp")


class CustomFlatButton(MDFlatButton):

    fixed_height = NumericProperty(None, allownone=True)

    def __init__(self, **kwargs):
        self.fixed_height = kwargs.pop('fixed_height', None)
        super().__init__(**kwargs)
        self.property('width').set_min(self, None)


class CustomRaisedButton(CustomRectangularButton, RectangularElevationBehavior, SpecificBackgroundColorBehavior, BaseElevationButton, BasePressedButton):
    pass


class CustomRaisedFlexButton(CustomRectangularFlexButton, RectangularElevationBehavior, SpecificBackgroundColorBehavior, BaseElevationButton, BasePressedButton):
    pass


class CustomFloatingActionButton(MDFloatingActionButton):

    button_size = NumericProperty(styles.app.btn_icon_normal_width)
    icon_pack = StringProperty('IconMD')

    def set_size(self, interval):
        self.width = self.button_size
        self.height = self.button_size


class FillRoundFlatButton(MDFillRoundFlatButton):
    pass


class CustomSwitch(Switch):
    pass


class RoundedButton(CustomRaisedButton):
    pass


class RoundedFlexWidthButton(RoundedButton):
    pass


class RoundedFlexHeightButton(RoundedButton):
    pass


class RoundedFlexButton(RoundedButton):
    pass


class CustomIconButton(ButtonBehavior, labels.MarkupLabel):

    icon = StringProperty("circle")
    icon_pack = StringProperty("IconMD")
    icon_size = StringProperty("12sp")
    button_width = NumericProperty("32dp")
    button_height = NumericProperty("32dp")
    background_color = ColorProperty([1, 1, 1, 1])
    background_normal = StringProperty('')
    background_down = StringProperty('')
    background_disabled_normal = StringProperty('')
    background_disabled_down = StringProperty('')
    border = ListProperty([0, 0, 0, 0])
    selected = BooleanProperty(False)


class TransparentIconButton(CustomIconButton):
    pass


class CloseIconButton(TransparentIconButton):
    pass


class LabeledIconButton(ButtonBehavior, layouts.VerticalLayout, ThemableBehavior):

    label_text = StringProperty("")
    label_font_size = NumericProperty("14sp")
    label_height = NumericProperty("20dp")
    label_color = ColorProperty(None, allownone=True)
    icon = StringProperty("circle")
    icon_pack = StringProperty("IconMD")
    icon_size = NumericProperty("20sp")
    icon_color = ColorProperty(None, allownone=True)
    button_width = NumericProperty("32dp")
    button_height = NumericProperty("32dp")
    background_color = ColorProperty([1, 1, 1, 1])
    background_normal = StringProperty('')
    background_down = StringProperty('')
    background_disabled_normal = StringProperty('')
    background_disabled_down = StringProperty('')
    border = ListProperty([0, 0, 0, 0])
    selected = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.icon_color is None:
            self.icon_color = self.theme_cls.primary_color
        if self.label_color is None:
            self.label_color = self.theme_cls.secondary_text_color


class RaisedIconButton(RectangularRippleBehavior, RectangularElevationBehavior, SpecificBackgroundColorBehavior, BaseElevationButton, BasePressedButton):

    icon = StringProperty("circle")
    icon_pack = StringProperty("Icon")
    selected = BooleanProperty(False)
    button_width = NumericProperty(styles.app.btn_icon_normal_width)
    button_height = NumericProperty(styles.app.btn_icon_normal_height)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.set_size)

    def set_size(self, interval):
        self.width = self.button_width
        self.height = self.button_height


def RootActionButton_set_size(self, interval):
    self.width = "24dp"
    self.height = "24dp"


def RootActionButton_on_touch_up(self, touch):
    super(MDFloatingRootButton, self).on_touch_up(touch)
    if self.collide_point(touch.x, touch.y):
        return True
    self.parent.close_stack()


class RootActionButton(MDFloatingActionButtonSpeedDial):

    top_offset = dp(80)
    buttons_colors = DictProperty()
    logo = BooleanProperty(False)
    root_button_rotate_angle = NumericProperty(360)
    do_update_event = ObjectProperty(None, allownone=True)
    update_delay_s = NumericProperty(0.1)
    initialized = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if _Debug:
            print('RootActionButton.__init__', self, kwargs)

    def on_data(self, instance, value):
        if _Debug:
            print('RootActionButton.on_data', instance, value)
        ret = super().on_data(instance, value)
        self.config_style()
        self._update_pos_buttons(instance, 0, 0)
        return ret

    def on_buttons_colors(self, instance, value):
        if _Debug:
            print('RootActionButton.on_buttons_colors', self, instance, value)
        for widget in self.children:
            if isinstance(widget, MDFloatingBottomButton):
                if widget.icon in value:
                    widget.md_bg_color = value[widget.icon]
                    widget._bg_color = value[widget.icon][0:3] + [.6]
            if isinstance(widget, MDFloatingLabel):
                label_icon = None
                for icn, txt in self.data.items():
                    if widget.text == txt:
                        label_icon = icn
                        break
                if label_icon and label_icon in value:
                    widget.bg_color = value[label_icon]

    def config_style(self):
        self.opening_time = 0.2
        self.hint_animation = False
        self.rotation_root_button = True
        self.root_button_anim = True
        self.label_text_color = styles.app.color_white99
        self.color_icon_stack_button = styles.app.color_white99
        self.color_icon_root_button = styles.app.color_white99
        self.bg_color_root_button = self.theme_cls.primary_dark
        self.bg_color_stack_button = self.theme_cls.primary_color
        self.bg_hint_color = self.theme_cls.primary_light
        if _Debug:
            print('RootActionButton.config_style', self.children)
        for widget in self.children:
            if isinstance(widget, MDFloatingBottomButton):
                widget.user_font_size = '17sp'
                widget.padding = '0dp'
            elif isinstance(widget, MDFloatingRootButton):
                widget.on_touch_up = RootActionButton_on_touch_up.__get__(widget, MDFloatingRootButton)
                widget.set_size = RootActionButton_set_size.__get__(widget, MDFloatingRootButton)
                widget.set_size(0)
                widget.user_font_size = '17sp'
                widget.padding = '0dp'
                if self.logo:
                    widget.icon = ''
                    widget.ids.lbl_txt.source = './bitdust.png'
            elif isinstance(widget, MDFloatingLabel):
                widget.elevation = 0

    def _update_pos_buttons(self, instance, width, height):
        if not self.initialized:
            self.initialized = True
            super()._update_pos_buttons(instance, width, height)
            return
        if _Debug:
            print('RootActionButton._update_pos_buttons', width, height)
        self.drop_stack()
        if self.do_update_event is not None:
            self.do_update_event.cancel()
        real_do_update = super()._update_pos_buttons
        self.do_update_event = Clock.schedule_once(lambda dt: real_do_update(instance, width, height), self.update_delay_s)

    def set_pos_root_button(self, instance):
        if _Debug:
            print('    RootActionButton.set_pos_root_button')
        instance.set_size = RootActionButton_set_size.__get__(instance, MDFloatingRootButton)
        instance.set_size(0)
        instance.user_font_size = '17sp'
        instance.padding = '0dp'
        if self.anchor == "right":
            instance.y = Window.height - self.top_offset
            instance.x = Window.width - (dp(36) + dp(20))
        instance.elevation = 0

    def set_pos_labels(self, widget):
        if _Debug:
            print('    RootActionButton.set_pos_labels')
        if self.anchor == "right":
            widget.x = Window.width - widget.width - dp(86)
        widget.elevation = 0

    def set_pos_bottom_buttons(self, instance):
        if _Debug:
            print('    RootActionButton.set_pos_bottom_buttons')
        instance.set_size = RootActionButton_set_size.__get__(instance, MDFloatingBottomButton)
        instance.set_size(0)
        if self.anchor == "right":
            if self.state != "open":
                instance.y = Window.height - self.top_offset
            instance.x = Window.width - (instance.height + instance.width / 2) - dp(2)
        instance.elevation = 0

    def open_stack(self, instance):
        if _Debug:
            print('RootActionButton.open_stack')
        for widget in self.children:
            if isinstance(widget, MDFloatingLabel):
                Animation.cancel_all(widget)
        if self.state != "open":
            y = Window.height - self.top_offset
            label_position = Window.height - self.top_offset + dp(2)
            anim_buttons_data = {}
            anim_labels_data = {}
            for widget in self.children:
                if isinstance(widget, MDFloatingBottomButton):
                    y -= dp(40)
                    widget.y = y
                    if not self._anim_buttons_data:
                        anim_buttons_data[widget] = Animation(
                            opacity=1,
                            d=self.opening_time,
                            t=self.opening_transition,
                        )
                elif isinstance(widget, MDFloatingLabel):
                    label_position -= dp(40)
                    if not self._label_pos_y_set:
                        widget.y = label_position + dp(3)
                        widget.x = Window.width - widget.width - dp(58)
                    if not self._anim_labels_data:
                        anim_labels_data[widget] = Animation(
                            opacity=1, d=self.opening_time
                        )
                elif (
                    isinstance(widget, MDFloatingRootButton)
                    and self.root_button_anim
                ):
                    Animation(
                        _angle=-self.root_button_rotate_angle,
                        d=self.opening_time_button_rotation,
                        t=self.opening_transition_button_rotation,
                    ).start(widget)

            if anim_buttons_data:
                self._anim_buttons_data = anim_buttons_data
            if anim_labels_data and not self.hint_animation:
                self._anim_labels_data = anim_labels_data
            self.state = "open"
            self.dispatch("on_open")
            self.do_animation_open_stack(self._anim_buttons_data)
            self.do_animation_open_stack(self._anim_labels_data)
            if not self._label_pos_y_set:
                self._label_pos_y_set = True
        else:
            self.close_stack()

    def close_stack(self):
        if _Debug:
            print('RootActionButton.close_stack')
        for widget in self.children:
            if isinstance(widget, MDFloatingBottomButton):
                Animation(
                    y=Window.height - self.top_offset,
                    d=self.closing_time,
                    t=self.closing_transition,
                    opacity=0,
                ).start(widget)
                widget._canvas_width = 0
                widget._padding_right = 0
            elif isinstance(widget, MDFloatingLabel):
                Animation(opacity=0, d=0.1).start(widget)
            elif (
                isinstance(widget, MDFloatingRootButton)
                and self.root_button_anim
            ):
                Animation(
                    _angle=0,
                    d=self.closing_time_button_rotation,
                    t=self.closing_transition_button_rotation,
                ).start(widget)
        self.state = "close"
        self.dispatch("on_close")

    def drop_stack(self):
        if _Debug:
            print('RootActionButton.drop_stack')
        self._label_pos_y_set = False
        for widget in self.children:
            if isinstance(widget, MDFloatingBottomButton):
                widget.opacity = 0
                widget.y = Window.height - self.top_offset
                widget._canvas_width = 0
                widget._padding_right = 0
            elif isinstance(widget, MDFloatingLabel):
                widget.opacity = 0
            elif (
                isinstance(widget, MDFloatingRootButton)
                and self.root_button_anim
            ):
                widget._angle = 0
        self.state = "close"
        self.dispatch("on_close")
