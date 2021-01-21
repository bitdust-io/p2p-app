from fonts.fontawesome_map import fontawesome_codes, fontawesome_ttf_filepath
from fonts.icofont_map import icofont_codes, icofont_ttf_filepath
from fonts.materialdesignicons_map import materialdesignicons_codes, materialdesignicons_ttf_filepath
from fonts.materialdesignicons5455_map import materialdesignicons5455_codes, materialdesignicons5455_ttf_filepath

#------------------------------------------------------------------------------

_Debug = True

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
# Font Awesome
# https://fontawesome.com/cheatsheet

def is_icofont_icon(name):
    return name in icofont_codes


def icofont_icon(name, font_file=None, with_spaces=True):
    if name not in icofont_codes:
        if _Debug:
            print('icofont_icon', name, '???')
        return ''
    if font_file is None:
        font_file = icofont_ttf_filepath
    s = '[font={}]{}[/font]'.format(font_file, icofont_codes[name])
    if _Debug:
        print('icofont_icon', font_file, name)
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

#------------------------------------------------------------------------------

def is_md5455_icon(name):
    return name in materialdesignicons_codes


def md5455_icon(name, font_file=None, with_spaces=False):
    if not name:
        return ''
    if name not in materialdesignicons5455_codes:
        if _Debug:
            print('md5455_icon', name, '???')
        return ''
    if font_file is None:
        font_file = materialdesignicons5455_ttf_filepath
    s = '[font={}]{}[/font]'.format(font_file, materialdesignicons5455_codes[name])
    if _Debug:
        print('md5455_icon', font_file, name)
    if not with_spaces:
        return s
    return ' {} '.format(s)

#------------------------------------------------------------------------------

def make_icon(name, icon_pack='materialdesignicons', font_file=None, with_spaces=False):
    if icon_pack in ['md', 'materialdesignicons', ]:
        # return md_icon(name, font_file=font_file, with_spaces=with_spaces)
        return md5455_icon(name, font_file=font_file, with_spaces=with_spaces)
    if icon_pack in ['fa', 'fontawesome', ]:
        return fa_icon(name, font_file=font_file, with_spaces=with_spaces)
    if icon_pack in ['ico', 'icofont', ]:
        return icofont_icon(name, font_file=font_file, with_spaces=with_spaces)
    raise Exception('unknown icon pack: %r' % icon_pack)
