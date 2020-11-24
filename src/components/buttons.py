from kivy.uix.button import Button
from kivymd.uix.button import MDFlatButton, MDRaisedButton, MDFillRoundFlatIconButton, MDFillRoundFlatButton

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


class TransparentButton(MDFlatButton):
    pass


class RoundedGreenIconButton(RoundedButton):
    pass


#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./components/buttons.kv')
