from kivy.properties import (
    BooleanProperty,  # @UnresolvedImport
    StringProperty,  # @UnresolvedImport
    NumericProperty,  # @UnresolvedImport
    BoundedNumericProperty,  # @UnresolvedImport
    ColorProperty,  # @UnresolvedImport
)
from kivy.uix.button import Button
from kivymd.theming import ThemableBehavior
from kivymd.uix.button import (
    BaseButton,
    BaseElevationButton,
    BasePressedButton,
    MDFloatingActionButton,
    MDFlatButton,
)
from kivymd.uix.behaviors import CircularRippleBehavior, RectangularRippleBehavior
from kivymd.uix.behaviors.elevation import RectangularElevationBehavior
from kivymd.uix.behaviors.backgroundcolor_behavior import SpecificBackgroundColorBehavior

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

    button_size = NumericProperty('32dp')
    icon_pack = StringProperty('md')

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


class CustomIconButton(ThemableBehavior, Button):

    icon = StringProperty("circle")
    icon_pack = StringProperty("md")
    button_width = NumericProperty("32dp")
    button_height = NumericProperty("32dp")


class TransparentIconButton(CustomIconButton):
    pass


class RaisedIconButton(CustomRectangularIconButton, RectangularElevationBehavior, SpecificBackgroundColorBehavior, BaseElevationButton, BasePressedButton):

    icon = StringProperty("circle")


class CloseIconButton(TransparentIconButton):
    pass


class CustomRaisedIconButton(RaisedIconButton):
    pass

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./components/buttons.kv')
