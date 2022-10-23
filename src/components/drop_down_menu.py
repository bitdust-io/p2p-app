from kivy.metrics import dp
from kivy.properties import ObjectProperty, OptionProperty, ListProperty, NumericProperty, StringProperty, ColorProperty  # @UnresolvedImport
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.graphics.vertex_instructions import Line  # @UnresolvedImport
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window

from kivymd.theming import ThemableBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import IRightBodyTouch, OneLineListItem, OneLineAvatarIconListItem, OneLineRightIconListItem
from kivymd.uix.behaviors import HoverBehavior

import kivymd.material_resources as m_res

#------------------------------------------------------------------------------

from components import screen

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

class DropdownMenuItemBase(HoverBehavior):

    def on_enter(self):
        self.parent.parent.drop_cls.set_bg_color_items(self)
        self.parent.parent.drop_cls.dispatch("on_enter", self)

    def on_leave(self):
        self.parent.parent.drop_cls.dispatch("on_leave", self)


class DropdownMenuItem(DropdownMenuItemBase, OneLineListItem):
    pass


class DropdownMenuItemIcon(DropdownMenuItemBase, OneLineAvatarIconListItem):
    icon = StringProperty()


class DropdownMenuItemRight(DropdownMenuItemBase, OneLineRightIconListItem):
    pass


class DropdownRightContent(IRightBodyTouch, MDBoxLayout):
    text = StringProperty()
    icon = StringProperty()


class BaseMenu(ScrollView):
    width_mult = NumericProperty(1)
    drop_cls = ObjectProperty()


