from kivy.uix.button import Button

#------------------------------------------------------------------------------

class BasicButton(Button):
    pass


class RoundedButtonInfo(BasicButton):
    pass


class RoundedButton(RoundedButtonInfo):
    pass


class RoundedFlexWidthButton(RoundedButton):
    pass


class RoundedFlexHeightButton(RoundedButton):
    pass


class RoundedFlexButton(RoundedButton):
    pass

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./components/buttons.kv')
