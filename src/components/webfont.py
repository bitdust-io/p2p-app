from fonts.fontawesome_map import fontawesome_codes, fontawesome_ttf_filepath

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------
# Font Awesome
# https://fontawesome.com/cheatsheet

def fa_icon(name, font_file=None, with_spaces=True):
    if name not in fontawesome_codes:
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

def md_icon(name, font_file=None, with_spaces=False):
    from kivymd.icon_definitions import md_icons
    if _Debug:
        print('md_icon', name, name in md_icons)
    s = '[font=Icons]{}[/font]'.format(md_icons[name])
    if not with_spaces:
        return s
    return ' {} '.format(s)
