
KV_IMPORT = """
#:import fa_icon components.webfont.fa_icon
#:import md_icon components.webfont.md_icon
#:import icofont_icon components.webfont.icofont_icon
#:import make_icon components.webfont.make_icon

#:import font_path fonts.all_fonts.font_path

#:import get_user_color lib.colorhash.get_user_color

#:import DynamicHeightTextInput components.text_input.DynamicHeightTextInput
#:import RaisedIconButton components.buttons.RaisedIconButton
#:import DropDownMenu components.drop_down_menu.DropDownMenu
#:import AutomatStatusPanel components.status_panel.AutomatStatusPanel
#:import AutomatShortStatusPanel components.status_panel.AutomatShortStatusPanel
#:import AutomatShortStatusPanelByIndex components.status_panel.AutomatShortStatusPanelByIndex
#:import CustomActionBottomAppBarButton components.tool_bar.CustomActionBottomAppBarButton
#:import CustomBottomAppBar components.tool_bar.CustomBottomAppBar
#:import CustomBottomToolbar components.tool_bar.CustomBottomToolbar
#:import CustomSelectionList components.selection.CustomSelectionList
#:import CustomIconLeftWidget components.buttons.CustomIconLeftWidget
"""


KV_FILES = [
    './components/layouts.kv',
    './components/labels.kv',
    './components/buttons.kv',
    './components/text_input.kv',
    './components/list_view.kv',
    './components/status_panel.kv',
    './components/tool_bar.kv',
    './components/drop_down_menu.kv',
    './components/dialogs.kv',
    './components/selection.kv',
    './components/main_win.kv',
]