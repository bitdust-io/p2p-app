import os
from typing import NoReturn, Union

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics.context_instructions import Color  # @UnresolvedImport
from kivy.graphics.vertex_instructions import Ellipse, RoundedRectangle, SmoothLine  # @UnresolvedImport
from kivy.metrics import dp
from kivy.properties import BooleanProperty, ColorProperty, ListProperty, NumericProperty, ObjectProperty, StringProperty  # @UnresolvedImport

from kivymd.theming import ThemableBehavior
from kivymd.uix.behaviors import TouchBehavior
from kivymd.uix.button import MDIconButton
from kivymd.uix.list import MDList
from kivymd.uix.relativelayout import MDRelativeLayout


uix_path = os.path.join(os.path.dirname(__file__), "uix")


class SelectionIconCheck(MDIconButton):
    scale = NumericProperty(0)
    icon_check_color = ColorProperty([0, 0, 0, 1])


class SelectionItem(ThemableBehavior, MDRelativeLayout, TouchBehavior):
    selected = BooleanProperty(False)
    owner = ObjectProperty()
    instance_item = ObjectProperty()
    instance_icon = ObjectProperty()
    overlay_color = ColorProperty([0, 0, 0, 0.2])
    progress_round_size = NumericProperty(dp(46))
    progress_round_color = ColorProperty(None)
    _progress_round = NumericProperty(0)
    _progress_line_end = NumericProperty(0)
    _progress_animation = BooleanProperty(False)
    _touch_long = BooleanProperty(False)
    _instance_progress_inner_circle_color = ObjectProperty()
    _instance_progress_inner_circle_ellipse = ObjectProperty()
    _instance_progress_inner_outer_color = ObjectProperty()
    _instance_progress_inner_outer_line = ObjectProperty()
    _instance_overlay_color = ObjectProperty()
    _instance_overlay_rounded_rec = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.duration_long_touch = 0.01
        Clock.schedule_once(self.set_progress_round)

    def set_progress_round(self, interval: Union[int, float]) -> NoReturn:
        with self.canvas.after:
            self._instance_progress_inner_circle_color = Color(
                rgba=(0, 0, 0, 0)
            )
            self._instance_progress_inner_circle_ellipse = Ellipse(
                size=self.get_progress_round_size(),
                pos=self.get_progress_round_pos(),
            )
            self.bind(
                pos=self.update_progress_inner_circle_ellipse,
                size=self.update_progress_inner_circle_ellipse,
            )
            # FIXME: Radius value is not displayed.
            self._instance_overlay_color = Color(rgba=(0, 0, 0, 0))
            self._instance_overlay_rounded_rec = RoundedRectangle(
                size=self.size,
                pos=self.pos,
                radius=self.instance_item.radius if hasattr(self.instance_item, "radius") else [0, ],
            )
            self.bind(
                pos=self.update_overlay_rounded_rec,
                size=self.update_overlay_rounded_rec,
            )
            self._instance_progress_inner_outer_color = Color(rgba=(0, 0, 0, 0))
            self._instance_progress_inner_outer_line = SmoothLine(
                width=dp(4),
                circle=[
                    self.center_x,
                    self.center_y,
                    self.progress_round_size * 0.58,
                    0,
                    0,
                ],
            )

    def do_selected_item(self, *args) -> NoReturn:
        Animation(scale=1, d=0.2).start(self.instance_icon)
        self.selected = True
        self._progress_animation = False
        self._instance_overlay_color.rgba = self.get_overlay_color()
        self.owner.dispatch("on_selected", self)

    def do_unselected_item(self) -> NoReturn:
        Animation(scale=0, d=0.2).start(self.instance_icon)
        self.selected = False
        self._instance_overlay_color.rgba = self.get_overlay_color()
        self.owner.dispatch("on_unselected", self)

    def do_animation_progress_line(
        self, animation: Animation, instance_selection_item, value: float
    ) -> NoReturn:
        self._instance_progress_inner_outer_line.circle = (
            self.center_x,
            self.center_y,
            self.progress_round_size * 0.58,
            0,
            360 * value,
        )

    def update_overlay_rounded_rec(self, *args) -> NoReturn:
        self._instance_overlay_rounded_rec.size = self.size
        self._instance_overlay_rounded_rec.pos = self.pos

    def update_progress_inner_circle_ellipse(self, *args) -> NoReturn:
        self._instance_progress_inner_circle_ellipse.size = (
            self.get_progress_round_size()
        )
        self._instance_progress_inner_circle_ellipse.pos = (
            self.get_progress_round_pos()
        )

    def reset_progress_animation(self) -> NoReturn:
        Animation.cancel_all(self)
        self._progress_animation = False
        self._instance_progress_inner_circle_color.rgba = (0, 0, 0, 0)
        self._instance_progress_inner_outer_color.rgba = (0, 0, 0, 0)
        self._instance_progress_inner_outer_line.circle = [
            self.center_x,
            self.center_y,
            self.progress_round_size * 0.58,
            0,
            0,
        ]
        self._progress_line_end = 0

    def get_overlay_color(self) -> list:
        return self.overlay_color if self.selected else (0, 0, 0, 0)

    def get_progress_round_pos(self) -> tuple:
        return (
            self.center_x - self.progress_round_size / 2,
            self.center_y - self.progress_round_size / 2,
        )

    def get_progress_round_size(self) -> tuple:
        return self.progress_round_size, self.progress_round_size

    def get_progress_round_color(self) -> tuple:
        return (
            self.theme_cls.primary_color
            if not self.progress_round_color
            else self.progress_round_color
        )

    def get_progress_line_color(self) -> tuple:
        return (
            self.theme_cls.primary_color[:-1] + [0.5]
            if not self.progress_round_color
            else self.progress_round_color[:-1] + [0.5]
        )

    def on_long_touch(self, *args) -> NoReturn:
        if not self.owner.get_selected():
            self._touch_long = True
            self._progress_animation = True

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            if self._touch_long:
                self._touch_long = False
        return super().on_touch_up(touch)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.selected:
                self.do_unselected_item()
            else:
                if self.owner.selected_mode:
                    self.do_selected_item()
        return super().on_touch_down(touch)

    def on__touch_long(
        self, instance_selection_tem, touch_value: bool
    ) -> NoReturn:
        if not touch_value:
            self.reset_progress_animation()

    def on__progress_animation(
        self, instance_selection_tem, touch_value: bool
    ) -> NoReturn:
        if touch_value:
            anim = Animation(_progress_line_end=360, d=1, t="in_out_quad")
            anim.bind(
                on_progress=self.do_animation_progress_line,
                on_complete=self.do_selected_item,
            )
            anim.start(self)
            self._instance_progress_inner_outer_color.rgba = (
                self.get_progress_line_color()
            )
            self._instance_progress_inner_circle_color.rgba = (
                self.get_progress_round_color()
            )
        else:
            self.reset_progress_animation()


