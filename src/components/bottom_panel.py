from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp

from kivymd.uix.toolbar import MDToolbar, MDActionBottomAppBarButton, MDActionTopAppBarButton, MDBottomAppBar


class BottomToolbarContainer(MDBottomAppBar):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.padding = [0, 0, ]
        self.minimum_height = 0

    def add_widget(self, widget, index=0, canvas=None):
        if isinstance(widget, BottomToolbar):
            super().add_widget(widget)
            return super().add_widget(widget.action_button)


class BottomToolbar(MDToolbar):

    action_button_offset_x = dp(52)
    action_button_offset_y = -dp(36)
    action_button_scale = 0.75
    toolbar_height = dp(28)
    _rounded_rectangle_height = dp(2)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.action_button._shift = self.action_button_offset_y
        self.action_button._scale_x = self.action_button_scale
        self.action_button._scale_y = self.action_button_scale
        Clock.schedule_once(lambda x: self.on_ready())

    def remove_notch(self):
        anim = Animation(d=0.0) + Animation(
            notch_radius=0,
            d=0.0,
        )
        anim.start(self)

    def set_notch(self):
        anim = Animation(d=0.0) + Animation(
            notch_radius=self.action_button_scale * (self.action_button.width / 2) + dp(4),
            d=0.0,
        )
        anim.start(self)

    def on_ready(self):
        self.action_button.x = self.action_button_offset_x + Window.width / 2 - self.action_button.width / 2
        self.action_button.y = self.action_button_offset_y + (
            (self.center[1] - self.height / 2)
            + self.theme_cls.standard_increment / 2
            + self._shift
        )
        self.minimum_height = 0
        self.maximum_height = self.toolbar_height
        self.size_hint_y = None
        self.height = self.toolbar_height
        self.ids.left_actions.size_hint_y = None
        self.ids.left_actions.height = self.toolbar_height
        self.ids.left_actions.padding = [0, 0, ]
        self.ids.right_actions.padding = [0, 0, ]
        self.ids.right_actions.size_hint_y = None
        self.ids.right_actions.height = self.toolbar_height
        self.ids.label_title.font_style = 'Subtitle2'

    def _on_resize(self, instance, width, height):
        self.minimum_height = 0
        self.maximum_height = self.toolbar_height
        self.size_hint_y = None
        self.height = self.toolbar_height
        if self.mode == "center":
            self.action_button.x = self.action_button_offset_x + width / 2 - self.action_button.width / 2
        else:
            self.action_button.x = self.action_button_offset_x + width - self.action_button.width * 2
        self.action_button.y = self.action_button_offset_y + (
            (self.center[1] - self.height / 2)
            + self.theme_cls.standard_increment / 2
            + self._shift
        )

    def on_mode(self, instance, value):

        def set_button_pos(*args):
            self.action_button.x = x
            self.action_button.y = y - self._rounded_rectangle_height / 2
            self.action_button._hard_shadow_size = (0, 0)
            self.action_button._soft_shadow_size = (0, 0)
            anim = Animation(_scale_x=self.action_button_scale, _scale_y=self.action_button_scale, d=0.0)
            anim.bind(on_complete=self.set_shadow)
            anim.start(self.action_button)

        if value == "center":
            self.set_notch()
            x = self.action_button_offset_x + Window.width / 2 - self.action_button.width / 2
            y = self.action_button_offset_y + (
                (self.center[1] - self.height / 2)
                + self.theme_cls.standard_increment / 2
                + self._shift
            )
        elif value == "end":
            self.set_notch()
            x = self.action_button_offset_x + Window.width - self.action_button.width * 2
            y = self.action_button_offset_y + (
                (self.center[1] - self.height / 2)
                + self.theme_cls.standard_increment / 2
                + self._shift
            )
            self.right_action_items = []
        elif value == "free-end":
            self.remove_notch()
            x = self.action_button_offset_x + Window.width - self.action_button.width - dp(10)
            y = self.action_button_offset_y + self.action_button.height + self.action_button.height / 2
        elif value == "free-center":
            self.remove_notch()
            x = self.action_button_offset_x + Window.width / 2 - self.action_button.width / 2
            y = self.action_button_offset_y + self.action_button.height + self.action_button.height / 2
        self.remove_shadow()
        anim = Animation(_scale_x=self.action_button_scale, _scale_y=self.action_button_scale, d=0.0)
        anim.bind(on_complete=set_button_pos)
        anim.start(self.action_button)
