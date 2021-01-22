from kivy.metrics import dp, sp
from kivy.clock import Clock
from kivy.properties import (
    BooleanProperty,  # @UnresolvedImport
    StringProperty,  # @UnresolvedImport
    NumericProperty,  # @UnresolvedImport
    BoundedNumericProperty,  # @UnresolvedImport
    ColorProperty,  # @UnresolvedImport
    ListProperty,  # @UnresolvedImport
)
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivymd.theming import ThemableBehavior
from kivymd.uix.label import MDLabel
from kivymd.uix.button import (
    BaseButton,
    BaseElevationButton,
    BasePressedButton,
    MDFloatingActionButton,
    MDFlatButton,
    MDIconButton,
)
from kivymd.uix.behaviors import CircularRippleBehavior, RectangularRippleBehavior
from kivymd.uix.behaviors.elevation import RectangularElevationBehavior
from kivymd.uix.behaviors.backgroundcolor_behavior import SpecificBackgroundColorBehavior

#------------------------------------------------------------------------------

from components.layouts import VerticalLayout
from components.styles import style

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
    _height = NumericProperty(0)
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
        super().__init__(**kwargs)
        self.property('width').set_min(self, None)


class CustomRaisedButton(CustomRectangularButton, RectangularElevationBehavior, SpecificBackgroundColorBehavior, BaseElevationButton, BasePressedButton):
    pass


class CustomFloatingActionButton(MDFloatingActionButton):

    button_size = NumericProperty(style.btn_icon_normal_width)
    icon_pack = StringProperty('IconMD')

    def set_size(self, interval):
        self.width = self.button_size
        self.height = self.button_size


class RoundedButton(CustomRaisedButton):
    pass


class RoundedFlexWidthButton(RoundedButton):
    pass


class RoundedFlexHeightButton(RoundedButton):
    pass


class RoundedFlexButton(RoundedButton):
    pass


class CustomIconButton(ButtonBehavior, MDLabel):

    icon = StringProperty("circle")
    icon_pack = StringProperty("IconMD")
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


class LabeledIconButton(ButtonBehavior, VerticalLayout, ThemableBehavior):

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
            self.label_color = self.theme_cls.primary_dark


class RaisedIconButton(RectangularRippleBehavior, RectangularElevationBehavior, SpecificBackgroundColorBehavior, BaseElevationButton, BasePressedButton):

    icon = StringProperty("circle")
    icon_pack = StringProperty("IconMD")
    selected = BooleanProperty(False)
    _radius = dp(4)
    button_width = NumericProperty(style.btn_icon_normal_width)
    button_height = NumericProperty(style.btn_icon_normal_height)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.set_size)

    def set_size(self, interval):
        self.width = self.button_width
        self.height = self.button_height

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./components/buttons.kv')
