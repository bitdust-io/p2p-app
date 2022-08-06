from kivy.metrics import dp
from kivy.properties import ObjectProperty, OptionProperty, ListProperty, NumericProperty  # @UnresolvedImport
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics.vertex_instructions import Line  # @UnresolvedImport

from kivymd.theming import ThemableBehavior
from kivymd.uix.menu import MDDropdownMenu, MDMenuItem, MDMenuItemIcon, MDMenuItemRight, RightContent

#------------------------------------------------------------------------------

from components import screen
from components import webfont

#------------------------------------------------------------------------------

class CustomDropdownMenu(MDDropdownMenu):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.card.elevation = 0

    def create_menu_items(self):
        for data in self.items:
            if data.get("icon") and data.get("right_content_cls", None):
                item = MDMenuItemIcon(
                    text=data.get("text", ""),
                    divider=data.get("divider", "Full"),
                    _txt_top_pad=data.get("top_pad", "20dp"),
                    _txt_bot_pad=data.get("bot_pad", "20dp"),
                )
            elif data.get("icon"):
                item = MDMenuItemIcon(
                    text=data.get("text", ""),
                    divider=data.get("divider", "Full"),
                    _txt_top_pad=data.get("top_pad", "20dp"),
                    _txt_bot_pad=data.get("bot_pad", "20dp"),
                )
            elif data.get("right_content_cls", None):
                item = MDMenuItemRight(
                    text=data.get("text", ""),
                    divider=data.get("divider", "Full"),
                    _txt_top_pad=data.get("top_pad", "20dp"),
                    _txt_bot_pad=data.get("bot_pad", "20dp"),
                )
            else:
                item = MDMenuItem(
                    text=data.get("text", ""),
                    divider=data.get("divider", "Full"),
                    _txt_top_pad=data.get("top_pad", "20dp"),
                    _txt_bot_pad=data.get("bot_pad", "20dp"),
                )
            if data.get("height", ""):
                item.height = data.get("height")
            if not data.get("icon"):
                item._txt_left_pad = data.get("left_pad", "32dp")
            else:
                item.icon = data.get("icon", "")
            item.bind(on_release=lambda x=item: self.dispatch("on_release", x))
            right_content_cls = data.get("right_content_cls", None)
            if isinstance(right_content_cls, RightContent):
                item.ids._right_container.width = right_content_cls.width + dp(20)
                item.ids._right_container.padding = ("10dp", 0, 0, 0)
                item.add_widget(right_content_cls)
            else:
                if "_right_container" in item.ids:
                    item.ids._right_container.width = 0
            for c in item.canvas.children:
                if isinstance(c, Line):
                    item.canvas.remove(c)
            if data.get('icon_pack') and data.get("icon"):
                item.ids.icon_widget.ids.lbl_txt.icon = 'ab-testing'  # small hack to overcome canvas rule of the MDIcon
                item.ids.icon_widget.ids.lbl_txt.text = webfont.make_icon(data.get("icon"), data.get('icon_pack'))
                item.ids.icon_widget.ids.lbl_txt.font_style = data.get('icon_pack')
            self.menu.ids.box.add_widget(item)

#------------------------------------------------------------------------------

class CustomFloatingActionButtonSpeedDial(ThemableBehavior, FloatLayout):
    callback = ObjectProperty(lambda x: None)
    data = ListProperty()
    width_mult = NumericProperty(5)
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

    def on_data(self, instance, value):
        menu_items = []
        for menu_item in value:
            itm = {
                "icon": menu_item[0],
                "text": menu_item[1],
                "viewclass": "OneLineListItem",
            }
            if len(menu_item) > 2:
                itm['icon_pack'] = menu_item[2]
            menu_items.append(itm)
        self.menu = CustomDropdownMenu(
            caller=screen.main_window().ids.dropdown_menu_placeholder,
            width_mult=self.width_mult,
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
