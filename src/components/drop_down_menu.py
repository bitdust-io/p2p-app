from kivy.properties import ObjectProperty, OptionProperty, DictProperty  # @UnresolvedImport
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics.vertex_instructions import Line  # @UnresolvedImport

from kivymd.theming import ThemableBehavior
from kivymd.uix.menu import MDDropdownMenu

#------------------------------------------------------------------------------

from components import screen

#------------------------------------------------------------------------------

class CustomDropdownMenu(MDDropdownMenu):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.card.elevation = 0

    def create_menu_items(self):
        super().create_menu_items()
        for w in self.menu.ids.box.children:
            removed = False
            for c in w.canvas.children:
                if isinstance(c, Line):
                    w.canvas.remove(c)
                    removed = True
                    break
            if removed:
                break

#------------------------------------------------------------------------------

class CustomFloatingActionButtonSpeedDial(ThemableBehavior, FloatLayout):
    callback = ObjectProperty(lambda x: None)
    data = DictProperty()
    state = OptionProperty("close", options=("close", "open"))
    menu = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type("on_open")
        self.register_event_type("on_close")

    def on_open(self, *args):
        pass

    def on_close(self, *args):
        pass

    def on_menu_item_clicked(self, menu_inst, item_inst):
        self.close_stack()
        if self.callback:
            self.callback(item_inst)

    def on_data(self, instance, val):
        menu_items = []
        value = dict(val)
        width_mult = value.pop('width_mult', 5)
        for icon_name in value.keys():
            itm = {
                "icon": icon_name,
                "text": value[icon_name],
                "viewclass": "OneLineListItem",
            }
            menu_items.append(itm)
        self.menu = CustomDropdownMenu(
            caller=screen.main_window().ids.dropdown_menu_placeholder,
            width_mult=width_mult,
            items=menu_items,
            opening_time=0,
            ver_growth="down",
            hor_growth="left",
            position="auto",
        )
        self.menu.bind(on_release=self.on_menu_item_clicked)

    def open_stack(self):
        self.menu.open()
        self.state = "open"
        self.dispatch("on_open")

    def close_stack(self):
        self.menu.dismiss()
        self.state = "close"
        self.dispatch("on_close")

    def drop_stack(self):
        self.menu.dismiss()
        self.state = "close"
        self.dispatch("on_close")


class DropDownMenu(CustomFloatingActionButtonSpeedDial):
    pass
