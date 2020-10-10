from kivy.uix.textinput import TextInput

#------------------------------------------------------------------------------

class BasicTextInput(TextInput):
    pass


class SingleLineTextInput(BasicTextInput):
    pass


class MultiLineTextInput(BasicTextInput):
    pass

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./components/text_input.kv')
