from kivy.metrics import dp
from kivy.core.window import Window

from kivymd.uix.snackbar import Snackbar

from components import screen

#------------------------------------------------------------------------------

def success(text, duration=5):
    Snackbar(
        text=text,
        bg_color=screen.my_app().theme_cls.accent_color,
        duration=duration,
        snackbar_x="10dp",
        snackbar_y="10dp",
        size_hint_x=(
            Window.width - (dp(10) * 2)
        ) / Window.width
    ).open()


def error(text, duration=5):
    Snackbar(
        text=text,
        bg_color=screen.my_app().theme_cls.error_color,
        duration=duration,
        snackbar_x="10dp",
        snackbar_y="10dp",
        size_hint_x=(
            Window.width - (dp(10) * 2)
        ) / Window.width
    ).open()
