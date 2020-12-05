from kivy.metrics import dp
from kivy.properties import StringProperty, NumericProperty  # @UnresolvedImport
from kivymd.uix.label import MDLabel

#------------------------------------------------------------------------------

class CustomIcon(MDLabel):
    icon = StringProperty("ab-testing")


class BaseLabel(MDLabel):
    pass


class MarkupLabel(BaseLabel):
    pass


class NormalLabel(MarkupLabel):
    pass


class HFlexMarkupLabel(MarkupLabel):
    label_height = NumericProperty('32dp')


class VFlexMarkupLabel(MarkupLabel):
    label_width = NumericProperty('100dp')

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./components/labels.kv')
