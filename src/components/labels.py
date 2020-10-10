from kivy.uix.label import Label

#------------------------------------------------------------------------------

class NormalLabel(Label):
    pass

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./components/labels.kv')
