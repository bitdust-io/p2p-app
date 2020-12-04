from kivy.properties import StringProperty  # @UnresolvedImport
from kivymd.uix.label import MDLabel

#------------------------------------------------------------------------------

class CustomIcon(MDLabel):
    icon = StringProperty("ab-testing")


class BaseLabel(MDLabel):
    pass


class MarkupLabel(BaseLabel):
    pass


class FlexMarkupLabel(MarkupLabel):
    pass


class HFlexMarkupLabel(MarkupLabel):
    pass


class NormalLabel(MarkupLabel):
    pass

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./components/labels.kv')
