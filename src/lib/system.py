from kivy.utils import platform

#------------------------------------------------------------------------------

_LatestState = None

#------------------------------------------------------------------------------

def latest_state():
    global _LatestState
    if _LatestState:
        return _LatestState
    _LatestState = str('' + platform)
    return _LatestState

#------------------------------------------------------------------------------

def is_windows():
    return latest_state() == 'win'


def is_android():
    return latest_state() == 'android'


def is_ios():
    return latest_state() == 'ios'
