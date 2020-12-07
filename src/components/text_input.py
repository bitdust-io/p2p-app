from kivymd.uix.textfield import MDTextField, MDTextFieldRect, MDTextFieldRound

#------------------------------------------------------------------------------

class BasicTextInput(MDTextField):
    pass


class SingleLineTextInput(BasicTextInput):
    pass


class RoundedTextInput(MDTextFieldRound):
    pass


class MultiLineTextInput(MDTextFieldRect):
    pass

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./components/text_input.kv')
