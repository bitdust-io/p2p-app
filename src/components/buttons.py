from kivy.properties import (
    BooleanProperty,  # @UnresolvedImport
    StringProperty,  # @UnresolvedImport
    NumericProperty,  # @UnresolvedImport
    BoundedNumericProperty,  # @UnresolvedImport
)
from kivymd.uix.button import (
    BaseButton,
    BaseFlatButton,
    BaseRaisedButton,
    BasePressedButton,
    BaseRoundButton,
    MDRaisedButton,
    MDFillRoundFlatButton,
)
from kivymd.uix.behaviors import CircularRippleBehavior, RectangularRippleBehavior
from kivymd.uix.behaviors.elevation import CircularElevationBehavior

#------------------------------------------------------------------------------

class NormalButton(MDRaisedButton):
    pass


class BasicButton(MDRaisedButton):
    pass


class RoundedButton(MDFillRoundFlatButton):
    pass


class RoundedFlexWidthButton(RoundedButton):
    pass


class RoundedFlexHeightButton(RoundedButton):
    pass


class RoundedFlexButton(RoundedButton):
    pass


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


class CustomIconButton(RoundedButton):
    icon = StringProperty("circle")


class CustomRoundButton(CircularRippleBehavior, BaseButton):
    pass


class IconButton(CustomRoundButton, BaseFlatButton, BasePressedButton):
    icon = StringProperty("circle")


class CustomFlatButton(CustomRectangularButton, BaseFlatButton, BasePressedButton):
    increment_width = 0


class CustomFloatingActionButton(
    CustomRoundButton, CircularElevationBehavior, BaseRaisedButton
):
    icon = StringProperty("android")
    background_palette = StringProperty("Accent")


#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./components/buttons.kv')
