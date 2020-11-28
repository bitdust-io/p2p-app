from kivy.properties import StringProperty  # @UnresolvedImport
from kivy.uix.button import Button
from kivymd.uix.button import BaseRectangularButton, BaseFlatButton, BasePressedButton, MDFlatButton, MDRaisedButton, MDFillRoundFlatIconButton, MDFillRoundFlatButton

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


class TransparentButton(BaseRectangularButtonAligned, BaseFlatButton, BasePressedButton):

    increment_width = 0


class RoundedGreenIconButton(RoundedButton):
    pass


#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./components/buttons.kv')
