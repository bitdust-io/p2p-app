from kivy.metrics import dp, sp
from kivy.core.window import Window

from kivymd.uix.snackbar import Snackbar

from components import screen

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

def get_coordinates(text, height=32, padding=10, font_size=15, state_panel_height=32, bottom=False, align='right', fill=False):
    x = 0
    y = 0
    pos_hint = {'right': 1, }
    width = Window.width
    if not fill:
        width = len(text) * sp(font_size) * 0.61 + dp(padding * 2)
    size_hint_x = width / Window.width
    animation_dir = 'Top'
    if align == 'left':
        x = 0
        pos_hint = {'left': 0, }
        animation_dir = 'Left'
    elif align == 'center':
        x = Window.width / 2.0
        pos_hint = {'center_x': 0.5, }
        animation_dir = 'Left'
        if bottom:
            animation_dir = 'Bottom'
    elif align == 'right':
        x = 0
        pos_hint = {'right': 1, }
        animation_dir = 'Right'
    else:
        raise Exception('wrong alignment: %r' % align)
    if bottom:
        y = screen.footer_bar().height
    else:
        y = Window.height - screen.toolbar().height - dp(state_panel_height) - dp(height)
    if _Debug:
        print('snackbar.get_coordinates: %r at %r %r %r %r' % (text, x, y, width, size_hint_x, ))
    return x, y, size_hint_x, pos_hint, animation_dir

#------------------------------------------------------------------------------

def success(text, duration=5, height=32, padding=10, font_size=15, state_panel_height=32, bottom=True, align='right', fill=False, shorten=True):
    x, y, size_hint_x, pos_hint, animation_dir = get_coordinates(text, height, padding, font_size, state_panel_height, bottom, align, fill)
    sb = Snackbar(
        height=dp(height),
        snackbar_x=x,
        snackbar_y=y,
        pos_hint=pos_hint,
        size_hint_x=size_hint_x,
        padding=dp(padding),
        radius=[0, 0, 0, 0, ],
        elevation=0,
        snackbar_animation_dir=animation_dir,
        bg_color=screen.my_app().theme_cls.accent_color,
        duration=duration,
        text='[font=data/fonts/RobotoMono-Regular.ttf]{}[/font]'.format(text),
    )
    sb.elevation = 0
    sb.ids.text_bar.halign = align
    sb.ids.text_bar.shorten = shorten
    sb.open()


def error(text, duration=5, height=32, padding=10, font_size=15, state_panel_height=32, bottom=True, align='right', fill=False, shorten=True):
    x, y, size_hint_x, pos_hint, animation_dir = get_coordinates(text, height, padding, font_size, state_panel_height, bottom, align, fill)
    sb = Snackbar(
        height=dp(height),
        snackbar_x=x,
        snackbar_y=y,
        pos_hint=pos_hint,
        size_hint_x=size_hint_x,
        padding=dp(padding),
        radius=[0, 0, 0, 0, ],
        elevation=0,
        snackbar_animation_dir=animation_dir,
        bg_color=screen.my_app().theme_cls.error_color,
        duration=duration,
        text='[font=data/fonts/RobotoMono-Regular.ttf]{}[/font]'.format(text),
    )
    sb.elevation = 0
    sb.ids.text_bar.halign = align
    sb.ids.text_bar.shorten = shorten
    sb.open()


def info(text, duration=5, height=32, padding=10, font_size=15, state_panel_height=32, bottom=True, align='right', fill=False, shorten=True):
    x, y, size_hint_x, pos_hint, animation_dir = get_coordinates(text, height, padding, font_size, state_panel_height, bottom, align, fill)
    sb = Snackbar(
        height=dp(height),
        snackbar_x=x,
        snackbar_y=y,
        size_hint_x=size_hint_x,
        pos_hint=pos_hint,
        padding=dp(padding),
        radius=[0, 0, 0, 0, ],
        elevation=0,
        snackbar_animation_dir=animation_dir,
        bg_color=screen.my_app().theme_cls.primary_light,
        duration=duration,
        text='[font=data/fonts/RobotoMono-Regular.ttf]{}[/font]'.format(text),
    )
    sb.elevation = 0
    sb.ids.text_bar.halign = align
    sb.ids.text_bar.shorten = shorten
    sb.open()
