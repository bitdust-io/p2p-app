from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivymd.theming import ThemableBehavior

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

def my_app():
    return App.get_running_app()


def main_window():
    return my_app().main_window


def toolbar():
    return main_window().ids.toolbar


def footer():
    return main_window().ids.footer


def footer_bar():
    return main_window().ids.footer_bar


def manager():
    return main_window().ids.screen_manager


def control():
    return my_app().control


def select_screen(screen_id, verify_state=False, screen_type=None, **kwargs):
    return main_window().select_screen(screen_id, verify_state=verify_state, screen_type=screen_type, **kwargs)


def close_screen(screen_id):
    return main_window().close_screen(screen_id)


def screen_back():
    return main_window().screen_back()


def stack_clear():
    main_window().screens_stack.clear()


def stack_append(screen_id):
    main_window().screens_stack.append(screen_id)


def model(model_name=None, snap_id=None):
    if model_name is None:
        return control().model_data
    if snap_id is not None:
        return control().model_data.get(model_name, {}).get(snap_id, None)
    if model_name == '*':
        return control().model_data.keys()
    return control().model_data.get(model_name, {})

#------------------------------------------------------------------------------

class AppScreen(ThemableBehavior, Screen):

    def __init__(self, **kw):
        kw = self.init_kwargs(**kw)
        kw.pop('id', None)
        super(AppScreen, self).__init__(**kw)

    def init_kwargs(self, **kw):
        return kw

    def get_icon(self):
        return ''

    def get_icon_pack(self):
        return 'Icons'

    def get_title(self):
        return ''

    def get_hot_button(self):
        return None

    def get_statuses(self):
        return {}

    def app(self):
        return my_app()

    def main_win(self):
        return main_window()

    def scr_manager(self):
        return manager()

    def control(self):
        return control()

    def model(self, model_name=None, snap_id=None):
        return model(model_name=model_name, snap_id=snap_id)

    def open_drop_down_menu(self):
        dd_menu = self.ids.get('drop_down_menu')
        if dd_menu:
            dd_menu.open_stack()

    def close_drop_down_menu(self):
        dd_menu = self.ids.get('drop_down_menu')
        if dd_menu:
            dd_menu.close_stack()

    def on_opened(self):
        pass

    def on_closed(self):
        pass

    def on_created(self):
        pass

    def on_destroying(self):
        pass

    def on_nav_button_clicked(self):
        pass

    def on_dropdown_menu_item_clicked(self, menu_inst, item_inst):
        pass

    def on_action_button_clicked(self):
        pass

    def on_hot_button_clicked(self):
        pass
