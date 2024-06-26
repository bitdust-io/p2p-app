
_Debug = False

#------------------------------------------------------------------------------

KV_IMPORT = """
#:import root_path components.all_components.root_path

#:import NoTransition kivy.uix.screenmanager.NoTransition
#:import SlideTransition kivy.uix.screenmanager.SlideTransition

#:import images_path kivymd.images_path

#:import fa_icon components.webfont.fa_icon
#:import md_icon components.webfont.md_icon
#:import icofont_icon components.webfont.icofont_icon
#:import make_icon components.webfont.make_icon

#:import font_path fonts.all_fonts.font_path

#:import get_user_color lib.colorhash.get_user_color

#:import CustomContentNavigationDrawer components.main_win.CustomContentNavigationDrawer
#:import DynamicHeightTextInput components.text_input.DynamicHeightTextInput
#:import RaisedIconButton components.buttons.RaisedIconButton
#:import DropDownMenu components.drop_down_menu.DropDownMenu
#:import AutomatStatusPanel components.status_panel.AutomatStatusPanel
#:import AutomatShortStatusPanel components.status_panel.AutomatShortStatusPanel
#:import AutomatShortStatusPanelByIndex components.status_panel.AutomatShortStatusPanelByIndex
#:import CustomFloatingActionButton components.tool_bar.CustomFloatingActionButton
#:import CustomBottomAppBar components.tool_bar.CustomBottomAppBar
#:import CustomBottomToolbar components.tool_bar.CustomBottomToolbar
#:import CustomTopToolbar components.tool_bar.CustomTopToolbar
#:import CustomSelectionList components.selection.CustomSelectionList
#:import CustomIconLeftWidget components.buttons.CustomIconLeftWidget
#:import CustomIconPackLeftWidget components.buttons.CustomIconPackLeftWidget
#:import CustomActionTopAppBarIconButton components.buttons.CustomActionTopAppBarIconButton
#:import PrivateDistributedFileSystem components.file_browser.PrivateDistributedFileSystem
#:import SharedDistributedFileSystem components.file_browser.SharedDistributedFileSystem
#:import DistributedFileListEntry components.file_browser.DistributedFileListEntry
#:import DistributedFileChooserListView components.file_browser.DistributedFileChooserListView
#:import DistributedFileChooserListLayout components.file_browser.DistributedFileChooserListLayout
#:import CircularProgressBar components.spinner.CircularProgressBar
"""


KV_FILES = [
    'components/layouts.kv',
    'components/labels.kv',
    'components/buttons.kv',
    'components/text_input.kv',
    'components/list_view.kv',
    'components/status_panel.kv',
    'components/tool_bar.kv',
    'components/drop_down_menu.kv',
    'components/dialogs.kv',
    'components/selection.kv',
    'components/main_win.kv',
    'components/file_browser.kv',
]


ROOT_APP_PATH = '.'


def root_path(sub_dir=None, filename=None):
    global ROOT_APP_PATH
    import os
    if sub_dir:
        if filename:
            ret = os.path.join(ROOT_APP_PATH, sub_dir, filename)
            if _Debug:
                print('all_components.root_path', ret)
            return ret
        ret = os.path.join(ROOT_APP_PATH, sub_dir)
        if _Debug:
            print('all_components.root_path', ret)
        return ret
    if filename:
        ret = os.path.join(ROOT_APP_PATH, filename)
        if _Debug:
            print('all_components.root_path', ret)
        return ret
    ret = ROOT_APP_PATH
    if _Debug:
        print('all_components.root_path', ret)
    return ret
