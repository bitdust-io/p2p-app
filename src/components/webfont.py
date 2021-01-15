from fonts.fontawesome_map import fontawesome_codes, fontawesome_ttf_filepath
from fonts.materialdesignicons_map import materialdesignicons_codes, materialdesignicons_ttf_filepath

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------
# Font Awesome
# https://fontawesome.com/cheatsheet

def is_fa_icon(name):
    return name in fontawesome_codes


def fa_icon(name, font_file=None, with_spaces=True):
    if name not in fontawesome_codes:
        if _Debug:
            print('fa_icon', name, '???')
        return ''
    if font_file is None:
        font_file = fontawesome_ttf_filepath
    s = '[font={}]{}[/font]'.format(font_file, fontawesome_codes[name])
    if _Debug:
        print('fa_icon', font_file, name)
    if not with_spaces:
        return s
    return ' {} '.format(s)

#------------------------------------------------------------------------------
# Material Design Icons
# https://materialdesignicons.com/

def is_md_icon(name):
    return name in materialdesignicons_codes


def md_icon(name, font_file=None, with_spaces=False):
    if not name:
        return ''
    if name not in materialdesignicons_codes:
        if _Debug:
            print('md_icon', name, '???')
        return ''
    if font_file is None:
        font_file = materialdesignicons_ttf_filepath
    s = '[font={}]{}[/font]'.format(font_file, materialdesignicons_codes[name])
    if _Debug:
        print('md_icon', font_file, name)
    if not with_spaces:
        return s
    return ' {} '.format(s)
