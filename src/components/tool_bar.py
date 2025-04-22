import time

from math import cos, radians, sin

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import (
    BooleanProperty,  # @UnresolvedImport
    ColorProperty,  # @UnresolvedImport
    ListProperty,  # @UnresolvedImport
    NumericProperty,  # @UnresolvedImport
    OptionProperty,  # @UnresolvedImport
    StringProperty,  # @UnresolvedImport
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout

from kivymd.color_definitions import text_colors
from kivymd.theming import ThemableBehavior
from kivymd.uix.behaviors import (
    RectangularElevationBehavior,
    SpecificBackgroundColorBehavior,
)
from kivymd.uix.toolbar.toolbar import NotchedBox, ActionTopAppBarButton
from kivymd.uix.tooltip import MDTooltip

#------------------------------------------------------------------------------

from lib import system

from components import buttons
from components import styles

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

class CustomActionAppBarButton(buttons.TransparentIconButton, MDTooltip, styles.AppStyle):
    anim = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.shift_y = dp(60)
        self.duration_long_touch = 0

    def start_blinking(self):
        if _Debug:
            print('CustomActionAppBarButton.start_blinking %r %r' % (self.icon, time.asctime()))
        if self.anim:
            self.anim.stop(self)
            self.anim = None
        self.anim = (
            Animation(text_color=self.state2color(-1), duration=.3) +
            Animation(text_color=self.state2color(1), duration=.3)
        )
        self.anim.repeat = True
        self.anim.start(self)

    def stop_blinking(self):
        if _Debug:
            print('CustomActionAppBarButton.stop_blinking %r %r' % (self.icon, time.asctime()))
        if self.anim:
            self.anim.stop(self)
            self.anim = None

    def animation_tooltip_show(self, interval):
        super().animation_tooltip_show(interval)
        Clock.schedule_once(self.remove_tooltip, 5)

#------------------------------------------------------------------------------

class CustomFloatingActionButton(buttons.FloatingActionButton):
    _scale_x = NumericProperty(1)
    _scale_y = NumericProperty(1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if _Debug:
            print('CustomFloatingActionButton.__init__')

    def set_size(self, interval):
        if _Debug:
            print('CustomFloatingActionButton.set_size')
        self.width = "44dp"
        self.height = "44dp"

#------------------------------------------------------------------------------

class CustomNotchedBox(
    ThemableBehavior,
    RectangularElevationBehavior,
    SpecificBackgroundColorBehavior,
    BoxLayout,
):
    standard_increment = NumericProperty('30dp')
    horizontal_margins = NumericProperty('12dp')
    notch_radius = NumericProperty()
    notch_center_x = NumericProperty("100dp")

    _indices_right = ListProperty()
    _vertices_right = ListProperty()
    _indices_left = ListProperty()
    _vertices_left = ListProperty()
    _rounded_rectangle_height = NumericProperty("6dp")
    _total_angle = NumericProperty(180)
    _rectangle_left_pos = ListProperty([0, 0])
    _rectangle_left_width = NumericProperty()
    _rectangle_right_pos = ListProperty([0, 0])
    _rectangle_right_width = NumericProperty()
    _rounding_percentage = NumericProperty(0.15)

    elevation = NumericProperty(6)

    def __init__(self, **kw):
        super().__init__(**kw)
        self.bind(
            size=self._update_canvas,
            pos=self._update_canvas,
            notch_radius=self._update_canvas,
            notch_center_x=self._update_canvas,
        )
        Clock.schedule_once(self._update_canvas)

    def _update_canvas(self, *args):
        pos = self.pos
        size = [
            self.width,
            self.size[1] - self._rounded_rectangle_height / 2,
        ]
        notch_center_x = self.notch_center_x

        circle_radius = self.notch_radius
        degree_diff = int((180 - self._total_angle) / 2)
        circle_center = [notch_center_x, pos[1] + size[1]]
        left_circle_pos = self._points_on_circle(
            circle_center, circle_radius, 180 + degree_diff, 270
        )

        self._rectangle_left_pos = [
            pos[0],
            pos[1] + size[1] - self._rounded_rectangle_height / 2,
        ]
        self._rectangle_left_width = left_circle_pos[0][0] - self.pos[0]

        right_circle_pos = self._points_on_circle(
            circle_center, circle_radius, -degree_diff, -90
        )

        self._rectangle_right_pos = [
            right_circle_pos[0][0],
            pos[1] + size[1] - self._rounded_rectangle_height / 2,
        ]
        self._rectangle_right_width = pos[0] + size[0] - right_circle_pos[0][0]

        raw_vertices_left = self._make_vertices(
            pos, [notch_center_x - pos[0], size[1]], "left", left_circle_pos
        )
        raw_vertices_right = self._make_vertices(
            [notch_center_x, pos[1]],
            [size[0] + pos[0] - notch_center_x, size[1]],
            "right",
            right_circle_pos,
        )

        left_vertices, left_indices = self._make_vertices_indices(
            raw_vertices_left
        )
        right_vertices, right_indices = self._make_vertices_indices(
            raw_vertices_right
        )

        self._update_mesh(left_vertices, left_indices, "left")
        self._update_mesh(right_vertices, right_indices, "right")

    def _update_mesh(self, vertices, indices, mode):
        if mode == "left":
            self._indices_left = indices
            self._vertices_left = vertices
        else:
            self._indices_right = indices
            self._vertices_right = vertices
        return True

    @staticmethod
    def _make_vertices_indices(points_list):
        vertices = []
        indices = []
        for index, point in enumerate(points_list):
            indices.append(index)
            vertices.extend([point[0], point[1], 0, 0])

        return [vertices, indices]

    @staticmethod
    def _make_vertices(rectangle_pos, rectangle_size, mode, notch_points=[]):
        x = rectangle_pos[0]
        y = rectangle_pos[1]
        w = rectangle_size[0]
        h = rectangle_size[1]

        if mode == "left":
            rectangle_vertices = [[x, y], [x, y + h]]
        elif mode == "right":
            rectangle_vertices = [[x + w, y], [x + w, y + h]]
        rectangle_vertices.extend(notch_points)
        if mode == "left":
            rectangle_vertices.extend([[x + w, y]])
        elif mode == "right":
            rectangle_vertices.extend([[x, y]])

        return rectangle_vertices

    @staticmethod
    def _points_on_circle(center, radius, start_angle, end_angle):
        points = []
        y_diff = False
        if end_angle >= 180:
            step = 1
            end_angle += 1
        elif end_angle <= 0:
            step = -1
            end_angle -= 1
        else:
            raise Exception("Invalid value for start angle")

        for degree in range(start_angle, end_angle, step):

            angle = radians(degree)
            x = center[0] + (radius * cos(angle))
            y = center[1] + (radius * sin(angle))

            if y_diff is False:
                y_diff = abs(y - center[1])

            y += y_diff
            points.append([x, y])

        return points


#------------------------------------------------------------------------------

class CustomTopToolbar(NotchedBox):
    left_action_items = ListProperty()
    right_action_items = ListProperty()
    title = StringProperty()
    anchor_title = OptionProperty("left", options=["left", "center", "right"])
    mode = OptionProperty(
        "center", options=["free-end", "free-center", "end", "center"]
    )
    round = NumericProperty("10dp")
    icon = StringProperty("android")
    icon_color = ColorProperty()
    type = OptionProperty("top", options=["top", "bottom"])
    opposite_colors = BooleanProperty(False)
    _shift = NumericProperty("3.5dp")

    def __init__(self, **kwargs):
        self.top_action_button = CustomFloatingActionButton()
        self.latest_left_action_items = []
        self.latest_right_action_items = []
        super().__init__(**kwargs)
        self.register_event_type("on_action_button")
        self.top_action_button.bind(center_x=self.setter("notch_center_x"))
        self.top_action_button.bind(
            on_release=lambda x: self.dispatch("on_action_button")
        )
        self.top_action_button.x = Window.width / 2 - self.top_action_button.width / 2
        self.top_action_button.y = (
            (self.center[1] - self.height / 2)
            + self.theme_cls.standard_increment / 2
            + self._shift
        )
        if not self.icon_color:
            self.icon_color = self.theme_cls.primary_color
        Window.bind(on_resize=self._on_resize)
        self.bind(specific_text_color=self.update_top_action_bar_text_colors)
        # self.bind(opposite_colors=self.update_opposite_colors)
        self.theme_cls.bind(primary_palette=self.update_md_bg_color)
        Clock.schedule_once(
            lambda x: self.on_left_action_items(0, self.left_action_items)
        )
        Clock.schedule_once(
            lambda x: self.on_right_action_items(0, self.right_action_items)
        )
        Clock.schedule_once(lambda x: self.set_md_bg_color(0, self.md_bg_color))
        Clock.schedule_once(lambda x: self.on_mode(None, self.mode))

    def on_action_button(self, *args):
        pass

    def on_md_bg_color(self, instance, value):
        if self.type == "bottom":
            self.md_bg_color = [0, 0, 0, 0]

    def on_left_action_items(self, instance, value):
        if self.latest_left_action_items != [i[0] for i in value]:
            self.update_top_action_bar(self.ids["left_actions"], value)
            self.latest_left_action_items = [i[0] for i in value]

    def on_right_action_items(self, instance, value):
        if self.latest_right_action_items != [i[0] for i in value]:
            self.update_top_action_bar(self.ids["right_actions"], value)
            self.latest_right_action_items = [i[0] for i in value]

    def set_md_bg_color(self, instance, value):
        if value == [1.0, 1.0, 1.0, 0.0]:
            self.md_bg_color = self.theme_cls.primary_color

    def update_top_action_bar(self, action_bar, action_bar_items):
        if _Debug:
            print('CustomTopToolbar.update_top_action_bar', self.specific_text_color, self.opposite_colors, action_bar, action_bar_items)
        action_bar.clear_widgets()
        new_width = 0
        for item in action_bar_items:
            new_width += dp(48)
            if len(item) == 1:
                item.append(lambda x: None)
            if len(item) > 1 and not item[1]:
                item[1] = lambda x: None
            if len(item) == 2:
                if type(item[1]) is str:
                    item.insert(1, lambda x: None)
                else:
                    item.append("")
            b = ActionTopAppBarButton(
                icon=item[0],
                on_release=item[1],
                tooltip_text=item[2],
                theme_text_color="Custom" if not self.opposite_colors else "Primary",
                text_color=self.specific_text_color,
                opposite_colors=self.opposite_colors,
            )
            b.theme_icon_color = "Custom"
            b._icon_color = self.specific_text_color
            action_bar.add_widget(b)
        action_bar.width = new_width

    def update_md_bg_color(self, *args):
        self.md_bg_color = self.theme_cls._get_primary_color()
        if _Debug:
            print('CustomTopToolbar.update_md_bg_color', self.md_bg_color)

    def update_opposite_colors(self, instance, value):
        if value:
            self.ids.label_title.theme_text_color = ""
        if _Debug:
            print('CustomTopToolbar.update_opposite_colors', value)

    def update_top_action_bar_text_colors(self, *args):
        for child in self.ids["left_actions"].children:
            child.text_color = self.specific_text_color
        for child in self.ids["right_actions"].children:
            child.text_color = self.specific_text_color
        if _Debug:
            print('CustomTopToolbar.update_top_action_bar_text_colors', args)

    def on_icon(self, instance, value):
        self.top_action_button.icon = value

    def on_icon_color(self, instance, value):
        self.top_action_button.md_bg_color = value

    def on_mode(self, instance, value):
        def set_button_pos(*args):
            self.top_action_button.x = x
            self.top_action_button.y = y - self._rounded_rectangle_height / 2
            self.top_action_button._hard_shadow_size = (0, 0)
            self.top_action_button._soft_shadow_size = (0, 0)
            anim = Animation(_scale_x=1, _scale_y=1, d=0)
            anim.bind(on_complete=self.set_shadow)
            anim.start(self.top_action_button)
            if _Debug:
                print('CustomTopToolbar.on_mode.set_button_pos', self.top_action_button.x, self.top_action_button.y, self.top_action_button.disabled, self.top_action_button.parent)

        if value == "center":
            self.set_notch()
            x = Window.width / 2 - self.top_action_button.width / 2
            y = (
                (self.center[1] - self.height / 2)
                + self.theme_cls.standard_increment / 2
                + self._shift
            )
        elif value == "end":

            self.set_notch()
            x = Window.width - self.top_action_button.width * 2
            y = (
                (self.center[1] - self.height / 2)
                + self.theme_cls.standard_increment / 2
                + self._shift
            )
            self.right_action_items = []
        elif value == "free-end":
            self.remove_notch()
            x = Window.width - self.top_action_button.width - dp(10)
            y = self.top_action_button.height + self.top_action_button.height / 2
        elif value == "free-center":
            self.remove_notch()
            x = Window.width / 2 - self.top_action_button.width / 2
            y = self.top_action_button.height + self.top_action_button.height / 2
        self.remove_shadow()
        anim = Animation(_scale_x=0, _scale_y=0, d=0)
        anim.bind(on_complete=set_button_pos)
        anim.start(self.top_action_button)

    def remove_notch(self):
        anim = Animation(d=0.1) + Animation(
            notch_radius=0,
            d=0.1,
        )
        anim.start(self)

    def set_notch(self):
        anim = Animation(d=0.1) + Animation(
            notch_radius=self.top_action_button.width / 2 + dp(8),
            d=0.1,
        )
        anim.start(self)

    def remove_shadow(self):
        self.top_action_button._hard_shadow_size = (0, 0)
        self.top_action_button._soft_shadow_size = (0, 0)

    def set_shadow(self, *args):
        self.top_action_button._hard_shadow_size = (dp(112), dp(112))
        self.top_action_button._soft_shadow_size = (dp(112), dp(112))

    def _on_resize(self, instance, width, height):
        if self.mode == "center":
            self.top_action_button.x = width / 2 - self.top_action_button.width / 2
        else:
            self.top_action_button.x = width - self.top_action_button.width * 2

    def _update_specific_text_color(self, instance, value):
        if self.specific_text_color in (
            [0.0, 0.0, 0.0, 0.87],
            [0.0, 0.0, 0.0, 1.0],
            [1.0, 1.0, 1.0, 1.0],
        ):
            self.specific_text_color = text_colors[
                self.theme_cls.primary_palette
            ][self.theme_cls.primary_hue]

#------------------------------------------------------------------------------

class CustomBottomToolbar(CustomNotchedBox, styles.AppStyle):

    left_action_items = ListProperty()
    right_action_items = ListProperty()
    title = StringProperty()
    anchor_title = OptionProperty("left", options=["left", "center", "right"])
    mode = OptionProperty(
        "center", options=["free-end", "free-center", "end", "center"]
    )
    round = NumericProperty("2dp")
    icon = StringProperty("android")
    icon_color = ColorProperty()
    type = OptionProperty("top", options=["top", "bottom"])
    opposite_colors = BooleanProperty(True)
    _shift = NumericProperty("26dp")

    def __init__(self, **kwargs):
        self.bottom_action_button = CustomFloatingActionButton()
        super().__init__(**kwargs)
        self.register_event_type("on_action_button")
        self.bottom_action_button.bind(center_x=self.setter("notch_center_x"))
        self.bottom_action_button.bind(
            on_release=lambda x: self.dispatch("on_action_button")
        )
        self.bottom_action_button.x = Window.width / 2 - self.bottom_action_button.width / 2
        self.bottom_action_button.y = (
            (self.center[1] - self.height / 2)
            + self.theme_cls.standard_increment / 2
            - self._shift
        )
        if system.is_android():
            self.bottom_action_button.y = self.bottom_action_button.y + dp(4)
        if not self.icon_color:
            self.icon_color = self.theme_cls.primary_color
        Window.bind(on_resize=self._on_resize)
        self.bind(specific_text_color=self.update_bottom_action_bar_text_colors)
        self.theme_cls.bind(primary_palette=self.update_md_bg_color)
        Clock.schedule_once(
            lambda x: self.on_left_action_items(0, self.left_action_items)
        )
        Clock.schedule_once(
            lambda x: self.on_right_action_items(0, self.right_action_items)
        )
        Clock.schedule_once(lambda x: self.set_md_bg_color(0, self.md_bg_color))
        Clock.schedule_once(lambda x: self.on_mode(None, self.mode))

    def set_bottom_action_button(self, icon, color=None):
        if icon:
            self.bottom_action_button.md_bg_color = color or self.theme_cls.primary_color
            self.bottom_action_button.icon = icon
            self.bottom_action_button.disabled = False
            self.on_mode(None, 'end')
        else:
            self.bottom_action_button.md_bg_color = [0, 0, 0, 0, ]
            self.bottom_action_button.md_bg_color_disabled = [0, 0, 0, 0, ]
            self.bottom_action_button.icon = ''
            self.bottom_action_button.disabled = True
            self.on_mode(None, 'end')
            self.remove_notch()

    def on_action_button(self, *args):
        if _Debug:
            print('CustomBottomToolbar.on_action_button', args)

    def on_md_bg_color(self, instance, value):
        if self.type == "bottom":
            self.md_bg_color = [0, 0, 0, 0]

    def on_left_action_items(self, instance, value):
        self.update_bottom_action_bar(self.ids["left_actions"], value)

    def on_right_action_items(self, instance, value):
        self.update_bottom_action_bar(self.ids["right_actions"], value)

    def set_md_bg_color(self, instance, value):
        if value == [1.0, 1.0, 1.0, 0.0]:
            self.md_bg_color = self.theme_cls.primary_color

    def update_bottom_action_bar(self, action_bar, action_bar_items):
        action_bar.clear_widgets()
        new_width = 0
        for item in action_bar_items:
            new_width += dp(48)
            w = CustomActionAppBarButton(
                icon=item['icon'],
                icon_pack=item.get('icon_pack') or 'Icon',
                icon_size=item.get('size') or '22sp',
                button_width=self.height,
                button_height=self.height,
                theme_text_color="Custom",
                text_color=self.state2color(-1),
                tooltip_text=item.get('tooltip') or '',
                on_release=item.get('cb') or (lambda x: None),
            )
            action_bar.add_widget(w)
        action_bar.width = new_width

    def get_action_bar_item(self, icon_name):
        for w in self.ids["left_actions"].children:
            if w.icon == icon_name:
                return w
        for w in self.ids["right_actions"].children:
            if w.icon == icon_name:
                return w
        return None

    def update_bottom_action_bar_item(self, icon_name, state):
        itm = self.get_action_bar_item(icon_name)
        if itm:
            if state == 0:
                itm.start_blinking()
            else:
                itm.stop_blinking()
                itm.text_color = self.state2color(state)
        else:
            if _Debug:
                print('CustomBottomToolbar.update_action_bar_item item was not found for name %r' % icon_name)

    def update_md_bg_color(self, *args):
        self.md_bg_color = self.theme_cls._get_primary_color()

    def update_opposite_colors(self, instance, value):
        if value:
            self.ids.label_title.theme_text_color = ""

    def update_bottom_action_bar_text_colors(self, *args):
        for child in self.ids["left_actions"].children:
            child.text_color = self.specific_text_color
        for child in self.ids["right_actions"].children:
            child.text_color = self.specific_text_color

    def on_icon(self, instance, value):
        self.bottom_action_button.icon = value

    def on_icon_color(self, instance, value):
        self.bottom_action_button.md_bg_color = value

    def on_mode(self, instance, value):
        def set_button_pos(*args):
            self.bottom_action_button.x = x
            self.bottom_action_button.y = y - self._rounded_rectangle_height / 2
            self.bottom_action_button._hard_shadow_size = (0, 0)
            self.bottom_action_button._soft_shadow_size = (0, 0)
            anim = Animation(_scale_x=1, _scale_y=1, d=0)
            anim.bind(on_complete=self.set_shadow)
            anim.start(self.bottom_action_button)
            if _Debug:
                print('CustomBottomToolbar.on_mode.set_button_pos', self.bottom_action_button.x, self.bottom_action_button.y, self.bottom_action_button.disabled, self.bottom_action_button.parent)

        if value == "center":
            self.set_notch()
            x = Window.width / 2 - self.bottom_action_button.width / 2
            y = (
                (self.center[1] - self.height / 2)
                + self.theme_cls.standard_increment / 2
                - self._shift
            )
        elif value == "end":

            self.set_notch()
            x = Window.width - self.bottom_action_button.width * 2
            y = (
                (self.center[1] - self.height / 2)
                + self.theme_cls.standard_increment / 2
                - self._shift
            )
            #self.right_action_items = []
        elif value == "free-end":
            self.remove_notch()
            x = Window.width - self.bottom_action_button.width - dp(10)
            y = self.bottom_action_button.height + self.bottom_action_button.height / 2
        elif value == "free-center":
            self.remove_notch()
            x = Window.width / 2 - self.bottom_action_button.width / 2
            y = self.bottom_action_button.height + self.bottom_action_button.height / 2
        if system.is_android():
            y = y + dp(4)
        self.remove_shadow()
        anim = Animation(_scale_x=0, _scale_y=0, d=0)
        anim.bind(on_complete=set_button_pos)
        anim.start(self.bottom_action_button)

    def remove_notch(self):
        anim = Animation(d=0) + Animation(
            notch_radius=0,
            d=0,
        )
        anim.start(self)

    def set_notch(self):
        anim = Animation(d=0) + Animation(
            notch_radius=self.bottom_action_button.width / 2 + dp(5),
            d=0,
        )
        anim.start(self)

    def remove_shadow(self):
        self.bottom_action_button._hard_shadow_size = (0, 0)
        self.bottom_action_button._soft_shadow_size = (0, 0)

    def set_shadow(self, *args):
        self.bottom_action_button._hard_shadow_size = (dp(112), dp(112))
        self.bottom_action_button._soft_shadow_size = (dp(112), dp(112))

    def _on_resize(self, instance, width, height):
        if self.mode == "center":
            self.bottom_action_button.x = width / 2 - self.bottom_action_button.width / 2
        else:
            self.bottom_action_button.x = width - self.bottom_action_button.width * 2

    def _update_specific_text_color(self, instance, value):
        if self.specific_text_color in (
            [0.0, 0.0, 0.0, 0.87],
            [0.0, 0.0, 0.0, 1.0],
            [1.0, 1.0, 1.0, 1.0],
        ):
            self.specific_text_color = text_colors[
                self.theme_cls.primary_palette
            ][self.theme_cls.primary_hue]

#------------------------------------------------------------------------------

class CustomBottomAppBar(FloatLayout):
    md_bg_color = ColorProperty([0, 0, 0, 0])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None

    def add_widget(self, widget, index=0, canvas=None):
        if isinstance(widget, CustomBottomToolbar):
            super().add_widget(widget)
            return super().add_widget(widget.bottom_action_button)
        return super().add_widget(widget, index=index, canvas=canvas)
