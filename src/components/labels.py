from kivy.properties import StringProperty, NumericProperty  # @UnresolvedImport
from kivy.uix.label import Label
from kivymd.uix.label import MDLabel
from kivymd.theming import ThemableBehavior

#------------------------------------------------------------------------------

class CustomIcon(MDLabel):
    icon = StringProperty("ab-testing")


class BaseLabel(MDLabel):
    pass


class MarkupLabel(BaseLabel):
    pass


class NormalLabel(MarkupLabel):
    pass


class HFlexMarkupLabel(ThemableBehavior, Label):
    label_height = NumericProperty('32dp')


class VFlexMarkupLabel(ThemableBehavior, Label):
    label_width = NumericProperty('100dp')

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./components/labels.kv')
