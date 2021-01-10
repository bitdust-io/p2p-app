from kivy.properties import BooleanProperty, ObjectProperty  # @UnresolvedImport
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.stacklayout import StackLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout

#------------------------------------------------------------------------------

class SelectableRecycleBoxLayout(RecycleBoxLayout, LayoutSelectionBehavior, FocusBehavior):

    touch_deselect_last = BooleanProperty(True)


class BaseSelectableRecord(RecycleDataViewBehavior):

    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        return super(BaseSelectableRecord, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        if super(BaseSelectableRecord, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        prev_selected = self.selected
        if is_selected:
            rv.selected_item = self
        else:
            rv.selected_item = None
        self.selected = is_selected
        rv.on_selection_applied(self, index, is_selected, prev_selected)
        return index


class SelectableStackRecord(BaseSelectableRecord, StackLayout):
    pass


class SelectableHorizontalRecord(BaseSelectableRecord, BoxLayout):
    pass


class SelectableRecycleView(RecycleView):

    selected_item = ObjectProperty(None, allownone=True)

    def clear_selection(self):
        if self.selected_item:
            self.selected_item.selected = False
            self.selected_item = None

    def on_selection_applied(self, item, index, is_selected, prev_selected):
        pass

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./components/list_view.kv')
