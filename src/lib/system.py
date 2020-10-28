from kivy.utils import platform

def is_android():
    return platform == 'android'


def is_ios():
    return platform == 'ios'
