import os

jetbrains_ttf_filepath = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'JetBrains', 'JetBrainsMono-Regular.ttf')

from kivy.utils import platform
if platform == 'android':
    jetbrains_ttf_filepath = os.path.join(os.environ['ANDROID_ARGUMENT'], 'fonts', 'JetBrains', 'JetBrainsMono-Regular.ttf')
