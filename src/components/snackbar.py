from kivy.metrics import dp
from kivy.core.window import Window

from kivymd.uix.snackbar import Snackbar

from components import screen

#------------------------------------------------------------------------------

def success(text, duration=5, state_panel_height=32, bottom=True):
    y = 0
    if not bottom:
        y = Window.height - screen.toolbar().height - dp(state_panel_height) - dp(32)
    sb = Snackbar(
        pos_hint={'right': 1, },
        size_hint_x=1,
        height=dp(32),
        snackbar_x=0,
        snackbar_y=y,
        radius=[0, 0, 0, 0, ],
        elevation=0,
        padding=dp(10),
        snackbar_animation_dir='Right',
        bg_color=screen.my_app().theme_cls.accent_color,
        duration=duration,
        text=text,
    )
    sb.elevation = 0
    sb.ids.text_bar.halign = 'right'
    sb.open()


def error(text, duration=5, state_panel_height=32, bottom=True):
    y = 0
    if not bottom:
        y = Window.height - screen.toolbar().height - dp(state_panel_height) - dp(32)
    sb = Snackbar(
        pos_hint={'right': 1, },
        size_hint_x=1,
        height=dp(32),
        snackbar_x=0,
        snackbar_y=y,
        radius=[0, 0, 0, 0, ],
        elevation=0,
        padding=dp(10),
        snackbar_animation_dir='Right',
        bg_color=screen.my_app().theme_cls.error_color,
        duration=duration,
        text=text,
    )
    sb.elevation = 0
    sb.ids.text_bar.halign = 'right'
    sb.open()


def info(text, duration=5, state_panel_height=32, bottom=True):
    y = 0
    if not bottom:
        y = Window.height - screen.toolbar().height - dp(state_panel_height) - dp(32)
    sb = Snackbar(
        pos_hint={'right': 1, },
        size_hint_x=1,
        height=dp(32),
        snackbar_x=0,
        snackbar_y=y,
        radius=[0, 0, 0, 0, ],
        elevation=0,
        padding=dp(10),
        snackbar_animation_dir='Right',
        bg_color=screen.my_app().theme_cls.primary_light,
        duration=duration,
        text=text,
    )
    sb.elevation = 0
    sb.ids.text_bar.halign = 'right'
    sb.open()
