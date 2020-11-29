from kivymd.uix.label import MDLabel, MDIcon

#------------------------------------------------------------------------------

class CustomIcon(MDIcon):
    pass


class NormalLabel(MDLabel):
    pass

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./components/labels.kv')
