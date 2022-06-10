from kivy.clock import Clock
from kivy.animation import Animation
from kivy.properties import (
    BooleanProperty,  # @UnresolvedImport
    StringProperty,  # @UnresolvedImport
    NumericProperty,  # @UnresolvedImport
    BoundedNumericProperty,  # @UnresolvedImport
    ColorProperty,  # @UnresolvedImport
    ListProperty,  # @UnresolvedImport
)
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.switch import Switch
from kivymd.uix.list import IconLeftWidget, ILeftBodyTouch
from kivymd.theming import ThemableBehavior
from kivymd.uix.button import (
    BaseButton,
    BasePressedButton,
    MDFlatButton,
    MDFillRoundFlatButton,
    MDFloatingActionButton,
)
from kivymd.uix.behaviors import CircularRippleBehavior, RectangularRippleBehavior
from kivymd.uix.behaviors.elevation import RectangularElevationBehavior, CommonElevationBehavior
from kivymd.uix.behaviors.backgroundcolor_behavior import SpecificBackgroundColorBehavior

#------------------------------------------------------------------------------

from components import styles
from components import layouts
from components import labels

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

class BasePressedButton(BaseButton):

    animation_fade_bg = None
    current_md_bg_color = ColorProperty(None)

    def on_touch_down(self, touch):
        if touch.is_mouse_scrolling:
            return False
        elif not self.collide_point(touch.x, touch.y):
            return False
        elif self in touch.ud:
            return False
        elif self.disabled:
            return False
        else:
            if self.md_bg_color == [0.0, 0.0, 0.0, 0.0]:
                self.current_md_bg_color = self.md_bg_color
                self.animation_fade_bg = Animation(
                    duration=0.5, md_bg_color=[0.0, 0.0, 0.0, 0.1]
                )
                self.animation_fade_bg.start(self)
            return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if (
            self.collide_point(touch.x, touch.y)
            and self.animation_fade_bg
            and not self.disabled
        ):
            self.animation_fade_bg.stop_property(self, "md_bg_color")
            Animation(
                duration=0.05, md_bg_color=self.current_md_bg_color
            ).start(self)
        return super().on_touch_up(touch)


class BaseElevationButton(CommonElevationBehavior, BaseButton):

    _elevation_normal = NumericProperty(0)
    _elevation_raised = NumericProperty(0)
    _anim_raised = None

    def on_elevation(self, instance, value):
        self._elevation_normal = self.elevation
        self._elevation_raised = self.elevation
        self._anim_raised = Animation(_elevation=value + 2, d=0.5)
        self._anim_raised.bind(on_progress=self._do_anim_raised)
        self._update_elevation(instance, value)

    def on_disabled(self, instance, value):
        # FIXME: If a button has a default `disabled` parameter of `True`,
        #  the `elevation` value is not cleared.
        if self.disabled:
            self._elevation = 0
            self._update_shadow(instance, 0)
        else:
            self._update_elevation(instance, self._elevation_normal)
        super().on_disabled(instance, value)

    def on_touch_down(self, touch):
        if not self.disabled:
            if touch.is_mouse_scrolling:
                return False
            if not self.collide_point(touch.x, touch.y):
                return False
            if self in touch.ud:
                return False
            if self._anim_raised:
                self._anim_raised.start(self)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if not self.disabled:
            if touch.grab_current is not self:
                if isinstance(self, MDFloatingActionButton):
                    self.stop_elevation_anim()
                return super().on_touch_up(touch)
            self.stop_elevation_anim()
        return super().on_touch_up(touch)

    def stop_elevation_anim(self):
        Animation.cancel_all(self, "_elevation")
        self._elevation = self._elevation_raised
        self._elevation_normal = self._elevation_raised
        self._update_shadow(self, self._elevation)

    def _do_anim_raised(self, animation, instance, value):
        self._elevation += value
        if self._elevation < self._elevation_raised + 2:
            self._update_shadow(instance, self._elevation)


class CustomRectangularButton(RectangularRippleBehavior, BaseButton):

    width = BoundedNumericProperty(
        10, min=10, max=None, errorhandler=lambda x: 10
    )
    text = StringProperty("")
    increment_width = NumericProperty("16dp")
    increment_height = NumericProperty("16dp")
    button_label = BooleanProperty(True)
    can_capitalize = BooleanProperty(True)
    _radius = NumericProperty("8dp")
    _height = NumericProperty("48dp")
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

#------------------------------------------------------------------------------

class CustomIconLeftWidget(IconLeftWidget):

    def set_size(self, interval):
        self.width = '36dp'
        self.height = '36dp'


class CustomIconPackLeftWidget(ILeftBodyTouch, CustomIconButton):
    pass