class BaseDropdownMenu(ThemableBehavior, FloatLayout):

    selected_color = ColorProperty(None)
    items = ListProperty()
    width_mult = NumericProperty(1)
    max_height = NumericProperty()
    border_margin = NumericProperty("4dp")
    ver_growth = OptionProperty(None, allownone=True, options=["up", "down"])
    hor_growth = OptionProperty(None, allownone=True, options=["left", "right"])
    background_color = ColorProperty(None)
    opening_transition = StringProperty("out_cubic")
    opening_time = NumericProperty(0.2)
    caller = ObjectProperty()
    position = OptionProperty("auto", options=["auto", "center", "bottom"])
    radius = ListProperty([dp(7), ])
    _start_coords = []
    _calculate_complete = False
    _calculate_process = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_resize=self.check_position_caller)
        Window.bind(on_maximize=self.set_menu_properties)
        Window.bind(on_restore=self.set_menu_properties)
        self.register_event_type("on_dismiss")
        self.register_event_type("on_enter")
        self.register_event_type("on_leave")
        self.register_event_type("on_release")
        self.target_height = 0

    def check_position_caller(self, instance, width, height):
        self.set_menu_properties(0)

    def set_bg_color_items(self, instance_selected_item):
        if self.selected_color:
            for item in self.ids.md_menu.ids.box.children:
                if item is not instance_selected_item:
                    item.bg_color = (0, 0, 0, 0)
                else:
                    instance_selected_item.bg_color = self.selected_color

    def set_menu_properties(self, interval=0):
        if self.caller:
            if _Debug:
                print('BaseDropdownMenu.set_menu_properties', self.ids.md_menu, type(self.ids.md_menu))
            if not self.ids.md_menu.ids.box.children:
                self.create_menu_items()
            # We need to pick a starting point, see how big we need to be,
            # and where to grow to.
            self._start_coords = self.caller.to_window(
                self.caller.center_x, self.caller.center_y
            )
            self.target_width = self.width_mult * m_res.STANDARD_INCREMENT

            # If we're wider than the Window...
            if self.target_width > Window.width:
                # ...reduce our multiplier to max allowed.
                self.target_width = (
                    int(Window.width / m_res.STANDARD_INCREMENT)
                    * m_res.STANDARD_INCREMENT
                )

            # Set the target_height of the menu depending on the size of
            # each MDMenuItem or MDMenuItemIcon
            self.target_height = 0
            for item in self.ids.md_menu.ids.box.children:
                self.target_height += item.height

            # If we're over max_height...
            if 0 < self.max_height < self.target_height:
                self.target_height = self.max_height

            # Establish vertical growth direction.
            if self.ver_growth is not None:
                ver_growth = self.ver_growth
            else:
                # If there's enough space below us:
                if (
                    self.target_height
                    <= self._start_coords[1] - self.border_margin
                ):
                    ver_growth = "down"
                # if there's enough space above us:
                elif (
                    self.target_height
                    < Window.height - self._start_coords[1] - self.border_margin
                ):
                    ver_growth = "up"
                # Otherwise, let's pick the one with more space and adjust ourselves.
                else:
                    # If there"s more space below us:
                    if (
                        self._start_coords[1]
                        >= Window.height - self._start_coords[1]
                    ):
                        ver_growth = "down"
                        self.target_height = (
                            self._start_coords[1] - self.border_margin
                        )
                    # If there's more space above us:
                    else:
                        ver_growth = "up"
                        self.target_height = (
                            Window.height
                            - self._start_coords[1]
                            - self.border_margin
                        )

            if self.hor_growth is not None:
                hor_growth = self.hor_growth
            else:
                # If there's enough space to the right:
                if (
                    self.target_width
                    <= Window.width - self._start_coords[0] - self.border_margin
                ):
                    hor_growth = "right"
                # if there's enough space to the left:
                elif (
                    self.target_width
                    < self._start_coords[0] - self.border_margin
                ):
                    hor_growth = "left"
                # Otherwise, let's pick the one with more space and adjust ourselves.
                else:
                    # if there"s more space to the right:
                    if (
                        Window.width - self._start_coords[0]
                        >= self._start_coords[0]
                    ):
                        hor_growth = "right"
                        self.target_width = (
                            Window.width
                            - self._start_coords[0]
                            - self.border_margin
                        )
                    # if there"s more space to the left:
                    else:
                        hor_growth = "left"
                        self.target_width = (
                            self._start_coords[0] - self.border_margin
                        )

            if ver_growth == "down":
                self.tar_y = self._start_coords[1] - self.target_height
            else:  # should always be "up"
                self.tar_y = self._start_coords[1]

            if hor_growth == "right":
                self.tar_x = self._start_coords[0]
            else:  # should always be "left"
                self.tar_x = self._start_coords[0] - self.target_width
            self._calculate_complete = True

    def open(self):

        def _open(interval):
            if not self._calculate_complete:
                return
            if self.position == "auto":
                self.ids.md_menu.pos = self._start_coords
                anim = Animation(
                    x=self.tar_x,
                    y=self.tar_y,
                    width=self.target_width,
                    height=self.target_height,
                    duration=self.opening_time,
                    opacity=1,
                    transition=self.opening_transition,
                )
                anim.start(self.ids.md_menu)
            else:
                if self.position == "center":
                    self.ids.md_menu.pos = (
                        self._start_coords[0] - self.target_width / 2,
                        self._start_coords[1] - self.target_height / 2,
                    )
                elif self.position == "bottom":
                    self.ids.md_menu.pos = (
                        self._start_coords[0] - self.target_width / 2,
                        self.caller.pos[1] - self.target_height,
                    )
                anim = Animation(
                    width=self.target_width,
                    height=self.target_height,
                    duration=self.opening_time,
                    opacity=1,
                    transition=self.opening_transition,
                )
            anim.start(self.ids.md_menu)
            Window.add_widget(self)
            Clock.unschedule(_open)
            self._calculate_process = False

        self.set_menu_properties()
        if not self._calculate_process:
            self._calculate_process = True
            Clock.schedule_interval(_open, 0)

    def on_touch_down(self, touch):
        if not self.ids.md_menu.collide_point(*touch.pos):
            self.dispatch("on_dismiss")
            return True
        super().on_touch_down(touch)
        return True

    def on_touch_move(self, touch):
        super().on_touch_move(touch)
        return True

    def on_touch_up(self, touch):
        super().on_touch_up(touch)
        return True

    def on_enter(self, instance):
        """Call when mouse enter the bbox of the item of menu."""

    def on_leave(self, instance):
        """Call when the mouse exit the item of menu."""

    def on_release(self, *args):
        """The method that will be called when you click menu items."""

    def on_dismiss(self):
        Window.remove_widget(self)
        self.ids.md_menu.width = 0
        self.ids.md_menu.height = 0
        self.ids.md_menu.opacity = 0

    def dismiss(self):
        self.on_dismiss()

    def create_menu_items(self):
        for data in self.items:
            if data.get("icon") and data.get("right_content_cls", None):
                item = DropdownMenuItemIcon(
                    text=data.get("text", ""),
                    divider=data.get("divider", "Full"),
                    _txt_top_pad=data.get("top_pad", "20dp"),
                    _txt_bot_pad=data.get("bot_pad", "20dp"),
                )
            elif data.get("icon"):
                item = DropdownMenuItemIcon(
                    text=data.get("text", ""),
                    divider=data.get("divider", "Full"),
                    _txt_top_pad=data.get("top_pad", "20dp"),
                    _txt_bot_pad=data.get("bot_pad", "20dp"),
                )
            elif data.get("right_content_cls", None):
                item = DropdownMenuItemRight(
                    text=data.get("text", ""),
                    divider=data.get("divider", "Full"),
                    _txt_top_pad=data.get("top_pad", "20dp"),
                    _txt_bot_pad=data.get("bot_pad", "20dp"),
                )
            else:
                item = DropdownMenuItem(
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
            if isinstance(right_content_cls, DropdownRightContent):
                item.ids._right_container.width = right_content_cls.width + dp(20)
                item.ids._right_container.padding = ("10dp", 0, 0, 0)
                item.add_widget(right_content_cls)
            else:
                if "_right_container" in item.ids:
                    item.ids._right_container.width = 0
            for c in item.canvas.children:
                if isinstance(c, Line):
                    item.canvas.remove(c)
            # if data.get('icon_pack') and data.get("icon"):
            #     item.ids.icon_widget.ids.lbl_txt.icon = 'ab-testing'  # small hack to overcome canvas rule of the MDIcon
            #     item.ids.icon_widget.ids.lbl_txt.text = webfont.make_icon(data.get("icon"), data.get('icon_pack'))
            #     item.ids.icon_widget.ids.lbl_txt.font_style = data.get('icon_pack')
            self.ids.md_menu.ids.box.add_widget(item)


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
        self.menu = BaseDropdownMenu(
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

#------------------------------------------------------------------------------

class DropDownMenu(CustomFloatingActionButtonSpeedDial):
    pass
