from fonts.fontawesome_map import fontawesome_codes
from fonts.materialdesignicons_map import materialdesignicons_codes

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------
# Font Awesome
# https://fontawesome.com/cheatsheet

def fa_icon(name, font_file='fonts/fa-solid.ttf', with_spaces=True):
    if name not in fontawesome_codes:
        return ''
    s = '[font={}]{}[/font]'.format(font_file, fontawesome_codes[name])
    if _Debug:
        print('fa_icon', name)
    if not with_spaces:
        return s
    return ' {} '.format(s)

#------------------------------------------------------------------------------
# Material Design Icons
# https://materialdesignicons.com/

def md_icon(name, font_file='fonts/materialdesignicons-webfont.ttf', with_spaces=False):
    if name not in materialdesignicons_codes:
        return ''
    s = '[font={}]{}[/font]'.format(font_file, materialdesignicons_codes[name])
    if _Debug:
        print('md_icon', name)
    if not with_spaces:
        return s
    return ' {} '.format(s)
