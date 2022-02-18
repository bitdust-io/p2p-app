import os
from kivy.utils import platform


def font_path(ttf_filename):
    if platform == 'android':
        return os.path.join(os.environ['ANDROID_ARGUMENT'], 'fonts', ttf_filename)
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), ttf_filename)