class CustomSelectionList(MDList):
    selected_mode = BooleanProperty(False)
    icon = StringProperty("check")
    icon_pos = ListProperty()
    icon_bg_color = ColorProperty([1, 1, 1, 1])
    icon_check_color = ColorProperty([0, 0, 0, 1])
    overlay_color = ColorProperty([0, 0, 0, 0.2])
    progress_round_size = NumericProperty(dp(46))
    progress_round_color = ColorProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type("on_selected")
        self.register_event_type("on_unselected")

    def add_widget(self, widget, index=0, canvas=None):
        selection_icon = SelectionIconCheck(
            icon=self.icon,
            md_bg_color=self.icon_bg_color,
            icon_check_color=self.icon_check_color,
        )
        container = SelectionItem(
            size_hint=(1, None),
            height=widget.height,
            instance_item=widget,
            instance_icon=selection_icon,
            overlay_color=self.overlay_color,
            progress_round_size=self.progress_round_size,
            progress_round_color=self.progress_round_color,
            owner=self,
        )
        container.add_widget(widget)

        if not self.icon_pos:
            pos = (
                dp(12),
                container.height / 2 - selection_icon.height / 2,
            )
        else:
            pos = self.icon_pos
        selection_icon.pos = pos
        container.add_widget(selection_icon)
        return super().add_widget(container, index, canvas)

    def get_selected(self) -> bool:
        selected = False
        for item in self.children:
            if item.selected:
                selected = True
                break
        return selected

    def get_selected_list_items(self) -> list:
        selected_list_items = []
        for item in self.children:
            if item.selected:
                selected_list_items.append(item)
        return selected_list_items

    def unselected_all(self) -> NoReturn:
        for item in self.children:
            item.do_unselected_item()
        self.selected_mode = False

    def selected_all(self) -> NoReturn:
        for item in self.children:
            item.do_selected_item()
        self.selected_mode = True

    def on_selected(self, *args):
        if not self.selected_mode:
            self.selected_mode = True

    def on_unselected(self, *args):
        self.selected_mode = self.get_selected()
