from kivy.animation import Animation
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import ObjectProperty, BooleanProperty, OptionProperty, ColorProperty, DictProperty, NumericProperty, StringProperty  # @UnresolvedImport
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout

from kivymd.theming import ThemableBehavior
from kivymd.uix.behaviors import RectangularElevationBehavior
from kivymd.uix.button import MDFloatingActionButton
from kivymd.uix.tooltip import MDTooltip


class BaseFloatingRootButton(MDFloatingActionButton):
    _angle = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.elevation = 0

    def set_size(self, interval):
        self.width = "32dp"
        self.height = "32dp"


class BaseFloatingBottomButton(MDFloatingActionButton, MDTooltip):
    _canvas_width = NumericProperty(0)
    _padding_right = NumericProperty(0)
    _bg_color = ColorProperty(None)

    def set_size(self, interval):
        self.width = "32dp"
        self.height = "32dp"


class BaseFloatingLabel(ThemableBehavior, RectangularElevationBehavior, BoxLayout):
    text = StringProperty()
    text_color = ColorProperty(None)
    bg_color = ColorProperty(None)


class CustomFloatingBottomButton(BaseFloatingBottomButton):
    pass


class CustomFloatingRootButton(BaseFloatingRootButton):
    pass


class CustomFloatingLabel(BaseFloatingLabel):
    pass


