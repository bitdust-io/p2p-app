from kivy.properties import StringProperty  # @UnresolvedImport
from kivymd.uix.button import (
    BaseRectangularButton,
    BaseFlatButton,
    BasePressedButton,
    BaseRoundButton,
    MDRaisedButton,
    MDFillRoundFlatButton,
)

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


class BaseRectangularButtonAligned(BaseRectangularButton):

    text_halign = StringProperty('center')


class BaseRoundButtonCustom(BaseRoundButton):
    pass


class IconButton(BaseRoundButtonCustom, BaseFlatButton, BasePressedButton):
    icon = StringProperty("circle")


class TransparentButton(BaseRectangularButtonAligned, BaseFlatButton, BasePressedButton):

    increment_width = 0


class RoundedGreenIconButton(RoundedButton):
    pass


#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./components/buttons.kv')
