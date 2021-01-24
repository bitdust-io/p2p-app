from fonts.fontawesome_map import fontawesome_codes, fontawesome_ttf_filepath
from fonts.icofont_map import icofont_codes, icofont_ttf_filepath
from fonts.materialdesignicons_map import materialdesignicons_codes, materialdesignicons_ttf_filepath

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------
# Font Awesome
# https://fontawesome.com/cheatsheet

def is_fa_icon(name):
    return name in fontawesome_codes


def fa_icon(name, font_file=None, with_spaces=True, with_font_tag=True):
    if name not in fontawesome_codes:
        if _Debug:
            print('fa_icon', name, '???')
        return ''
    if font_file is None and with_font_tag:
        font_file = fontawesome_ttf_filepath
    s = ''
    if with_font_tag:
        s = '[font={}]{}[/font]'.format(font_file, fontawesome_codes[name])
    else:
        s = fontawesome_codes[name]
    if _Debug:
        print('fa_icon', font_file, name)
    if not with_spaces:
        return s
    return ' {} '.format(s)


#------------------------------------------------------------------------------

def is_icofont_icon(name):
    return name in icofont_codes


def icofont_icon(name, font_file=None, with_spaces=True, with_font_tag=True):
    if name not in icofont_codes:
        if _Debug:
            print('icofont_icon', name, '???')
        return ''
    if font_file is None and with_font_tag:
        font_file = icofont_ttf_filepath
    s = ''
    if with_font_tag:
        s = '[font={}]{}[/font]'.format(font_file, icofont_codes[name])
    else:
        s = icofont_codes[name]
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


def md_icon(name, font_file=None, with_spaces=False, with_font_tag=True):
    if not name:
        return ''
    if name not in materialdesignicons_codes:
        if _Debug:
            print('md_icon', name, '???')
        return ''
    if font_file is None and with_font_tag:
        font_file = materialdesignicons_ttf_filepath
    s = ''
    if with_font_tag:
        s = '[font={}]{}[/font]'.format(font_file, materialdesignicons_codes[name])
    else:
        s = materialdesignicons_codes[name]
    if _Debug:
        print('md_icon', font_file, name)
    if not with_spaces:
        return s
    return ' {} '.format(s)

#------------------------------------------------------------------------------

def get_icon_code(name, icon_pack='IconMD'):
    if icon_pack in ['md', 'materialdesignicons', 'IconMD', ]:
        return md_icon(name, font_file=None, with_spaces=False, with_font_tag=False)
    if icon_pack in ['fa', 'fontawesome', 'IconFA', ]:
        return fa_icon(name, font_file=None, with_spaces=False, with_font_tag=False)
    if icon_pack in ['ico', 'icofont', 'IconICO', ]:
        return icofont_icon(name, font_file=None, with_spaces=False, with_font_tag=False)
    raise Exception('unknown icon pack: %r' % icon_pack)


def make_icon(name, icon_pack='IconMD', font_file=None, with_spaces=False):
    if icon_pack in ['md', 'materialdesignicons', 'IconMD', ]:
        return md_icon(name, font_file=font_file, with_spaces=with_spaces)
    if icon_pack in ['fa', 'fontawesome', 'IconFA', ]:
        return fa_icon(name, font_file=font_file, with_spaces=with_spaces)
    if icon_pack in ['ico', 'icofont', 'IconICO', ]:
        return icofont_icon(name, font_file=font_file, with_spaces=with_spaces)
    raise Exception('unknown icon pack: %r' % icon_pack)