class CustomFloatingActionButtonSpeedDial(ThemableBehavior, FloatLayout):
    icon = StringProperty("dots-vertical")
    anchor = OptionProperty("right", option=["right"])
    callback = ObjectProperty(lambda x: None)
    label_text_color = ColorProperty([0, 0, 0, 1])
    data = DictProperty()
    right_pad = BooleanProperty(True)
    root_button_anim = BooleanProperty(False)
    opening_transition = StringProperty("out_cubic")
    closing_transition = StringProperty("out_cubic")
    opening_transition_button_rotation = StringProperty("out_cubic")
    closing_transition_button_rotation = StringProperty("out_cubic")
    opening_time = NumericProperty(0.2)
    closing_time = NumericProperty(0.2)
    opening_time_button_rotation = NumericProperty(0.2)
    closing_time_button_rotation = NumericProperty(0.2)
    state = OptionProperty("close", options=("close", "open"))
    bg_color_root_button = ColorProperty(None)
    bg_color_stack_button = ColorProperty(None)
    color_icon_stack_button = ColorProperty(None)
    color_icon_root_button = ColorProperty(None)
    bg_hint_color = ColorProperty(None)
    hint_animation = BooleanProperty(False)

    top_offset = dp(80)
    buttons_colors = DictProperty()
    logo = BooleanProperty(False)
    root_button_rotate_angle = NumericProperty(360)
    do_update_event = ObjectProperty(None, allownone=True)
    update_delay_s = NumericProperty(0.1)
    initialized = False

    _label_pos_y_set = False
    _anim_buttons_data = {}
    _anim_labels_data = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type("on_open")
        self.register_event_type("on_close")
        Window.bind(on_resize=self._update_pos_buttons)

    def on_open(self, *args):
        pass

    def on_close(self, *args):
        pass

    def on_leave(self, instance):
        if self.state == "open":
            for widget in self.children:
                if isinstance(widget, CustomFloatingLabel) and self.hint_animation:
                    Animation.cancel_all(widget)
                    if self.data[instance.icon] == widget.text:
                        Animation(
                            _canvas_width=0,
                            _padding_right=0,
                            d=self.opening_time,
                            t=self.opening_transition,
                        ).start(instance)
                        if self.hint_animation:
                            Animation(
                                opacity=0, d=0.1, t=self.opening_transition
                            ).start(widget)
                        break

    def on_enter(self, instance):
        if self.state == "open":
            for widget in self.children:
                if isinstance(widget, CustomFloatingLabel) and self.hint_animation:
                    widget.elevation = 0
                    if self.data[instance.icon] == widget.text:
                        Animation(
                            _canvas_width=widget.width + dp(24),
                            _padding_right=dp(5) if self.right_pad else 0,
                            d=self.opening_time,
                            t=self.opening_transition,
                        ).start(instance)
                        if self.hint_animation:
                            Animation(
                                opacity=1,
                                d=self.opening_time,
                                t=self.opening_transition,
                            ).start(widget)
                        break

    def on_data(self, instance, value):
        super().__init__()
        self.clear_widgets()
        self._anim_buttons_data = {}
        self._anim_labels_data = {}
        self._label_pos_y_set = False
        # Bottom buttons.
        for name_icon in value.keys():
            bottom_button = CustomFloatingBottomButton(
                icon=name_icon,
                on_enter=self.on_enter,
                on_leave=self.on_leave,
                opacity=0,
            )
            bottom_button.bind(
                on_release=lambda x=bottom_button: self.callback(x)
            )
            self.set_pos_bottom_buttons(bottom_button)
            self.add_widget(bottom_button)
            # Labels.
            floating_text = value[name_icon]
            if floating_text:
                label = CustomFloatingLabel(text=floating_text, opacity=0)
                label.text_color = self.label_text_color
                self.set_pos_labels(label)
                self.add_widget(label)
        # Top root button.
        root_button = CustomFloatingRootButton(on_release=self.open_stack)
        root_button.icon = self.icon
        self.set_pos_root_button(root_button)
        self.add_widget(root_button)
        # self._update_pos_buttons(instance, 0, 0)

    def on_buttons_colors(self, instance, value):
        for widget in self.children:
            if isinstance(widget, CustomFloatingBottomButton):
                if widget.icon in value:
                    widget.md_bg_color = value[widget.icon]
                    widget._bg_color = value[widget.icon][0:3] + [.6]
            if isinstance(widget, CustomFloatingLabel):
                label_icon = None
                for icn, txt in self.data.items():
                    if widget.text == txt:
                        label_icon = icn
                        break
                if label_icon and label_icon in value:
                    widget.bg_color = value[label_icon]

    def on_icon(self, instance, value):
        w = self._get_count_widget(CustomFloatingRootButton)
        if w:
            w.icon = value

    def on_label_text_color(self, instance, value):
        for widget in self.children:
            if isinstance(widget, CustomFloatingLabel):
                widget.text_color = value

    def on_color_icon_stack_button(self, instance, value):
        for widget in self.children:
            if isinstance(widget, CustomFloatingBottomButton):
                widget.text_color = value

    def on_hint_animation(self, instance, value):
        for widget in self.children:
            if isinstance(widget, CustomFloatingLabel):
                widget.bg_color = (0, 0, 0, 0)

    def on_bg_hint_color(self, instance, value):
        for widget in self.children:
            if isinstance(widget, CustomFloatingBottomButton):
                widget._bg_color = value

    def on_color_icon_root_button(self, instance, value):
        w = self._get_count_widget(CustomFloatingRootButton)
        if w:
            w.text_color = value

    def on_bg_color_stack_button(self, instance, value):
        for widget in self.children:
            if isinstance(widget, CustomFloatingBottomButton):
                widget.md_bg_color = value

    def on_bg_color_root_button(self, instance, value):
        w = self._get_count_widget(CustomFloatingRootButton)
        if w:
            w.md_bg_color = value

    def set_pos_labels(self, widget):
        if self.anchor == "right":
            widget.x = Window.width - widget.width - dp(86)

    def set_pos_root_button(self, instance):
        if self.anchor == "right":
            instance.y = Window.height - self.top_offset
            instance.x = Window.width - (dp(36) + dp(20))

    def set_pos_bottom_buttons(self, instance):
        if self.anchor == "right":
            if self.state != "open":
                instance.y = Window.height - self.top_offset
            instance.x = Window.width - (instance.height + instance.width / 2) - dp(2)

    def open_stack(self, instance):
        for widget in self.children:
            if isinstance(widget, CustomFloatingLabel):
                Animation.cancel_all(widget)

        if self.state != "open":
            y = Window.height - self.top_offset
            label_position = Window.height - self.top_offset + dp(2)
            anim_buttons_data = {}
            anim_labels_data = {}

            for widget in self.children:
                if isinstance(widget, CustomFloatingBottomButton):
                    # Sets new button positions.
                    y -= dp(40)
                    widget.y = y
                    if not self._anim_buttons_data:
                        anim_buttons_data[widget] = Animation(
                            opacity=1,
                            d=self.opening_time,
                            t=self.opening_transition,
                        )
                elif isinstance(widget, CustomFloatingLabel):
                    # Sets new labels positions.
                    label_position -= dp(40)
                    # Sets the position of signatures only once.
                    if not self._label_pos_y_set:
                        widget.y = label_position + dp(3)
                        widget.x = Window.width - widget.width - dp(58)
                    if not self._anim_labels_data:
                        anim_labels_data[widget] = Animation(
                            opacity=1, d=self.opening_time
                        )
                elif (
                    isinstance(widget, CustomFloatingRootButton)
                    and self.root_button_anim
                ):
                    # Rotates the root button 45 degrees.
                    Animation(
                        _angle=-self.root_button_rotate_angle,
                        d=self.opening_time_button_rotation,
                        t=self.opening_transition_button_rotation,
                    ).start(widget)

            if anim_buttons_data:
                self._anim_buttons_data = anim_buttons_data
            if anim_labels_data and not self.hint_animation:
                self._anim_labels_data = anim_labels_data

            self.state = "open"
            self.dispatch("on_open")
            self.do_animation_open_stack(self._anim_buttons_data)
            self.do_animation_open_stack(self._anim_labels_data)
            if not self._label_pos_y_set:
                self._label_pos_y_set = True
        else:
            self.close_stack()

    def do_animation_open_stack(self, anim_data):
        def on_progress(animation, widget, value):
            if value >= 0.1:
                animation_open_stack()

        def animation_open_stack(*args):
            try:
                widget = next(widgets_list)
                animation = anim_data[widget]
                animation.bind(on_progress=on_progress)
                animation.start(widget)
            except StopIteration:
                pass

        widgets_list = iter(list(anim_data.keys()))
        animation_open_stack()

    def close_stack(self):
        for widget in self.children:
            if isinstance(widget, CustomFloatingBottomButton):
                Animation(
                    y=Window.height - self.top_offset,
                    d=self.closing_time,
                    t=self.closing_transition,
                    opacity=0,
                ).start(widget)
                widget._canvas_width = 0
                widget._padding_right = 0
            elif isinstance(widget, CustomFloatingLabel):
                Animation(opacity=0, d=0.1).start(widget)
            elif (
                isinstance(widget, CustomFloatingRootButton)
                and self.root_button_anim
            ):
                Animation(
                    _angle=0,
                    d=self.closing_time_button_rotation,
                    t=self.closing_transition_button_rotation,
                ).start(widget)
        self.state = "close"
        self.dispatch("on_close")

    def drop_stack(self):
        self._label_pos_y_set = False
        for widget in self.children:
            if isinstance(widget, CustomFloatingBottomButton):
                widget.opacity = 0
                widget.y = Window.height - self.top_offset
                widget._canvas_width = 0
                widget._padding_right = 0
            elif isinstance(widget, CustomFloatingLabel):
                widget.opacity = 0
            elif (
                isinstance(widget, CustomFloatingRootButton)
                and self.root_button_anim
            ):
                widget._angle = 0
        self.state = "close"
        self.dispatch("on_close")

    def do_update_pos_buttons(self, instance, width, height):
        # Updates button positions when resizing screen.
        for widget in self.children:
            if isinstance(widget, CustomFloatingBottomButton):
                self.set_pos_bottom_buttons(widget)
            elif isinstance(widget, CustomFloatingRootButton):
                self.set_pos_root_button(widget)
            elif isinstance(widget, CustomFloatingLabel):
                self.set_pos_labels(widget)

    def _update_pos_buttons(self, instance, width, height):
        if not self.initialized:
            self.initialized = True
            self.do_update_pos_buttons(instance, width, height)
            return
        self.drop_stack()
        if self.do_update_event is not None:
            self.do_update_event.cancel()
        real_do_update = self.do_update_pos_buttons
        self.do_update_event = Clock.schedule_once(lambda dt: real_do_update(instance, width, height), 0)

    def _get_count_widget(self, instance):
        widget = None
        for widget in self.children:
            if isinstance(widget, instance):
                break
        return widget


class RootActionButton(CustomFloatingActionButtonSpeedDial):
    pass
