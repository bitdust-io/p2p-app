from kivy.uix.textinput import TextInput
from kivymd.uix.textfield import MDTextField

#------------------------------------------------------------------------------

class BasicTextInput(MDTextField):
    pass


class SingleLineTextInput(BasicTextInput):
    pass


class MultiLineTextInput(BasicTextInput):
    pass

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./components/text_input.kv')
