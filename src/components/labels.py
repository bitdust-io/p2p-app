from kivy.properties import StringProperty  # @UnresolvedImport
from kivymd.uix.label import MDLabel

#------------------------------------------------------------------------------

class CustomIcon(MDLabel):
    icon = StringProperty("ab-testing")


class NormalLabel(MDLabel):
    pass

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./components/labels.kv')
